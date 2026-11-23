#!/usr/bin/env python3
"""T-032: the frames of the report (docs/reports/T-032/*.jpg, 1280 wide) from the dev client Cam (the camera, spectator).
  python3 tools/build/spiders_shots.py [name ...]        (no names: all)
Frames: border (autumn -> white from the trail Heather -> Garden, day), victims (the trail of the victims with their things), wire (a
trip wire with the scratch), canopy (the canopy from inside at noon), cocoons (cocoons on chains), remains (a cocoon with remains),
live (the live cocoon with the bow), giant (the fallen giant and the drop from above the lid), nest (inside, night vision), roots (the
burrow of roots), mistress (in the fight, a player next to her), belfry (Toivo next to the ringer), fade_before / fade_after (the
fading of chapter I), seen (Toivo's window «Что ты видел?», `keep`)."""
import importlib.util, json, math, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def load(n, path):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, path)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon", "tools/rcon.py")
R = rc.run
OUT = os.path.join(ROOT, "docs/reports/T-032"); os.makedirs(OUT, exist_ok=True)
CL = os.path.join(ROOT, "server/client")
M = json.load(open(os.path.join(ROOT, "server/build/r1/spiders.json")))
sys.path.insert(0, os.path.join(ROOT, "tools/build"))
import numpy as np
import spiders_plan as P
_T = np.load(os.path.join(ROOT, "server/build/r1/spiders_T.npz")); TT = _T["T"]; TX, TZ = int(_T["x1"]), int(_T["z1"])
def G(x, z): return int(TT[int(z) - TZ, int(x) - TX])
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
    for c in ("gamerule advance_time false", "gamerule locator_bar false", "weather clear", "difficulty easy", "gamemode spectator Cam2", "tp Cam2 205 160 -350"):
        R(c)

def feet(p): return p[2] / 2 + 1
def main(names):
    setup()
    pv, pa = M["pv"], M["pa"]; F = M["floor"]; hole = M["hole"]; lv = M["live"]; nr = M["nest_r"]; gx, za, zb = M["giant_xz"]
    gr = P.grids()
    S = {
        "border": lambda: (R("time set 5000"), shot("border", (pa[0][0] + 1.5, feet(pa[0]) + 1.2, pa[0][1] + 8.5), (165, 138, -292), settle=14)),
        "victims": lambda: victims(),
        "wire": lambda: wire(),
        "canopy": lambda: (R("time set 6000"), shot("canopy", (pv[len(pv) // 2][0] + 0.5, feet(pv[len(pv) // 2]) + 0.2, pv[len(pv) // 2][1] + 0.5), (pv[len(pv) // 2][0] + 6, feet(pv[len(pv) // 2]) + 9, pv[len(pv) // 2][1] - 8), settle=9)),
        "cocoons": lambda: cocoons(),
        "remains": lambda: remains(),
        "live": lambda: (R("function last_ember:spiders/reset"), R("time set 6000"), time.sleep(3), shot("live", (lv["clearing"][0] + 2.5, lv["clearing"][1] + 0.3, lv["clearing"][2] + 3.5), (lv["origin"][0] + 1, lv["origin"][1] + 0.5, lv["origin"][2] + 1), settle=8)),
        "giant": lambda: (R("time set 6000"), shot("giant", (hole[2] + 6.5, P.B4(gr, hole[2] + 6, hole[1] + 8) + 4.5, hole[1] + 9.5), (hole[0] + 1, P.B4(gr, hole[0] + 1, hole[1] + 1) - 3, hole[1] + 1), settle=9)),
        "nest": lambda: (R("time set 6000"), shot("nest", (nr[2] - 1.5, F + 4, nr[3] - 2.5), (nr[0] + 6, F + 2, nr[1] + 6), settle=8, nv=True)),
        "roots": lambda: roots(),
        "mistress": lambda: mistress(),
        "belfry": lambda: belfry(),
        "fade": lambda: faded(),
        "seen": lambda: seen(),
    }
    order = [n for n in S if n != "seen"] + ["seen"]
    for n in (names or order):
        if n in S: S[n]()
    R("gamerule advance_time true"); R("gamemode survival Cam2"); R("function last_ember:spiders/reset")

def victims():
    pv = M["pv"]; R("time set 6000")
    a = pv[2]; b = pv[16]
    shot("victims", (a[0] + 0.5, feet(a) + 0.3, a[1] + 0.5), (b[0] + 0.5, feet(b) - 0.5, b[1] + 0.5), settle=9)
def wire():
    t = M["trips"][0]; w = t["wire"][0]; h = t["hooks"][0]
    R("time set 6000"); dx, dz = (w[0] - h[0], w[2] - h[2])
    f = (w[0] + 0.5 - 3 * dz + 1.5 * dx, w[1] + 0.9, w[2] + 0.5 + 3 * dx + 1.5 * dz)
    shot("wire", f, (h[0] + 0.5, w[1] + 0.6, h[2] + 0.5), settle=8, nv=True)
def cocoons():
    co = sorted(M["cocoons"], key=lambda k: abs(k["x"] - 160) + abs(k["z"] + 300))[0]
    R("time set 6000")
    shot("cocoons", (co["x"] + 5.5, co["y"] - 0.5, co["z"] + 5.5), (co["x"] + 0.5, co["y"] + 1.5, co["z"] + 0.5), settle=8, nv=True)
def remains():
    r = M["remains"][1]; b = r["barrel"]; f = r["front"]
    R("time set 6000"); R("function last_ember:spiders/gen/props_put")
    shot("remains", (f[0] + 0.5 + (f[0] - b[0]) * 1.5, b[1] + 1.2, f[1] + 0.5 + (f[1] - b[2]) * 1.5), (b[0] + 0.5, b[1] + 0.6, b[2] + 0.5), settle=8, nv=True)
def roots():
    lp = M["lair_path"]; q = lp[len(lp) * 2 // 3]; e = lp[-1]
    R("time set 6000"); F = M["floor"]
    shot("roots", (lp[3][0] + 3.5, F + 2.2, lp[3][1] + 4.5), (q[0] + 0.5, q[2] / 2 + 1, q[1] + 0.5), settle=8, nv=True)
def mistress():
    """the Mistress awake (a fight held still for the frame: NoAI after waking) and Cam2 next to her for the scale"""
    bx, by, bz = M["points"]["boss"]; F = M["floor"]
    R("time set 6000"); R("function last_ember:spiders/boss_reset"); time.sleep(2)
    R("gamemode adventure Cam2"); R(f"tp Cam2 {bx + 3.5} {F + 1} {bz + 1.5}"); R(f"effect give Cam2 minecraft:resistance infinite 4 true")
    time.sleep(2.5)
    R("execute as @e[type=minecraft:spider,tag=le.sp_boss,limit=1] run data modify entity @s NoAI set value 1b")
    R(f"execute as @e[type=minecraft:spider,tag=le.sp_boss,limit=1] run tp @s {bx} {by} {bz} -90 0")
    R(f"tp Cam2 {bx + 3.6} {F + 1} {bz + 0.5} 90 0")
    shot("mistress", (bx + 6.5, F + 3.2, bz + 7.5), (bx + 1.5, F + 1.3, bz + 0.5), settle=5, nv=True)
    R("gamemode spectator Cam2"); R("tp Cam2 205 160 -350"); R("function last_ember:spiders/boss_reset")
def belfry():
    b = M["toivo_pts"]["belfry"]
    R("time set 6000"); R("scoreboard players set #toivo le.sp 2"); R("data modify storage last_ember:spiders toivo set value 2")
    R("forceload add 30 -508 40 -498"); R("function last_ember:spiders/gen/toivo_belfry"); time.sleep(2)
    shot("belfry", (b[0] + 0.0, b[1] + 0.6, b[2] - 2.6), (33.5, 131.0, -504.0), settle=8)
    R("forceload remove 30 -508 40 -498")
def faded():
    R("time set 6000"); place(FADE_CAM, FADE_TGT); time.sleep(14); snap("fade_before")
    R("function last_ember:altar/set_chapters {n:1}"); R("function last_ember:region/gen/fade_r1"); time.sleep(16)
    snap("fade_after")
    R("function last_ember:region/gen/unfade_r1"); R("function last_ember:altar/set_chapters {n:0}"); time.sleep(6)
FADE_CAM = (204, 172, -230); FADE_TGT = (150, 128, -300)
def seen():
    """Toivo's window «Что ты видел?» (the button pressed: the window of the bones), `keep`"""
    R("function last_ember:spiders/reset"); time.sleep(2)
    R("function last_ember:spiders/gen/cocoon_open"); R("scoreboard players set #toivo le.sp 1"); R("data modify storage last_ember:spiders toivo set value 1")
    R("function last_ember:spiders/gen/toivo_thicket"); time.sleep(2)
    t = M["toivo_pts"]["thicket"]
    R("time set 6000"); R("gamemode adventure Cam"); R(f"tp Cam {t[0]} {t[1]} {t[2] + 2.0} 180 10"); time.sleep(4)
    R("scoreboard players enable Cam le.sptrig"); R("execute as Cam at @s run trigger le.sptrig set 1"); time.sleep(3)
    snap("seen", hud=True, keep=True)
    open(os.path.join(CL, "shot-request.txt"), "w").write("!sneak_off\n"); time.sleep(2)
    R("gamemode spectator Cam")

if __name__ == "__main__":
    main(sys.argv[1:])
