#!/usr/bin/env python3
"""T-022 frames (server + client Cam): writes server/build/r1/shots_<time>.json and runs tools/screenshot.py -> docs/reports/T-022/*.jpg
Usage: python3 tools/build/r1_shots.py [noon|midnight]"""
import json, math, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
m = json.load(open(os.path.join(ROOT, "server/build/r1/r1.json")))
B = {bid: (x, y, z) for n, bid, x, y, z in m["bonfires"]}
def look(cx, cy, cz, tx, ty, tz):
    dx, dy, dz = tx - cx, ty - cy, tz - cz
    return round(math.degrees(math.atan2(-dx, dz)), 1), round(-math.degrees(math.atan2(dy, math.hypot(dx, dz))), 1)
sys.path.insert(0, os.path.join(ROOT, "tools/build")); from scanio import Scan
S = Scan(os.path.join(ROOT, "server/build/r1/after.bin"))
def top(x, z): return int(S.top[int(z) - S.z0, int(x) - S.x0])
shots = []
def add(name, c, t, h=None, settle=10):
    """c = (x, y, z) or (x, z) with h: the camera h blocks above the highest block there (trees included)"""
    if h is not None: c = (c[0], max(top(c[0] - 1, c[1]), top(c[0], c[1]), top(c[0] + 1, c[1]), top(c[0], c[1] - 1), top(c[0], c[1] + 1)) + h, c[1])
    yaw, pitch = look(*c, *t); shots.append(dict(name=name, x=c[0], y=c[1], z=c[2], yaw=yaw, pitch=pitch, settle=settle))
add("r1_wall_from_north_edge", (-300.5, -700.5), (-250, 150, -870), h=18, settle=12)
add("r1_bridge_over_rift", (-45.5, 118, 650.5), (0, 120, 650))
add("r1_rift_walls", (90.5, 72, 646.5), (210, 40, 652))       # rims, ledges, cornices, scree, horizontal strata (HQ review, 5)
add("r1_bridge_from_south", (0.5, 129.6, 700.5), (0.5, 128, 650))
add("r1_pass_rubble", (-622.5, -189.5), (-645, 82, -190), h=5)
w = B["r1_weepers"]; add("r1_view_from_circle_bonfire", (w[0] + 0.5, w[1] + 2.6, w[2] - 3.5), (w[0] + 120, w[1] - 10, w[2] + 10))
add("r1_shortcut_door_ledge", (-370.5, -195.5), (-380, 113, -196), h=3)
def clear(c, t):
    """the line from the camera to the target passes above every block (trees included) of the scan"""
    n = int(math.dist(c, t)) * 2
    for i in range(2, n - 2):
        f = i / n; x, y, z = (c[k] + (t[k] - c[k]) * f for k in range(3))
        if top(x, z) + 1 > y: return False
    return True
for bid in ("r1_garden", "r1_grove", "r1_fens"):                       # a bonfire seen from its trail: the nearest trail point with a clear view
    n_ = next(b[0] for b in m["bonfires"] if b[1] == bid); bx, by, bz = B[bid]; tg = (bx + 0.5, by + 1.5, bz + 0.5)
    t = next(t for t in m["trails"] if t["b"] == n_ and t["prof"]); pr = t["prof"]
    pick = None
    for k in range(18, min(80, len(pr))):
        p = pr[len(pr) - 1 - k]
        for h in (2.6, 4, 6):
            c = (p[0], p[2] + h, p[1])
            if clear(c, tg): pick = c; break
        if pick: break
    pick = pick or (pr[max(0, len(pr) - 30)][0], pr[max(0, len(pr) - 30)][2] + 8, pr[max(0, len(pr) - 30)][1])
    add(f"r1_bonfire_from_trail_{bid[3:]}", pick, tg)
# overviews from high above the Refuge (HQ review: «камера над Приютом, взгляд на север и на юг», 12 chunks)
add("r1_overview_north", (0.5, 205, 60.5), (0.5, 110, -170.5), settle=20)
add("r1_overview_south", (0.5, 205, -60.5), (0.5, 110, 230.5), settle=20)
add("r1_overview_west", (-280.5, 160, 0.5), (-520, 120, 0), settle=15)
tm = sys.argv[1] if len(sys.argv) > 1 else "noon"
if tm != "noon": shots = [dict(s, name=s["name"] + "_night") for s in shots if s["name"] in ("r1_view_from_circle_bonfire", "r1_bonfire_from_trail_fens", "r1_overview_north", "r1_bridge_over_rift")]
sys.path.insert(0, os.path.join(ROOT, "tools")); import importlib.util
sp = importlib.util.spec_from_file_location("rcon", os.path.join(ROOT, "tools/rcon.py")); rc = importlib.util.module_from_spec(sp); sp.loader.exec_module(rc)
rc.run("gamerule locator_bar false")          # the locator bar is drawn even with the HUD hidden
spec = os.path.join(ROOT, f"server/build/r1/shots_{tm}.json"); json.dump({"time": tm, "weather": "clear", "shots": shots}, open(spec, "w"), indent=1)
out = os.path.join(ROOT, "docs/reports/T-022"); os.makedirs(out, exist_ok=True)
subprocess.run([sys.executable, os.path.join(ROOT, "tools/screenshot.py"), spec, "--out", out], check=False)
rc.run("gamerule locator_bar true")
for s in shots:
    src = os.path.join(out, s["name"] + ".png")
    if os.path.exists(src): subprocess.run(["convert", src, "-resize", "1600x", "-quality", "80", src[:-4] + ".jpg"]); os.remove(src)
