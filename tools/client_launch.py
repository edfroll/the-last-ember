#!/usr/bin/env python3
"""Launch the local Minecraft 26.3 client (from the TLauncher install) straight into the test server.
Usage: client_launch.py [--host localhost:25565] [--name Cam] [--size 1280x720]
Uses a dedicated game dir (server/client/) so the player's own options/saves are untouched; assets and libraries are read from
~/Library/Application Support/minecraft. Prints the PID; client log: server/client/logs/latest.log
"""
import argparse, glob, json, os, platform, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MC = os.path.expanduser("~/Library/Application Support/minecraft")
VER = "26.3"
OS_NAME, ARCH = "osx", platform.machine()

def rules_ok(rules):
    if not rules: return True
    ok = False
    for r in rules:
        m = True
        if "os" in r:
            o = r["os"]
            if "name" in o and o["name"] != OS_NAME: m = False
            if "arch" in o and o["arch"] != ("arm64" if ARCH == "arm64" else "x86"): m = False
        if "features" in r: m = False  # no optional features by default
        if m: ok = r["action"] == "allow"
    return ok

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="localhost:25565"); ap.add_argument("--name", default="Cam"); ap.add_argument("--size", default="1280x720")
    ap.add_argument("--dir", default="server/client", help="game dir (separate per extra client)"); ap.add_argument("--mem", default="3G")
    a = ap.parse_args()
    d = json.load(open(f"{MC}/versions/{VER}/{VER}.json"))
    cp = []
    for l in d["libraries"]:
        if not rules_ok(l.get("rules")): continue
        art = l.get("downloads", {}).get("artifact")
        if art:
            rel = art.get("path") or art["url"].split("://", 1)[1].split("/", 1)[1]  # 26.x manifests omit "path"
            p = f"{MC}/libraries/{rel}"
            if os.path.exists(p): cp.append(p)
            else: print("missing lib", p, file=sys.stderr)
    cp.append(f"{MC}/versions/{VER}/{VER}.jar")
    game_dir = os.path.join(ROOT, a.dir); os.makedirs(game_dir, exist_ok=True)
    opt = os.path.join(game_dir, "options.txt")
    if not os.path.exists(opt):
        open(opt, "w").write("renderDistance:12\npauseOnLostFocus:false\nonboardAccessibility:false\nfullscreen:false\nguiScale:2\nnarrator:0\ntutorialStep:none\n")
    import re  # keep the dev client clean: no tutorial hints
    txt = open(opt).read()
    for k, v in (("tutorialStep", "none"), ("pauseOnLostFocus", "false"), ("renderClouds", '"false"')):
        txt = re.sub(rf"(?m)^{k}:.*$", f"{k}:{v}", txt) if f"{k}:" in txt else txt + f"{k}:{v}\n"
    open(opt, "w").write(txt)
    # the map's resource pack is always the current working copy
    rp = os.path.join(game_dir, "resourcepacks/last_ember")
    if os.path.exists(rp): shutil.rmtree(rp)
    shutil.copytree(os.path.join(ROOT, "resourcepack"), rp)
    txt = open(opt).read()
    txt = re.sub(r"(?m)^resourcePacks:.*$", 'resourcePacks:["vanilla","file/last_ember"]', txt) if "resourcePacks:" in txt else txt + 'resourcePacks:["vanilla","file/last_ember"]\n'
    open(opt, "w").write(txt)
    w, h = a.size.split("x")
    subs = {"natives_directory": f"{MC}/versions/{VER}/natives", "launcher_name": "last-ember-dev", "launcher_version": "1",
            "classpath": ":".join(cp), "auth_player_name": a.name, "version_name": VER, "game_directory": game_dir,
            "assets_root": f"{MC}/assets", "assets_index_name": d["assetIndex"]["id"], "auth_uuid": "00000000-0000-0000-0000-%012d" % (abs(hash(a.name)) % 10**12),
            "auth_access_token": "0", "clientid": "", "auth_xuid": "", "version_type": "release",
            "resolution_width": w, "resolution_height": h, "quickPlayMultiplayer": a.host}
    def expand(args, feats):
        out = []
        for x in args:
            if isinstance(x, str): out.append(x); continue
            r = x.get("rules")
            if r and not all(rr["action"] == "allow" and all(feats.get(k) == v for k, v in rr.get("features", {}).items()) and
                             ("os" not in rr or rules_ok([{"action": "allow", "os": rr["os"]}])) for rr in r): continue
            v = x["value"]; out += v if isinstance(v, list) else [v]
        return [s for s in out]
    feats = {"has_custom_resolution": True, "is_quick_play_multiplayer": True}
    jvm = expand(d["arguments"]["jvm"], feats); game = expand(d["arguments"]["game"], feats)
    def sub(s):
        for k, v in subs.items(): s = s.replace("${%s}" % k, v)
        return s
    java = glob.glob(f"{ROOT}/server/jdk25/*/Contents/Home/bin/java")[0]
    cmd = [java, f"-Xmx{a.mem}", f"-javaagent:{ROOT}/server/shotagent.jar={game_dir}"] + [sub(s) for s in jvm] + [d["mainClass"]] + [sub(s) for s in game]
    os.makedirs(f"{game_dir}/logs", exist_ok=True)
    try:  # camera player must not die/fall on join: new joiners become spectators (best effort, server may be down)
        import importlib.util
        sp = importlib.util.spec_from_file_location("rcon", os.path.join(ROOT, "tools/rcon.py")); rc = importlib.util.module_from_spec(sp); sp.loader.exec_module(rc)
        rc.run("defaultgamemode spectator"); rc.run(f"gamemode spectator {a.name}")
    except Exception as e:
        print("note: could not set spectator default via RCON:", e, file=sys.stderr)
    p = subprocess.Popen(cmd, cwd=game_dir, stdout=open(f"{game_dir}/logs/stdout.txt", "w"), stderr=subprocess.STDOUT, start_new_session=True)
    # once the camera is in, give the server its normal default back (real players must not join as spectators)
    restore = (f"import time,sys; sys.path.insert(0,{os.path.join(ROOT, 'tools')!r}); import rcon\n"
               f"for _ in range(120):\n    time.sleep(2)\n    if {a.name!r} in rcon.run('list'): break\n"
               f"rcon.run('gamemode spectator {a.name}'); rcon.run('defaultgamemode survival')\n")
    subprocess.Popen([sys.executable, "-c", restore], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(p.pid)

main()
