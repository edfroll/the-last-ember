#!/usr/bin/env python3
"""T-028: the frames of the report (docs/reports/T-028/*.jpg, 1280 wide) from the dev client Cam (the server, Cam and Cam2 running):
the gorge and the colossi from bonfire 7 by day and at sunset, the causeway at night, the pier between the colossi, the sword and its
sign, the eyes asleep / lit / dim, the strike and the flight (Cam2 struck three times, a frame each), the stair tunnel, the
rest platform with the niches, the arch with the roots, the view down from the bridgehead, the bridge, the gate, the table, the faded
lake with the broken arm, an overview.
  python3 tools/build/castle_shots.py [name ...]"""
import importlib.util, json, math, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def load(n, path):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, path)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon", "tools/rcon.py")
R = rc.run
OUT = os.path.join(ROOT, "docs/reports/T-028"); os.makedirs(OUT, exist_ok=True)
CL = os.path.join(ROOT, "server/client")
M = json.load(open(os.path.join(ROOT, "server/build/r1/castle.json")))
sys.path.insert(0, os.path.join(ROOT, "tools/build")); import castle_plan as P
W = P.W
def yawpitch(f, t):
    dx, dy, dz = t[0] - f[0], t[1] - f[1], t[2] - f[2]
    return math.degrees(math.atan2(-dx, dz)), -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
def jpg(name):
    from PIL import Image
    src = os.path.join(CL, "screenshots", name + ".png")
    if os.path.exists(src): Image.open(src).convert("RGB").resize((1280, 720)).save(os.path.join(OUT, name + ".jpg"), quality=80)
def snap(name, hud=False, pre=True, clean=False):
    for nm in ((name + "__pre",) if pre else ()) + (name,):
        d = os.path.join(CL, "shot-done.txt")
        if os.path.exists(d): os.remove(d)
        open(os.path.join(CL, "shot-request.txt"), "w").write(f"{nm} {1 if hud else 0}{' clean' if clean else ''}\n")
        for _ in range(120):
            if os.path.exists(d): break
            time.sleep(0.5)
        time.sleep(1.0 if nm == name else 11.0)
    jpg(name); print("  shot", name, flush=True)
def place(f, t):
    R("gamemode spectator Cam"); yw, pt = yawpitch((f[0], f[1] + 1.62, f[2]), t)
    R(f"tp Cam {f[0]} {f[1]} {f[2]} {yw:.1f} {pt:.1f}")
def shot(name, f, t, hud=False, settle=7):
    place(f, t); time.sleep(settle); snap(name, hud)
def day(): R("time set noon")
def setup():
    R("gamerule advance_time false"); R("gamerule locator_bar false"); R("weather clear 100000"); R("difficulty peaceful")
    R("gamemode spectator Cam2"); R("tp Cam2 400 220 120")
    for c in ("forceload add 350 -70 470 10", "forceload add 400 0 490 100"): R(c)
    R("function last_ember:castle/reset"); day(); time.sleep(3)
EYE = M["dp"]["eyes"]
def from7():
    day(); shot("from7_day", (362.5, 169, -44.5), (426, 138, -34))
    R("time set 12600"); shot("from7_sunset", (362.5, 169, -44.5), (426, 138, -34)); day()
def causeway():
    R("time set 18000"); shot("causeway_night", (386.5, W + 2, -52.5), (430, 128, -36)); day()
def pier():
    shot("pier", (403.5, W + 3, -34.5), (432, 128, -34))
def sword():
    s = M["sword"]["sign"]; g = M["sword"]["guard"]
    shot("sword", (404.5, W + 3, -47.5), (416, W + 8, -46))
    shot("sword_sign", (s[0] - 0.6, W + 2, s[2] - 1.4), (s[0] + 0.5, s[1] + 0.5, s[2] + 0.5), settle=6)
    shot("sword_causeway", (400.5, W + 2, -52.5), (416, W + 8, -45.5))
def eyes():
    f = (410.5, W + 40, -46.5); t = (424, W + 45, -46)
    R("tick freeze"); R("function last_ember:castle/gen/eyes_asleep"); shot("eyes_asleep", f, t)
    R("function last_ember:castle/gen/eyes_lit"); shot("eyes_lit", f, t)
    R("function last_ember:castle/gen/eyes_dim"); shot("eyes_dim", f, t)
    R("function last_ember:castle/gen/eyes_asleep"); R("tick unfreeze")
def strike():
    """Cam2 (survival) walks onto the pier three times (a frame each: the palms charging, the start of the flight, the flight high over
    the channel); 13 s between the frames: the «Saved screenshot» line of the frame before is gone"""
    R("difficulty easy"); R("tp Cam2 400.5 %d -52.5" % (W + 2)); time.sleep(1); R("gamemode survival Cam2"); R("tag Cam2 remove le.cpass")
    place((402.5, W + 9, -22.5), (424, W + 14, -33)); time.sleep(12)
    def go():
        R("scoreboard players set Cam2 le.cg 0"); R("effect give Cam2 minecraft:instant_health 1 10 true"); R("tp Cam2 426.5 %d -33.5 90 0" % (W + 2))
    def flying(): return "le.cfly" in R("data get entity Cam2 Tags")
    go(); time.sleep(0.55); snap("strike_charge", pre=False)
    time.sleep(13); go()
    for _ in range(60):
        if flying(): break
        time.sleep(0.05)
    snap("strike_flight1", pre=False)
    time.sleep(13); go()
    for _ in range(60):
        if flying(): break
        time.sleep(0.05)
    time.sleep(0.45); snap("strike_flight2", pre=False)
    time.sleep(3); R("gamemode spectator Cam2"); R("tp Cam2 400 220 120"); R("difficulty peaceful")
def stair():
    shot("stair_tunnel", (430.5, W + 2, -35.5), (444, 129.5, -35.5))
    shot("rest_niches", (418.5, 150, -34), (431, 147, -34))
    shot("arch_roots", (424.5, 166, -32), (433, 166, -32))
    shot("down_from_head", (430.5, 166, -6.5), (405, W, -30))
def bridge():
    shot("bridge", (451.5, 163, -6.5), (451.5, 168, 31))
    shot("gate", (451.5, 163, 24.5), (451.5, 165.5, 31))
    shot("table", (448, 205, 14), (447, 166, 64))
def faded():
    R("function last_ember:region/gen/fade_r1"); time.sleep(8)
    shot("faded_lake", (396.5, 135, -4.5), (424, 128, -26), settle=8)
    shot("faded_arm", (408.5, 130, -14.5), (424, 158, -25), settle=6)
    R("function last_ember:region/gen/unfade_r1"); time.sleep(8)
CLIFF_EYE, CLIFF_AT = (414.5, 119, 11.5), (448, 146, 27)     # the dry rift (its west sill), along the north face of the table
def cliff():
    """the face of the rock from the moat, close (HQ review T-028: the living rock)"""
    R("time set 2000"); shot("cliff", CLIFF_EYE, CLIFF_AT); day()
def overview():
    shot("overview", (330, 232, 30), (440, 140, -10), settle=12)
SH = dict(cliff=cliff, from7=from7, causeway=causeway, pier=pier, sword=sword, eyes=eyes, strike=strike, stair=stair, bridge=bridge, faded=faded, overview=overview)
if __name__ == "__main__":
    setup()
    for a in sys.argv[1:] or list(SH): SH[a]()
    R("gamemode survival Cam"); R("gamemode survival Cam2"); R("difficulty easy"); day()
