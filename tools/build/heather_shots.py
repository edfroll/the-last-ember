#!/usr/bin/env python3
"""T-031: the frames of the report (docs/reports/T-031/*.jpg, 1280 wide) from the dev client Cam (the camera, spectator).
  python3 tools/build/heather_shots.py [name ...]        (no names: all)
Frames: village_day, village_dusk (from the bridge), street, odd_walled, odd_ladder, odd_beds, odd_roof, odd_deep, odd_reversed, well,
mill_a + mill_b (12.5 s apart: the sails turned), garden, church_inside, ringer, workers, noon (the dead in the sun, not burning),
midnight (frozen, facing the belfry), ridge_pad (the head and the sword from the pad of bonfire 9), ridge_shelf (from the village shelf),
mouth (the view from the mouth to the northern Dol), intro (the window of the acquaintance, `keep`)."""
import importlib.util, json, math, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def load(n, path):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, path)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon", "tools/rcon.py")
R = rc.run
OUT = os.path.join(ROOT, "docs/reports/T-031"); os.makedirs(OUT, exist_ok=True)
CL = os.path.join(ROOT, "server/client")
M = json.load(open(os.path.join(ROOT, "server/build/r1/heather.json")))
sys.path.insert(0, os.path.join(ROOT, "tools/build"))
import heather_build as HB
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
def hfr(h, u, w, y):
    f = HB.Frame(h["r"], h["face"]); x, z = f.xz(u, w); return (x + 0.5, y, z + 0.5)
def house(kind):
    return next(h for h in M["houses"] if h["kind"] == kind)

def setup():
    open(os.path.join(CL, "shot-request.txt"), "w").write("!sneak_off\n"); time.sleep(2)
    for c in ("gamerule advance_time false", "gamerule locator_bar false", "weather clear", "difficulty easy", "gamemode spectator Cam2", "tp Cam2 70 64 -416"):
        R(c)

def main(names):
    setup()
    br = M["bridge"]; sq = M["square"]; sL = M["sL"]; ch = M["church"]; L = ch["L"]
    wx, wy, wz = M["well"]; hd = M["head"]; ml = M["mill"]
    st = M["street"]
    mid = st[len(st) // 3]
    S = {
        "village_day": lambda: (R("time set 5000"), shot("village_day", (70.5, br["south_y"] + 2, -427.5), (60, 100, -480), settle=12)),
        "village_dusk": lambda: (R("time set 12600"), shot("village_dusk", (70.5, br["south_y"] + 2, -427.5), (60, 100, -480), settle=10)),
        "street": lambda: (R("time set 6000"), shot("street", (mid[0] + 0.5, mid[2] / 2 + 2.6, mid[1] + 0.5), (sq[0] + 5, sL + 3, sq[1] + 5), settle=9)),
        "odd_walled": lambda: odd("walled"),
        "odd_ladder": lambda: odd("ladder"),
        "odd_beds": lambda: odd("beds"),
        "odd_roof": lambda: odd("roof"),
        "odd_deep": lambda: odd("deep"),
        "odd_reversed": lambda: odd("reversed"),
        "well": lambda: (R("time set 6000"), shot("well", (wx + 5.5, wy + 2, wz + 4.5), (wx + 0.5, wy + 1, wz + 0.5), settle=8)),
        "mill": lambda: mill(),
        "garden": lambda: garden(),
        "church_inside": lambda: (R("time set 6000"), shot("church_inside", (ch["nave"][2] - 1.5, L + 3.2, (ch["nave"][1] + ch["nave"][3]) / 2 + 0.5), (ch["nave"][0] + 3, L + 1.2, ch["nave"][1] + 2), settle=8, nv=True)),
        "ringer": lambda: (R("time set 14000"), shot("ringer", (M["ringer"][0] + 2.6, M["ringer"][1] + 0.4, M["ringer"][2] + 2.6), (ch["bell"][0] + 0.5, ch["bell"][1], ch["bell"][2] + 0.5), settle=8)),
        "workers": lambda: workers(),
        "noon": lambda: noon(),
        "midnight": lambda: midnight(),
        "ridge_pad": lambda: (R("time set 6000"), shot("ridge_pad", (P_PAD[0], P_PAD[1] + 1, P_PAD[2]), (hd["sword_base"][0], 120, hd["sword_base"][2]), settle=14)),
        "ridge_shelf": lambda: (R("time set 6000"), shot("ridge_shelf", (sq[0] + 0.5, sL + 6, sq[3] + 0.5), (hd["sword_base"][0], 118, hd["sword_base"][2]), settle=12)),
        "mouth": lambda: (R("time set 6000"), shot("mouth", (M["tp"]["mouth"][0], M["mouth_y"] + 0.1, M["tp"]["mouth"][2] + 1.5), (M["tp"]["mouth"][0], M["mouth_y"] - 8, M["tp"]["mouth"][2] - 60), settle=12)),
        "intro": lambda: intro(),
    }
    order = [n for n in S if n != "intro"] + ["intro"]
    for n in (names or order):
        if n in S: S[n]()
    R("gamerule advance_time true"); R("gamemode survival Cam2")

P_PAD = (65.5, 64, -415.5)          # a cell of the pad that sees the sword over the houses of the bank
def odd(k):
    R("time set 6000")
    if k == "walled":
        h = house("walled"); L = h["L"]; f = HB.Frame(h["r"], h["face"]); du = f.W // 2
        shot("odd_walled", hfr(h, du, f.D - 2, L + 1), hfr(h, du + 1, 0, L + 1.6), settle=7, nv=True)          # from inside: the walled door, the window beside
    elif k == "ladder":
        h = house("ladder"); L = h["L"]; f = HB.Frame(h["r"], h["face"])
        shot("odd_ladder", hfr(h, f.W - 2, 4, L + 1), hfr(h, 1, 2, L + 3.2), settle=7, nv=True)
    elif k == "beds":
        h = house("ladder"); L = h["L"]; f = HB.Frame(h["r"], h["face"])
        shot("odd_beds", hfr(h, f.W - 2, f.D // 2, L + 5), hfr(h, 0, f.D // 2, L + 6.2), settle=7, nv=True)
    elif k == "roof":
        h = house("roof"); f = HB.Frame(h["r"], h["face"]); t = h["roof_table"]
        shot("odd_roof", hfr(h, f.W + 3, -3, h["top"] + 4), (t[0] + 0.5, t[1] + 0.5, t[2] + 0.5), settle=7)
    elif k == "deep":
        h = house("deep"); L = h["L"]; f = HB.Frame(h["r"], h["face"])
        shot("odd_deep", hfr(h, f.W // 2, 1, L + 1.5), hfr(h, f.W // 2, f.D // 2, h["bot"] + 1), settle=7, nv=True)
    elif k == "reversed":
        h = house("reversed"); L = h["L"]; f = HB.Frame(h["r"], h["face"])
        shot("odd_reversed", hfr(h, f.W // 2 - 1, 2, L + 1), hfr(h, f.W // 2, f.D - 1, L + 1.6), settle=7, nv=True)

def mill():
    ml = M["mill"]; ax, ay, az = ml["axle"]
    R("time set 6000"); f = (ax + 4, ay - 4, az + 16); t = (ax, ay, az)
    R("tp Cam2 %.1f %.1f %.1f" % (ax - 3, ay - 10, az + 4))        # a player within 64: the sails turn (Cam is a spectator)
    R("gamemode adventure Cam2")
    place(f, t); time.sleep(8); snap("mill_a"); snap("mill_b")
    R("gamemode spectator Cam2"); R("tp Cam2 70 64 -416")

def garden():
    g = M["gardens"]["garden1"]; r = g["r"]
    R("time set 7000"); shot("garden", (r[2] + 2.5, g["L"] + 4, r[3] + 3.5), (r[0] + 3, g["L"] + 1, r[1] + 2), settle=8)

def workers():
    z = next(q for q in M["zombies"] if q["where"] == "garden1")
    R("time set 6000"); R("function last_ember:heather/reset"); time.sleep(3)
    x, y, zz = z["pos"]
    shot("workers", (x + 4.5, y + 1.0, zz + 4.5), (x, y + 1.2, zz), settle=8)

def noon():
    z = next(q for q in M["zombies"] if q["where"] == "well")
    R("time set 6000"); time.sleep(2); x, y, zz = z["pos"]
    shot("noon", (x + 5.5, y + 2, zz + 3.5), (x, y + 1, zz), settle=10)

def midnight():
    z = next(q for q in M["zombies"] if q["where"] == "well")
    x, y, zz = z["pos"]
    R("tp Cam2 %.1f %.1f %.1f" % (M["ringer"][0] + 2, M["ringer"][1], M["ringer"][2])); R("gamemode adventure Cam2")      # within 96 of the bell
    place((x + 4.5, y + 1.5, zz + 5.5), (x, y + 1.2, zz), nv=True)
    R("gamerule advance_time true"); R("time set 17985"); time.sleep(3.5)
    R("gamerule advance_time false")
    snap("midnight")
    R("gamemode spectator Cam2"); R("tp Cam2 70 64 -416"); R("time set 6000")

def intro():
    R("time set 6000"); R("gamemode adventure Cam"); R("tag Cam remove le.hmet")
    rx, ry, rz, yaw = M["ringer"]
    R(f"tp Cam {rx + 1.6} {ry} {rz} 90 10"); time.sleep(4)
    R("execute as Cam at @s run function last_ember:heather/meet"); time.sleep(3)
    snap("intro", hud=True, keep=True)
    open(os.path.join(CL, "shot-request.txt"), "w").write("!sneak_off\n"); time.sleep(2)
    R("gamemode spectator Cam")

if __name__ == "__main__":
    main(sys.argv[1:])
