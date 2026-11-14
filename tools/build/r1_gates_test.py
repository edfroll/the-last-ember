#!/usr/bin/env python3
"""T-022: the walk bot cannot get through the west pass (rubble) or over the south bridge (raised middle) while they are closed,
and walks through after gate/open. Needs the server and the dev client Cam (tools/build/r1_routes.py first).
  pass:   the gorge trail from the Р2 side (route r1_pass_r1_weepers, up to x -600)
  bridge: along the deck x 0.5 from the north approach (z 570) to the south one (z 718)
Usage: python3 tools/build/r1_gates_test.py [pass bridge]"""
import json, math, os, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools/build")); sys.path.insert(0, os.path.join(ROOT, "tools"))
from scanio import Scan
import rcon as rc
W = os.path.join(ROOT, "server/build/walk")
m = json.load(open(os.path.join(ROOT, "server/build/r1/r1.json"))); deck = m["bridge"]["deck"]
ok = bad = 0
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n)
    else: bad += 1; print("  FAIL", n, e)
def walk(route, name):
    p = os.path.join(W, name + ".json"); json.dump(route, open(p, "w"))
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools/walkbot.py"), p, "--out", os.path.join(W, name)], capture_output=True, text=True)
    probs = [l for l in r.stdout.splitlines() if l.startswith("PROBLEM")]; end = [l for l in r.stdout.splitlines() if l.startswith("END")]
    return probs, (end[0] if end else r.stdout[-300:])
def routes():
    pr = json.load(open(os.path.join(W, "r1_pass_r1_weepers.json")))
    pz = {"start": pr["start"], "points": [q for q in pr["points"] if q[0] <= -600]}
    S = Scan(os.path.join(ROOT, "server/build/r1/after.bin"))
    pts = []
    for z in range(573, 719, 3):
        y = deck + 1 if 619 <= z <= 681 else S.g(0, z) + 1
        pts.append([0.5, z + 0.5, y])
    return pz, {"start": [0.5, S.g(0, 570) + 1.2, 570.5], "points": pts}
def run(what):
    pz, br = routes()
    rc.run("gamerule send_command_feedback false"); rc.run("difficulty peaceful"); rc.run("time set noon")
    for gid, route, nm, where in (("west_pass", pz, "pass", "the west pass"), ("south_bridge", br, "bridge", "the south bridge")):
        if nm not in what: continue
        print(f"[{where}]")
        rc.run(f'function last_ember:gate/close {{id:"{gid}"}}')
        sx, sy, sz = route["start"]; rc.run(f"gamemode spectator Cam"); rc.run(f"tp Cam {sx} {sy + 20} {sz}"); time.sleep(5)   # the template is placed once its chunk is loaded
        probs, end = walk(route, f"r1_gate_{nm}_closed")
        chk(f"{where} closed: the bot is stopped ({len(probs)} problems; {end})", len(probs) > 0, probs)
        rc.run(f'function last_ember:gate/open {{id:"{gid}"}}'); time.sleep(4)
        probs, end = walk(route, f"r1_gate_{nm}_open")
        chk(f"{where} open: the bot walks through ({end})", len(probs) == 0, probs)
        rc.run(f'function last_ember:gate/close {{id:"{gid}"}}'); time.sleep(2)
    print(f"\n{ok} ok, {bad} failed"); sys.exit(1 if bad else 0)
if __name__ == "__main__": run(sys.argv[1:] or ["pass", "bridge"])
