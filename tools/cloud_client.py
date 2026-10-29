#!/usr/bin/env python3
"""The cloud (Linux) client: downloads the Minecraft 26.3 client from Mojang into server/mc/ in the launcher layout
(versions/26.3/26.3.{jar,json}, libraries/, assets/indexes + objects without the sounds) so tools/client_launch.py
and tools/build_shotagent.sh work without the macOS launcher. The clients render with Mesa (software) on a virtual
display: tools/client_launch.py starts Xvfb on :99 by itself when there is no DISPLAY.
Usage: python3 tools/cloud_client.py          (idempotent; files already there are skipped)"""
import concurrent.futures as cf, hashlib, json, os, sys, urllib.error, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MC = os.path.join(ROOT, "server/mc"); VER = "26.3"
import time
def get(url, tries=1):
    for i in range(tries):
        try: return urllib.request.urlopen(url, timeout=120).read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == tries - 1: raise
            time.sleep(2 + 2 * i)            # Maven Central rate limit
SRV_LIBS = os.path.join(ROOT, "server/libraries")      # the server jar unpacks the libraries it shares with the client
MISSING = []
def fetch(url, path, sha=None):
    if os.path.exists(path) and (sha is None or hashlib.sha1(open(path, "rb").read()).hexdigest() == sha): return 0
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rel = path.split("/libraries/", 1)[1] if "/libraries/" in path else None
    if rel and os.path.exists(os.path.join(SRV_LIBS, rel)): data = open(os.path.join(SRV_LIBS, rel), "rb").read()
    else:
        # the cloud proxy lets Mojang's piston hosts through but not libraries/resources: Maven Central has the open-source ones,
        # the few Mojang-only libraries get stubs (tools/cloud_stubs/), the assets (sounds, other languages) are not needed
        try: data = get(url)
        except Exception:
            if not rel: MISSING.append(url); return 0
            try: data = get("https://repo1.maven.org/maven2/" + rel, 6)
            except Exception: MISSING.append(rel); return 0
    if sha and hashlib.sha1(data).hexdigest() != sha: raise SystemExit("bad sha1: " + url)
    open(path + ".part", "wb").write(data); os.replace(path + ".part", path); return len(data)
man = json.loads(get("https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"))
vurl = [v["url"] for v in man["versions"] if v["id"] == VER][0]
vd = os.path.join(MC, "versions", VER); fetch(vurl, os.path.join(vd, VER + ".json")); d = json.load(open(os.path.join(vd, VER + ".json")))
fetch(d["downloads"]["client"]["url"], os.path.join(vd, VER + ".jar"), d["downloads"]["client"]["sha1"])
jobs = []
for l in d["libraries"]:
    a = l.get("downloads", {}).get("artifact")
    if not a or any(r.get("os", {}).get("name") not in (None, "linux") for r in l.get("rules", [])): continue
    rel = a.get("path") or a["url"].split("://", 1)[1].split("/", 1)[1]
    jobs.append((a["url"], os.path.join(MC, "libraries", rel), a["sha1"]))
ai = d["assetIndex"]; ip = os.path.join(MC, "assets/indexes", ai["id"] + ".json"); fetch(ai["url"], ip, ai["sha1"])
for name, o in json.load(open(ip))["objects"].items():
    if name.endswith(".ogg"): continue           # no sound card in the cloud: the sounds are not needed
    h = o["hash"]; jobs.append(("https://resources.download.minecraft.net/%s/%s" % (h[:2], h), os.path.join(MC, "assets/objects", h[:2], h), h))
with cf.ThreadPoolExecutor(4) as ex: total = sum(ex.map(lambda j: fetch(*j), jobs))
if MISSING: print("not downloaded (%d): " % len(MISSING) + ", ".join(m for m in MISSING if "/objects/" not in m)[:2000])
print("server/mc ready: %d files, %.1f MB downloaded" % (len(jobs) + 2, total / 1e6))

# the Mojang-only libraries the proxy does not let through: stubs compiled from tools/cloud_stubs/ (patchy and the tracy natives are not used)
import glob, subprocess, tempfile, zipfile
jh = subprocess.run(["bash", "-c", ". '%s/tools/env.sh'; le_java_home" % ROOT], capture_output=True, text=True).stdout.strip()
for pkg, rel in (("text2speech", "com/mojang/text2speech/1.19.12/text2speech-1.19.12.jar"), ("blocklist", "com/mojang/blocklist/1.0.10/blocklist-1.0.10.jar"),
                 ("patchy", "com/mojang/patchy/2.2.10/patchy-2.2.10.jar")):
    out = os.path.join(MC, "libraries", rel)
    if os.path.exists(out): continue
    os.makedirs(os.path.dirname(out), exist_ok=True); src = glob.glob(os.path.join(ROOT, "tools/cloud_stubs/com/mojang", pkg, "*.java"))
    with tempfile.TemporaryDirectory() as t:
        if src: subprocess.run([jh + "/bin/javac", "-d", t] + src, check=True)
        with zipfile.ZipFile(out, "w") as z:
            for f in glob.glob(t + "/**/*.class", recursive=True): z.write(f, os.path.relpath(f, t))
    print("stub", rel)

# the assets the proxy does not let through: placeholders under the hash names the index expects (the client does not check them)
import io, struct, zlib
def tiny_png(c=(20, 18, 18)):
    raw = b"".join(b"\x00" + bytes(c) * 4 for _ in range(4))
    ch = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", 4, 4, 8, 2, 0, 0, 0)) + ch(b"IDAT", zlib.compress(raw)) + ch(b"IEND", b"")
def pack_zip(desc):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z: z.writestr("pack.mcmeta", json.dumps({"pack": {"description": desc, "min_format": 97, "max_format": 97}}))
    return b.getvalue()
made = 0
for name, o in json.load(open(ip))["objects"].items():
    if name.endswith(".ogg"): continue
    p = os.path.join(MC, "assets/objects", o["hash"][:2], o["hash"])
    if os.path.exists(p): continue
    if name == "pack.mcmeta": data = json.dumps({"pack": {"description": "Minecraft resources", "min_format": 97, "max_format": 97}}).encode()
    elif name.endswith(".png"): data = tiny_png()
    elif name.endswith("sounds.json") or name.endswith("/lang/en_us.json") or "/lang/" in name: data = b"{}"
    elif name.endswith("unifont.json") or name.endswith("unifont_pua.json"): data = b'{"providers":[]}'
    elif "/resourcepacks/" in name: data = pack_zip(name.rsplit("/", 1)[1][:-4])
    elif name.endswith(".zip"): data = pack_zip("font")
    else: data = b""
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "wb").write(data); made += 1
if made: print("placeholder assets:", made)
