#!/usr/bin/env python3
"""T-033: the frames of the report (docs/reports/T-033/*.jpg, 1280 wide) from the dev client Cam (the camera, spectator).
  python3 tools/build/mines_shots.py [name ...]        (no names: all)
Frames: yard_day / yard_night (the yard with the headframe from the trail), office (the lunch on the table), journal (the journal open,
`keep`), adit (the adit's mouth), h1 (H1 with its lanterns and coal), h2 (H2 with iron in the wall), cave_before / cave_dust / cave_after
(cave-in 1: standing, the gravel dust of the warning, down), water (the knee-deep water with the drips on H3), big (the big collapse with
the pickaxe and the fresh crawl), pocket (the pocket with lapis, night vision), bran (Bran resting), dead (a dead miner in his helmet),
smith (Halvard's window with the deal of the letter, `keep`)."""
import importlib.util, json, math, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def load(n, path):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, path)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon", "tools/rcon.py"); tc = load("test_class", "tools/test_class.py")
R = rc.run
OUT = os.path.join(ROOT, "docs/reports/T-033"); os.makedirs(OUT, exist_ok=True)
CL = os.path.join(ROOT, "server/client")
M = json.load(open(os.path.join(ROOT, "server/build/r1/mines.json")))
LV = {int(k): v for k, v in M["levels"].items()}; Y = M["Y"]; f1, f2, f3 = LV[1], LV[2], LV[3]
def yawpitch(f, t):
    dx, dy, dz = t[0] - f[0], t[1] - f[1], t[2] - f[2]
    return math.degrees(math.atan2(-dx, dz)), -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
def jpg(name):
    from PIL import Image
    src = os.path.join(CL, "screenshots", name + ".png")
    if os.path.exists(src): Image.open(src).convert("RGB").resize((1280, 720)).save(os.path.join(OUT, name + ".jpg"), quality=80); os.remove(src)
LAST = [0.0]
def gap(sec=12.5):
    t = LAST[0] + sec - time.time()
    if t > 0: time.sleep(t)
def snap(name, hud=False, keep=False):
    gap()
    d = os.path.join(CL, "shot-done.txt")
    if os.path.exists(d): os.remove(d)
    open(os.path.join(CL, "shot-request.txt"), "w").write(f"{name} {1 if hud else 0} {'keep' if keep else 'clean'}\n")
    for _ in range(120):
        if os.path.exists(d): break
        time.sleep(0.5)
    time.sleep(0.6)
    LAST[0] = time.time(); jpg(name); print("  shot", name, flush=True)
def place(f, t, nv=False):
    R("gamemode spectator Cam"); yw, pt = yawpitch((f[0], f[1] + 1.62, f[2]), t)
    if nv: R("effect give Cam minecraft:night_vision infinite 0 true")
    else: R("effect clear Cam minecraft:night_vision")
    R(f"tp Cam {f[0]} {f[1]} {f[2]} {yw:.1f} {pt:.1f}")
def shot(name, f, t, settle=7, nv=False, hud=False):
    place(f, t, nv); time.sleep(settle); snap(name, hud)
def setup():
    open(os.path.join(CL, "shot-request.txt"), "w").write("!sneak_off\n"); time.sleep(2)
    for c in ("gamerule advance_time false", "gamerule locator_bar false", "weather clear", "difficulty easy", "gamemode spectator Cam2", "tp Cam2 258 %d -66" % (Y + 1),
              "function last_ember:mines/reset"):
        R(c)
    time.sleep(3)
def cave():
    R("function last_ember:mines/gen/restore_1"); R("time set 6000"); time.sleep(2)
    c = M["caves"][0]; x1, z1, x2, z2 = c["rect"]
    f, t = (x1 - 4.5, f2 + 1.0, -59.0), (x2, f2 + 2.2, -59.5)
    shot("cave_before", f, t, settle=7, nv=True)
    gap(); R("scoreboard players set #w1 le.mn 9"); time.sleep(1.0); snap("cave_dust")
    time.sleep(3); snap("cave_after")
    R("function last_ember:mines/gen/restore_1")
def journal():
    of = M["office"]; j = of["journal"]
    R("time set 6000"); R("gamemode adventure Cam"); R("effect clear Cam minecraft:night_vision")
    tc.face("Cam", j[0] + 0.5, j[1], j[2] + 2.3, j[0] + 0.5, j[1] + 0.8, j[2] + 0.5); time.sleep(3)
    open(os.path.join(CL, "shot-request.txt"), "w").write("!use\n"); time.sleep(2.5)
    snap("journal", hud=True, keep=True)
    open(os.path.join(CL, "shot-request.txt"), "w").write("!sneak_off\n"); time.sleep(2); R("gamemode spectator Cam")
def smith():
    R("time set 6000"); R('function last_ember:trader/reset {id:"smith"}'); time.sleep(2)
    R("gamemode survival Cam"); R("clear Cam"); R("loot give Cam loot last_ember:mines/bran_letter"); R("effect clear Cam minecraft:night_vision")
    tc.face("Cam", 58.5, 101, 25.3, 58.5, 101.9, 27.5); time.sleep(4)
    open(os.path.join(CL, "shot-request.txt"), "w").write("!use\n"); time.sleep(1.5)
    offers = R("data get entity @e[tag=le.tr_smith,limit=1] Offers.Recipes"); idx = offers.count("buy:") - 1
    open(os.path.join(CL, "shot-request.txt"), "w").write(f"!trade_sel {idx}\n"); time.sleep(1.5)
    snap("smith", hud=True, keep=True)
    open(os.path.join(CL, "shot-request.txt"), "w").write("!sneak_off\n"); time.sleep(2); R("clear Cam"); R("gamemode spectator Cam")
def dead():
    d = M["points"]["dead"][3]
    R("function last_ember:mines/reset"); time.sleep(3)
    yaw = math.radians(d[3]); fx, fz = d[0] - 2.2 * math.sin(yaw) * -1, d[2] - 2.2 * math.cos(yaw)
    shot("dead", (d[0] + 1.8, d[1] + 0.1, d[2] + 1.2), (d[0], d[1] + 1.4, d[2]), settle=7, nv=True)
def main(names):
    setup()
    hf = M["headframe"]; hc = ((hf[0] + hf[2]) / 2 + 0.5, Y + 9, (hf[1] + hf[3]) / 2 + 0.5)
    t = M["office"]["table"]; big = M["big_rect"]; br = M["points"]["bran"]
    S = {
        "yard_day": lambda: (R("time set 5000"), shot("yard_day", (259.5, Y + 9, -36.5), (hc[0] - 4, Y + 5, hc[2]), settle=14)),
        "yard_night": lambda: (R("time set 18000"), shot("yard_night", (259.5, Y + 9, -36.5), (hc[0] - 4, Y + 5, hc[2]), settle=10)),
        "office": lambda: (R("time set 6000"), shot("office", (261.6, Y + 1.0, -76.4), (t[0] + 0.8, t[1] + 1.0, t[2] + 0.5), settle=7)),
        "journal": journal,
        "adit": lambda: (R("time set 6000"), shot("adit", (276.5, Y + 1.5, -63.5), (284, Y + 1.5, -65.5), settle=7)),
        "h1": lambda: (R("time set 6000"), shot("h1", (299.5, f1 + 1.0, -44.5), (299.5, f1 + 2.0, -60.5), settle=8)),
        "h2": lambda: (R("time set 6000"), shot("h2", (305.5, f2 + 1.0, -50.6), (305.5, f2 + 1.8, -58.5), settle=8, nv=True)),
        "cave": cave,
        "water": lambda: (R("time set 6000"), shot("water", (289.6, f3 + 1.0, -44.5), (277, f3 + 1.5, -45.0), settle=8, nv=True)),
        "big": lambda: (R("time set 6000"), shot("big", (263.6, f3 + 1.0, big[3] + 4.6), (264.6, f3 + 1.3, big[3] - 1.5), settle=8, nv=True)),
        "pocket": lambda: (R("time set 6000"), shot("pocket", (266.6, f3 + 1.2, -70.5), (259.5, f3 + 1.8, -73.0), settle=8, nv=True)),
        "bran": lambda: (R("time set 6000"), shot("bran", (br[0] + 2.4, br[1] + 0.2, br[2] + 1.6), (br[0], br[1] + 1.5, br[2]), settle=7, nv=True)),
        "dead": dead,
        "smith": smith,
    }
    for n in (names or list(S)):
        S[n]()
    R("gamemode spectator Cam"); R("effect clear Cam minecraft:night_vision"); R("function last_ember:mines/reset")

if __name__ == "__main__":
    main(sys.argv[1:])
