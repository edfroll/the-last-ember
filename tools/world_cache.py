#!/usr/bin/env python3
"""World cache: build the test world once per main commit, keep the archive in the repo branch `world-cache`, rebuild only what a task changed.

Two snapshots, both taken by tools/build/rebuild.sh with the server STOPPED (before the first start, so datapack state is pristine):
  gen    the generated natural world (pregen under `tick freeze`) + server/build/r1/nat.bin       key: seed, server jar, worldgen of the datapack, pregen area
  final  the built world before its first start + server/build/r1/*.bin/json/npz (inputs of the place steps) + `snap/<place>/`:
         the chunks (region, entities, poi) of each place's box as they were just before its step of tools/build/r1_apply.sh
         (taken by tools/terrain.sh when it scans `<place>_pre.bin` with LE_SNAPDIR set)
Branch `world-cache` = one orphan commit (overwritten on every push): manifest.json + gen.tar.gz.NN + final.tar.gz.NN (parts < 95 MB).

  python3 tools/world_cache.py status            what the cache holds, what changed in the world inputs since its commit, the mode to use
  python3 tools/world_cache.py fetch             download the branch into server/cache/ (checks sha256 of every archive)
  python3 tools/world_cache.py restore gen|final put a snapshot into server/world (+ server/build/r1); the server must be stopped
  python3 tools/world_cache.py redo [place…]     restore final, put back the pre-step chunks of each place, re-run its step of r1_apply.sh,
                                                 then the tail (biomepaint, borders, sync). A place new since the cache is just run.
                                                 Without places: the ones `status` names.
  python3 tools/world_cache.py save gen|final    (rebuild.sh) pack the current world into server/cache/<name>.tar.gz + manifest
  python3 tools/world_cache.py push              upload server/cache/ to the branch (only from a commit that is in origin/main or
                                                 descends from the cached commit; refuses to overwrite a newer cache)
Modes `status` prints: final (nothing in the world inputs changed: use the archive as is), redo <places> (only these places changed),
gen (the frame, Refuge, tools or biomes changed: rebuild.sh --cache = everything after pregen), scratch (seed/jar/worldgen/pregen changed)."""
import hashlib, json, os, re, shutil, struct, subprocess, sys, tarfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRV = os.path.join(ROOT, "server"); WORLD = os.path.join(SRV, "world"); CACHE = os.path.join(SRV, "cache"); R1 = os.path.join(SRV, "build/r1")
BRANCH = "world-cache"; PART = 95 * 1024 * 1024
DIMS = ("region", "entities", "poi")
OW = "dimensions/minecraft/overworld"
# what makes the world before its first start (everything else -- datapack functions, resource pack, tests, docs -- acts at runtime)
WORLD_INPUTS = ("tools/build/", "tools/seedmap/", "tools/sculpt_specs/", "tools/terrain.sh", "tools/blockwriter.sh", "tools/biomepaint.sh",
                "tools/borders.sh", "tools/sculpt.sh", "tools/env.sh", "tools/gen_biomes.py", "tools/gen_bonfires.py", "tools/gen_gates.py",
                "biomes/", "bonfires/bonfires.txt", "gates/gates.txt", "datapack/data/minecraft/worldgen/", "datapack/data/last_ember/worldgen/")
NOT_WORLD = re.compile(r"tools/build/(.*_(routes|shots|walk)\.(py|sh)|r1_(check|render|routes|shots|walk|perf|gates_test|bonfires_test)\.(py|sh)|walkcheck\.py|routes\.py)$")
GEN_INPUTS = ("datapack/data/minecraft/worldgen/", "datapack/data/last_ember/worldgen/", "tools/build/pregen.py")


def sh(*a, **kw):
    return subprocess.run(a, cwd=ROOT, check=kw.pop("check", True), capture_output=True, text=True, **kw).stdout.strip()


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def gen_key():
    """hash of what the generated natural world depends on (working tree, so an uncommitted change counts)"""
    h = hashlib.sha1()
    h.update(open(os.path.join(SRV, "server.properties")).read().split("level-seed=")[1].split("\n")[0].encode())
    h.update(sha256(os.path.join(SRV, "server-26.3.jar")).encode())
    h.update("".join(l for l in open(os.path.join(ROOT, "tools/build/rebuild.sh")) if "pregen.py" in l and not l.startswith("#")).encode())
    for top in GEN_INPUTS:
        p = os.path.join(ROOT, top)
        files = [p] if os.path.isfile(p) else sorted(os.path.join(d, f) for d, _, fs in os.walk(p) for f in fs)
        for f in files: h.update(os.path.relpath(f, ROOT).encode()); h.update(open(f, "rb").read())
    return h.hexdigest()


# ---------------------------------------------------------------- chunk snapshots (anvil files: 4 KiB sectors, header of 1024 offsets)
def _read_header(data):
    return [struct.unpack_from(">I", data, i * 4)[0] for i in range(1024)] if len(data) >= 8192 else [0] * 1024


def chunks_of_box(x1, z1, x2, z2):
    return [(cx, cz) for cx in range(x1 >> 4, (x2 >> 4) + 1) for cz in range(z1 >> 4, (z2 >> 4) + 1)]


def snap_save(world, box, out):
    """copy the raw stored chunks (compressed as they are) of the box into out/<dim>/<cx>_<cz>.bin (+ .mcc for external chunks)"""
    os.makedirs(out, exist_ok=True)
    json.dump({"box": box}, open(os.path.join(out, "box.json"), "w"))
    n = 0
    for dim in DIMS:
        os.makedirs(os.path.join(out, dim), exist_ok=True)
        cache = {}
        for cx, cz in chunks_of_box(*box):
            rf = os.path.join(world, OW, dim, "r.%d.%d.mca" % (cx >> 5, cz >> 5))
            if rf not in cache: cache[rf] = open(rf, "rb").read() if os.path.exists(rf) else b""
            data = cache[rf]; hdr = _read_header(data); off = hdr[(cx & 31) + (cz & 31) * 32]
            if not off: continue
            sec = off >> 8; length = struct.unpack_from(">I", data, sec * 4096)[0]
            open(os.path.join(out, dim, "%d_%d.bin" % (cx, cz)), "wb").write(data[sec * 4096: sec * 4096 + 4 + length])
            if data[sec * 4096 + 4] & 128:   # oversized chunk kept in c.<x>.<z>.mcc next to the region file
                shutil.copy(os.path.join(os.path.dirname(rf), "c.%d.%d.mcc" % (cx, cz)), os.path.join(out, dim, "%d_%d.mcc" % (cx, cz)))
            n += 1
    return n


def snap_restore(world, snap):
    """put the snapshot's chunks back (appended to the region file, header pointed at them); chunks of the box missing in the snapshot
    are removed. Stale sectors stay in the file as free space (the game compacts nothing, it just reuses)."""
    box = json.load(open(os.path.join(snap, "box.json")))["box"]; n = 0
    for dim in DIMS:
        byreg = {}
        for cx, cz in chunks_of_box(*box): byreg.setdefault((cx >> 5, cz >> 5), []).append((cx, cz))
        for (rx, rz), cks in byreg.items():
            rf = os.path.join(world, OW, dim, "r.%d.%d.mca" % (rx, rz))
            data = bytearray(open(rf, "rb").read()) if os.path.exists(rf) else bytearray()
            if len(data) < 8192: data = bytearray(8192)
            changed = False
            for cx, cz in cks:
                i = (cx & 31) + (cz & 31) * 32
                src = os.path.join(snap, dim, "%d_%d.bin" % (cx, cz))
                mcc = os.path.join(os.path.dirname(rf), "c.%d.%d.mcc" % (cx, cz))
                if os.path.exists(mcc): os.remove(mcc)
                if not os.path.exists(src):
                    if struct.unpack_from(">I", data, i * 4)[0]: struct.pack_into(">I", data, i * 4, 0); changed = True
                    continue
                blob = open(src, "rb").read()
                if os.path.exists(src[:-4] + ".mcc"): shutil.copy(src[:-4] + ".mcc", mcc)
                if len(data) % 4096: data.extend(b"\0" * (4096 - len(data) % 4096))
                sec = len(data) // 4096; cnt = (len(blob) + 4095) // 4096
                data.extend(blob); data.extend(b"\0" * (cnt * 4096 - len(blob)))
                struct.pack_into(">I", data, i * 4, (sec << 8) | cnt)
                struct.pack_into(">I", data, 4096 + i * 4, int(time.time()))
                changed = True; n += 1
            if changed:
                os.makedirs(os.path.dirname(rf), exist_ok=True); open(rf, "wb").write(bytes(data))
    return n


# ---------------------------------------------------------------- r1_apply.sh sections
def apply_sections(text=None):
    """{'frame': lines, '<place>': lines, 'tail': lines} of tools/build/r1_apply.sh: a place's section starts at its `# T-0NN:` comment,
    it is named by the `<place>_pre.bin` it scans; the tail starts at tools/biomepaint.sh"""
    if text is None: text = open(os.path.join(ROOT, "tools/build/r1_apply.sh")).read()
    secs = {}; cur = "head"; buf = []
    def close():
        if not buf: return
        name = cur
        if cur == "place":
            m = re.search(r"/(\w+)_pre\.bin", "".join(buf)); name = m.group(1) if m else "place%d" % len(secs)
        secs[name] = list(buf)
    for line in text.splitlines(keepends=True):
        if re.match(r"# T-0\d\d", line) and cur in ("frame", "place"):
            close(); cur = "place"; buf.clear()
        elif line.startswith("tools/biomepaint.sh") and cur != "tail":
            close(); cur = "tail"; buf.clear()
        elif cur == "head" and line.startswith("python3 tools/build/r1.py"):
            close(); cur = "frame"; buf.clear()
        buf.append(line)
    close()
    return secs


def run_lines(lines, log):
    script = "set -euo pipefail\ncd %s\n%s" % (ROOT, "".join(l for l in lines if not l.startswith(("set -", "cd "))))
    with open(log, "a") as f:
        r = subprocess.run(["bash", "-c", script], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT)
    if r.returncode: sys.exit("step failed (exit %d), see %s" % (r.returncode, log))


# ---------------------------------------------------------------- archives
def manifest_path(): return os.path.join(CACHE, "manifest.json")


def load_manifest(path=None):
    p = path or manifest_path()
    return json.load(open(p)) if os.path.exists(p) else {}


def save(name):
    os.makedirs(CACHE, exist_ok=True)
    if subprocess.run(["pgrep", "-f", "server-26.3.jar"], capture_output=True).returncode == 0: sys.exit("stop the server first")
    out = os.path.join(CACHE, name + ".tar.gz"); tmp = out + ".tmp"
    with tarfile.open(tmp, "w:gz", compresslevel=1) as t:
        for top in ("level.dat", "data", "players", "dimensions"):
            p = os.path.join(WORLD, top)
            if os.path.exists(p): t.add(p, arcname="world/" + top)
        if name == "gen":
            t.add(os.path.join(R1, "nat.bin"), arcname="r1/nat.bin")
        else:
            for f in sorted(os.listdir(R1)):
                if f.endswith((".bin", ".json", ".npz", ".txt")): t.add(os.path.join(R1, f), arcname="r1/" + f)
            snaps = os.path.join(CACHE, "snap")
            if os.path.isdir(snaps): t.add(snaps, arcname="snap")
    os.replace(tmp, out)
    m = load_manifest()
    head = sh("git", "rev-parse", "HEAD"); dirty = bool(sh("git", "status", "--porcelain", "--", *WORLD_INPUTS, "tools/build/r1_apply.sh"))
    m[name] = {"commit": head, "dirty": dirty, "made": time.strftime("%Y-%m-%d %H:%M:%S"), "sha256": sha256(out), "size": os.path.getsize(out)}
    if name == "gen": m["gen"]["key"] = gen_key()
    else:
        m["final"]["gen_key"] = gen_key(); m["final"]["sections"] = {k: hashlib.sha1("".join(v).encode()).hexdigest() for k, v in apply_sections().items()}
    json.dump(m, open(manifest_path(), "w"), indent=1)
    print("saved %s: %.1f MB, commit %s%s" % (out, os.path.getsize(out) / 1e6, head[:10], " (uncommitted world inputs!)" if dirty else ""))


def restore(name):
    if subprocess.run(["pgrep", "-f", "server-26.3.jar"], capture_output=True).returncode == 0: sys.exit("stop the server first")
    m = load_manifest(); arc = os.path.join(CACHE, name + ".tar.gz")
    if name not in m or not os.path.exists(arc): sys.exit("no %s snapshot in server/cache: python3 tools/world_cache.py fetch" % name)
    if sha256(arc) != m[name]["sha256"]: sys.exit("%s: sha256 does not match the manifest" % arc)
    for top in ("level.dat", "level.dat_old", "data", "players", "dimensions", "session.lock"):
        p = os.path.join(WORLD, top)
        if os.path.isdir(p): shutil.rmtree(p)
        elif os.path.exists(p): os.remove(p)
    if name == "final": shutil.rmtree(os.path.join(CACHE, "snap"), ignore_errors=True)
    os.makedirs(R1, exist_ok=True)
    with tarfile.open(arc) as t:
        for mem in t.getmembers():
            if mem.name.startswith("world/"): mem.name = mem.name[6:]; t.extract(mem, WORLD, filter="data")
            elif mem.name.startswith("r1/"): mem.name = mem.name[3:]; t.extract(mem, R1, filter="data")
            elif mem.name.startswith("snap"): t.extract(mem, CACHE, filter="data")
    os.makedirs(os.path.join(WORLD, "datapacks"), exist_ok=True)   # the datapack of this checkout (offline tools read its biomes)
    subprocess.run(["rsync", "-a", "--delete", os.path.join(ROOT, "datapack") + "/", os.path.join(WORLD, "datapacks/last_ember") + "/"], check=True)
    print("restored %s (commit %s, made %s)" % (name, m[name]["commit"][:10], m[name]["made"]))


def fetch():
    os.makedirs(CACHE, exist_ok=True)
    r = subprocess.run(["git", "fetch", "--depth", "1", "origin", "+refs/heads/%s:refs/remotes/origin/%s" % (BRANCH, BRANCH)], cwd=ROOT, capture_output=True, text=True)
    if r.returncode: sys.exit("no branch %s on origin yet (%s)" % (BRANCH, r.stderr.strip()[-200:]))
    ref = "origin/" + BRANCH
    m = json.loads(sh("git", "show", ref + ":manifest.json"))
    for name in ("gen", "final"):
        if name not in m: continue
        out = os.path.join(CACHE, name + ".tar.gz")
        if os.path.exists(out) and sha256(out) == m[name]["sha256"]: continue
        with open(out + ".tmp", "wb") as f:
            for part in m[name]["parts"]:
                f.write(subprocess.run(["git", "show", "%s:%s" % (ref, part)], cwd=ROOT, capture_output=True, check=True).stdout)
        if sha256(out + ".tmp") != m[name]["sha256"]: sys.exit("%s: sha256 mismatch after download" % name)
        os.replace(out + ".tmp", out)
    json.dump(m, open(manifest_path(), "w"), indent=1)
    print("fetched: " + ", ".join("%s %s (%.0f MB)" % (n, m[n]["commit"][:10], m[n]["size"] / 1e6) for n in ("gen", "final") if n in m))


def push():
    m = load_manifest()
    for name in ("gen", "final"):
        if name not in m: sys.exit("nothing to push: no %s snapshot (tools/build/rebuild.sh makes both)" % name)
        if m[name].get("dirty"): sys.exit("%s was built with uncommitted world inputs: commit, rebuild, push" % name)
    commit = m["final"]["commit"]
    sh("git", "fetch", "origin", "main")
    if subprocess.run(["git", "merge-base", "--is-ancestor", commit, "origin/main"], cwd=ROOT).returncode:
        sys.exit("final was built from %s, which is not in origin/main: the cache holds only worlds of main" % commit[:10])
    old = subprocess.run(["git", "ls-remote", "origin", "refs/heads/" + BRANCH], cwd=ROOT, capture_output=True, text=True).stdout.split()
    lease = old[0] if old else ""
    if lease:
        sh("git", "fetch", "--depth", "1", "origin", "+refs/heads/%s:refs/remotes/origin/%s" % (BRANCH, BRANCH))
        prev = json.loads(sh("git", "show", "origin/%s:manifest.json" % BRANCH))["final"]["commit"]
        if prev != commit and subprocess.run(["git", "merge-base", "--is-ancestor", prev, commit], cwd=ROOT).returncode:
            sys.exit("the cache on origin (%s) is not older than this world (%s): not overwriting" % (prev[:10], commit[:10]))
    entries = []
    for name in ("gen", "final"):
        arc = os.path.join(CACHE, name + ".tar.gz"); parts = []
        with open(arc, "rb") as f:
            k = 0
            while True:
                b = f.read(PART)
                if not b: break
                pname = "%s.tar.gz.%02d" % (name, k); k += 1
                blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=ROOT, input=b, capture_output=True, check=True).stdout.decode().strip()
                entries.append("100644 blob %s\t%s" % (blob, pname)); parts.append(pname)
        m[name]["parts"] = parts
    mj = json.dumps(m, indent=1).encode()
    mb = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=ROOT, input=mj, capture_output=True, check=True).stdout.decode().strip()
    entries.append("100644 blob %s\tmanifest.json" % mb)
    tree = subprocess.run(["git", "mktree"], cwd=ROOT, input="\n".join(entries) + "\n", capture_output=True, text=True, check=True).stdout.strip()
    msg = "world cache for main %s (gen %s)" % (commit[:10], m["gen"]["commit"][:10])
    c = subprocess.run(["git", "commit-tree", tree, "-m", msg], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    args = ["git", "push", "--force-with-lease=refs/heads/%s:%s" % (BRANCH, lease), "origin", "%s:refs/heads/%s" % (c, BRANCH)]
    for attempt in range(4):
        r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
        if r.returncode == 0: break
        if "stale info" in r.stderr or "rejected" in r.stderr: sys.exit("push rejected (someone updated the cache): " + r.stderr[-300:])
        time.sleep(2 ** (attempt + 1))
    else: sys.exit("push failed: " + r.stderr[-300:])
    json.dump(m, open(manifest_path(), "w"), indent=1)
    print("pushed %s: %s" % (BRANCH, msg))


# ---------------------------------------------------------------- what to rebuild
def plan(m=None):
    """(mode, places, changed files)"""
    m = m or load_manifest()
    if "final" not in m: return "scratch", [], ["no cache (fetch first)"]
    base = m["final"]["commit"]
    if subprocess.run(["git", "cat-file", "-e", base + "^{commit}"], cwd=ROOT).returncode:
        sh("git", "fetch", "origin", "main", check=False)
    if gen_key() != m["final"].get("gen_key"):
        return ("gen" if "gen" in m and gen_key() == m["gen"].get("key") else "scratch"), [], ["generation inputs (seed, jar, worldgen, pregen)"]
    changed = [f for f in sh("git", "diff", "--name-only", base, "--", *WORLD_INPUTS, "tools/build/r1_apply.sh").splitlines()]
    changed += [l[3:] for l in sh("git", "status", "--porcelain", "--", *WORLD_INPUTS, "tools/build/r1_apply.sh").splitlines()]
    changed = sorted(set(f for f in changed if not NOT_WORLD.search(f)))
    secs = apply_sections(); old = m["final"].get("sections", {})
    places = [k for k in secs if k not in ("head", "frame", "tail")]
    redo = set(k for k in places if old.get(k) != hashlib.sha1("".join(secs[k]).encode()).hexdigest())
    if any(old.get(k) != hashlib.sha1("".join(secs[k]).encode()).hexdigest() for k in ("frame", "tail") if k in secs):
        return "gen", [], changed + ["r1_apply.sh: frame/tail lines"]
    rest = []
    for f in changed:
        if f == "tools/build/r1_apply.sh": continue
        b = os.path.basename(f)
        owner = [p for p in places if b.startswith(("r1_%s." % p, "%s_" % p, "%s." % p))]
        if owner: redo.update(owner)
        else: rest.append(f)
    if rest: return "gen", [], rest
    if redo: return "redo", [p for p in places if p in redo], changed
    return "final", [], changed


def status():
    m = load_manifest()
    for n in ("gen", "final"):
        if n in m: print("%-5s commit %s  made %s  %.0f MB%s" % (n, m[n]["commit"][:10], m[n]["made"], m[n]["size"] / 1e6, "  (dirty)" if m[n].get("dirty") else ""))
    mode, places, changed = plan(m)
    print("changed world inputs since the cache: %s" % (", ".join(changed) if changed else "none"))
    print("mode: %s%s" % (mode, (" " + " ".join(places)) if places else ""))
    print({"final": "  -> python3 tools/world_cache.py restore final, then start (nothing to rebuild)",
           "redo": "  -> python3 tools/world_cache.py redo " + " ".join(places),
           "gen": "  -> tools/build/rebuild.sh --cache   (everything after the generation of chunks)",
           "scratch": "  -> tools/build/rebuild.sh            (from scratch)"}[mode])


def redo(places):
    if not places:
        mode, places, _ = plan()
        if mode != "redo": sys.exit("status says %s, not redo" % mode)
    secs = apply_sections(); log = os.path.join(SRV, "debug/world_cache_redo.log"); os.makedirs(os.path.dirname(log), exist_ok=True)
    open(log, "w").close()
    for p in places:
        if p not in secs: sys.exit("no section %s in tools/build/r1_apply.sh (have: %s)" % (p, ", ".join(k for k in secs if k not in ("head", "frame", "tail"))))
    t0 = time.time(); restore("final")
    os.environ["LE_SNAPDIR"] = os.path.join(CACHE, "snap")
    for p in places:
        snap = os.path.join(CACHE, "snap", p)
        if os.path.isdir(snap): print("  %s: %d chunks put back" % (p, snap_restore(WORLD, snap)))
        else: print("  %s: new since the cache, its box is untouched in the archive" % p)
        print("  %s: step" % p); run_lines(secs[p], log)
    print("  tail (biomes, borders, sync)"); run_lines(secs["tail"], log)
    print("redo done in %d s (log %s); now start the server as rebuild.sh does: tools/build/rebuild.sh --start-only" % (time.time() - t0, log))


def main():
    a = sys.argv[1:]
    if not a: print(__doc__); return
    cmd = a[0]
    if cmd == "status": status()
    elif cmd == "fetch": fetch()
    elif cmd == "restore": restore(a[1])
    elif cmd == "save": save(a[1])
    elif cmd == "push": push()
    elif cmd == "redo": redo(a[1:])
    elif cmd == "snap": print("snap %s: %d chunks" % (a[6], snap_save(a[1], [int(v) for v in a[2:6]], a[6])))
    elif cmd == "unsnap": print("unsnap: %d chunks" % snap_restore(a[1], a[2]))
    elif cmd == "sections": print({k: len(v) for k, v in apply_sections().items()})
    elif cmd == "key": print(gen_key())
    else: print(__doc__); sys.exit(1)


if __name__ == "__main__":
    main()
