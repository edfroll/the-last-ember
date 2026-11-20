#!/usr/bin/env python3
"""T-027: the frames of the report (docs/reports/T-027/*.jpg, 1280 wide) from the dev client Cam (the server and Cam running):
the hollow from the gate by day and by night, the descent, the hill with the three swords, the field of swords, the chapel, a grave
(the epitaph close, the candle lit / the pit's unlit), a barrow outside and inside, the crypt's door, its corridor, the hall, the
Magister, a knight spirit, an evil spirit, the lodge outside (chimneys, lantern, stream), the room, the mansard, the shed with the
empty holder, the soul lights of the spyglass at night, the faded cemetery and lodge, the keeper's window, a cursed thing.
  python3 tools/build/cemetery_shots.py [name ...]"""
import importlib.util, json, math, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def load(n, path):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, path)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon", "tools/rcon.py"); tc = load("tc", "tools/test_class.py")
R = rc.run
OUT = os.path.join(ROOT, "docs/reports/T-027"); os.makedirs(OUT, exist_ok=True)
CL = os.path.join(ROOT, "server/client")
M = json.load(open(os.path.join(ROOT, "server/build/r1/cemetery.json")))
W = M["W"]; CR = M["crypt"]; LO = M["lodge"]; G = {g["n"]: g for g in M["graves"]}
sys.path.insert(0, os.path.join(ROOT, "tools/build")); import cemetery_plan as P
def yawpitch(f, t):
    dx, dy, dz = t[0] - f[0], t[1] - f[1], t[2] - f[2]
    return math.degrees(math.atan2(-dx, dz)), -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
def jpg(name):
    from PIL import Image
    src = os.path.join(CL, "screenshots", name + ".png")
    if os.path.exists(src): Image.open(src).convert("RGB").resize((1280, 720)).save(os.path.join(OUT, name + ".jpg"), quality=80)
def shot(name, f, t, hud=False, settle=6, keep=False, spectator=True):
    if spectator: R("gamemode spectator Cam")
    yw, pt = yawpitch((f[0], f[1] + 1.62, f[2]), t)
    R(f"tp Cam {f[0]} {f[1]} {f[2]} {yw:.1f} {pt:.1f}"); time.sleep(settle)
    for nm in (name + "__pre", name):
        d = os.path.join(CL, "shot-done.txt")
        if os.path.exists(d): os.remove(d)
        open(os.path.join(CL, "shot-request.txt"), "w").write(f"{nm} {1 if hud else 0}{' keep' if keep else ''}\n")
        for _ in range(120):
            if os.path.exists(d): break
            time.sleep(0.5)
        time.sleep(1.0 if nm == name else 11.0)
    jpg(name); print("  shot", name, flush=True)
def day(): R("time set noon")
def night(): R("time set midnight")
def setup():
    R("gamerule advance_time false"); R("gamerule locator_bar false"); R("weather clear 100000"); R("difficulty peaceful"); R("gamemode spectator Cam2"); R("tp Cam2 240 250 300")
    for c in ("forceload add 84 420 276 526", "forceload add 124 374 276 420"): R(c)
    time.sleep(3)
def gate():
    day(); shot("gate_day", (126.5, 193, 448.5), (190, 120, 470))
    night(); shot("gate_night", (126.5, 193, 448.5), (190, 120, 470)); day()
def descent():
    d = M["desc"]; a = d[40]; b = d[95]
    shot("descent", (a[0] + 6, a[2] + 8, a[1] - 10), (b[0], b[2], b[1]))
    shot("descent_top", (150, 200, 425), (130, 186, 448))
def hill():
    L = M["hill_level"]
    shot("hill", (215, L + 6, 470), (240, L + 14, 499))
    shot("hill_plate", (236.5, L + 1, P.HILL[1] + 4.5), (236.5, L + 1.8, P.HILL[1] + 1))
def swords():
    shot("swords", (205, 108, 455), (235, 100, 490))
def chapel():
    c = M["chapel"]; tx, ty, tz = c["tree"]
    shot("chapel", (tx + 16, ty + 6, tz - 10), (tx, ty + 4, tz))
def grave():
    g = G[2]
    shot("grave_epitaph", (g["x"] + 0.5, g["y"] + 1.3, g["z"] + 2.6), (g["x"] + 0.5, g["y"] + 2.4, g["z"]))
    p = G[15]; night()
    shot("grave_candles", (p["x"] + 4.5, p["y"] + 3, p["z"] + 6.5), (p["x"], p["y"] + 2, p["z"] - 1)); day()
def barrow():
    b = M["barrows"][0]; fx, fz = b["front"]; dx, dz = P.DIRS[b["facing"]]
    shot("barrow_out", (fx + dx * 9 + 3, b["E"] + 5, fz + dz * 9 + 3), (fx, b["E"] + 3, fz - dz * 4))
    ix, iz = b["inside"]
    R(f"execute positioned {ix} {b['E'] + 2} {iz} run summon minecraft:marker ~ ~ ~ {{Tags:[\"le.shotlight\"]}}")
    R(f"setblock {ix} {b['E'] + 3} {iz} minecraft:light[level=12]")
    shot("barrow_in", (b["door"][0] + 0.5, b["E"] + 1, b["door"][1] + 0.5), (ix + 0.5, b["E"] + 1.5, iz + 0.5))
    R(f"setblock {ix} {b['E'] + 3} {iz} minecraft:air"); R("kill @e[tag=le.shotlight]")
def crypt():
    d = CR["door"]
    shot("crypt_door", (d[0] + 0.5, d[1] + 2, d[2] + 11), (d[0] + 0.5, d[1] + 2, d[2]))
    R("scoreboard players set #door le.cem 1"); R("function last_ember:cemetery/gen/door_set")
    c0 = CR["corridor"]; lx = []
    for z in range(c0[2], c0[5] + 1, 4): R(f"setblock {d[0]} {CR['C'] + 3} {z} minecraft:light[level=10]"); lx.append(z)
    shot("crypt_corridor", (d[0] + 0.5, CR["C"] + 1, c0[5] + 0.5), (d[0] + 0.5, CR["C"] + 2, c0[2]))
    for z in lx: R(f"setblock {d[0]} {CR['C'] + 3} {z} minecraft:air")
    hx1, hy, hz1, hx2, _, hz2 = CR["hall"]
    shot("crypt_hall", (d[0] + 0.5, hy + 4, hz2 - 0.5), CR["sarc"])
def mobs():
    R("difficulty easy"); night()
    hx1, hy, hz1, hx2, _, hz2 = CR["hall"]; s = CR["sarc"]
    R("scoreboard players set #q le.cem 3"); R("scoreboard players set #door le.cem 1"); R("function last_ember:cemetery/save")
    R("gamemode survival Cam"); R(f"tp Cam {s[0] + 0.5} {hy + 1} {hz2 - 2.5}"); time.sleep(6)
    R("execute as @e[type=minecraft:skeleton,tag=le.cmag] run data merge entity @s {NoAI:1b}")
    shot("magister", (s[0] + 0.5, hy + 1, s[2] + 7.5), (s[0] + 0.5, hy + 2.5, s[2] + 0.5))
    R("function last_ember:cemetery/mag_leash"); R("scoreboard players set #q le.cem 0"); R("scoreboard players set #door le.cem 0"); R("function last_ember:cemetery/save")
    g = G[7]
    R(f"execute positioned {g['x'] + 4} {g['y'] + 1} {g['z']} run function last_ember:cemetery/spirit_knight")
    R(f"execute positioned {g['x'] - 3} {g['y'] + 1} {g['z'] + 2} run function last_ember:cemetery/spirit_vex")
    R("execute as @e[tag=le.cspirit] run data merge entity @s {NoAI:1b}")
    shot("spirits", (g["x"] + 0.5, g["y"] + 2, g["z"] + 9), (g["x"] + 0.5, g["y"] + 2, g["z"]))
    R("execute as @e[tag=le.cspirit] at @s run function last_ember:cemetery/spirit_gone"); R("difficulty peaceful"); day()
def lodge():
    hx, hy, hz = LO["centre"]
    shot("lodge_out", (122, 201, 432), (104, 199, 444))
    shot("lodge_stream", (117, 199, 437), (111, 196, 433))
    shot("lodge_room", (101.5, hy, 440.5), (109, hy + 0.5, 445))
    R(f"tp Cam {LO['lectern'][0] + 0.5} {LO['lectern'][1]} {LO['lectern'][2] - 2.5}")
    shot("lodge_attic", (LO["lectern"][0] + 0.5, LO["lectern"][1], LO["lectern"][2] - 3), (LO["lectern"][0] + 0.5, LO["lectern"][1] + 0.6, LO["lectern"][2] + 0.5))
    h = LO["holder"]; shot("lodge_shed", (h[0] - 3.5, h[1] - 1, h[2] + 0.5), (h[0] + 1, h[1], h[2] + 0.5))
def spyglass():
    night(); R("scoreboard players set #q le.cem 0")
    sp = LO["spyglass"]; R("gamemode survival Cam"); R(f"tp Cam {sp[0] - 0.5} {sp[1] - 1} {sp[2] + 0.5} -90 10"); time.sleep(2)
    R("execute store result score Cam le.cspy run time query gametime"); R("scoreboard players add Cam le.cspy 600")
    shot("spyglass_night", (sp[0] - 0.5, sp[1] - 1, sp[2] + 0.5), (200, 100, 470), spectator=False, settle=4)
    R("scoreboard players reset Cam le.cspy"); day()
def faded():
    R("function last_ember:region/gen/fade_r1"); time.sleep(6)
    shot("faded_cemetery", (215, M["hill_level"] + 6, 468), (237, M["hill_level"] + 2, 485))
    night(); shot("faded_lodge", (122, 201, 432), (104, 199, 444)); day()
    d = CR["door"]; shot("faded_keeper", (d[0] + 0.5, d[1] + 1, d[2] + 9), (d[0] + 0.5, d[1] + 1, d[2] + 2))
    R("function last_ember:region/gen/unfade_r1"); time.sleep(5)
def window():
    R("function last_ember:cemetery/reset"); R("gamemode survival Cam")
    k = M["dp"]["keeper_day"]; R(f"tp Cam {k[0] - 1.6} {k[1]} {k[2]}"); time.sleep(2)
    R(f"execute as Cam at @s anchored eyes run tp @s ~ ~ ~ facing {k[0]} {k[1] + 1.2} {k[2]}"); time.sleep(0.5)
    tc.act("Cam", "!use"); time.sleep(2.0)
    nm = "window_intro"
    d = os.path.join(CL, "shot-done.txt")
    if os.path.exists(d): os.remove(d)
    open(os.path.join(CL, "shot-request.txt"), "w").write(f"{nm} 1 keep\n")
    for _ in range(60):
        if os.path.exists(d): break
        time.sleep(0.5)
    time.sleep(1); jpg(nm); print("  shot", nm)
    tc.act("Cam", "!fps"); time.sleep(0.5)
def cursed():
    R("gamemode survival Cam"); R("clear Cam"); R("loot replace entity Cam hotbar.0 loot last_ember:cemetery/grave_1"); R("loot replace entity Cam hotbar.1 loot last_ember:cemetery/grave_3")
    R("tp Cam 118.5 192 450.5 0 10"); time.sleep(2)
    R("item replace entity Cam hotbar.2 with minecraft:stone"); R("item replace entity Cam hotbar.2 with minecraft:air")
    tc.act("Cam", "!swap"); time.sleep(0.3); tc.act("Cam", "!swap"); time.sleep(0.5)
    shot("cursed_item", (118.5, 192, 450.5), (118.5, 192.5, 460), hud=True, spectator=False, settle=1)
    R("clear Cam")
SHOTS = dict(gate=gate, descent=descent, hill=hill, swords=swords, chapel=chapel, grave=grave, barrow=barrow, crypt=crypt, mobs=mobs, lodge=lodge,
             spyglass=spyglass, faded=faded, window=window, cursed=cursed)
if __name__ == "__main__":
    setup()
    for n in sys.argv[1:] or list(SHOTS): SHOTS[n]()
    R("gamemode survival Cam2"); R("difficulty easy")
