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
    shot("barrow_out", (fx + dx * 10, b["E"] + 12, fz + dz * 10), (fx, b["E"] + 3, fz - dz * 5))
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
    R("difficulty easy"); day()
    hx1, hy, hz1, hx2, _, hz2 = CR["hall"]; sx, sy, sz = CR["sarc"]
    R("function last_ember:cemetery/gen/mag_summon"); time.sleep(1)
    R("execute as @e[type=minecraft:skeleton,tag=le.cmag] run data merge entity @s {NoAI:1b}")
    R(f"tp @e[type=minecraft:skeleton,tag=le.cmag] {sx + 0.5} {sy + 1} {sz + 4.5} 0 0")
    R(f"setblock {sx} {sy + 5} {sz + 6} minecraft:light[level=12]")
    shot("magister", (sx + 0.5, sy, sz + 9.5), (sx + 0.5, sy + 2.2, sz + 4.5))
    R(f"setblock {sx} {sy + 5} {sz + 6} minecraft:air"); R("function last_ember:cemetery/mag_leash"); R("difficulty peaceful")
def spirits():
    """a knight spirit and an evil spirit on the floor at night (review T-027: the old frame had the camera in the ground of a slope).
    The camera stands over the scanned ground (cemetery_post.bin) 9 south of them, Cam2 (a living player: spirits leave when only
    spectators are near) behind the camera, out of the frame"""
    import scanio
    sc = scanio.Scan(os.path.join(ROOT, "server/build/r1/cemetery_post.bin"))
    gnd = lambda x, z: int(sc.ground[z - sc.z0, x - sc.x0])
    R("difficulty easy"); night()
    g = G[2]; x, y, z = g["x"], g["y"] + 1, g["z"]
    cz = z + 10; cy = max(gnd(x + a, cz + d) for a in (-1, 0, 1) for d in (-1, 0, 1)) + 1
    R("gamemode survival Cam2"); R(f"tp Cam2 {x + 0.5} {gnd(x, cz + 6) + 1} {cz + 6.5}")
    R(f"execute positioned {x + 2.5} 0 {z + 4.5} positioned over motion_blocking_no_leaves run function last_ember:cemetery/spirit_knight")
    R(f"execute positioned {x - 1.5} 0 {z + 4.5} positioned over motion_blocking_no_leaves run function last_ember:cemetery/spirit_vex")
    R("execute as @e[tag=le.cspirit] run data merge entity @s {NoAI:1b}"); R("effect give @e[tag=le.cspirit] minecraft:fire_resistance infinite 0 true")
    R("execute as @e[tag=le.cspirit] at @s run tp @s ~ ~ ~ 180 0")
    shot("spirits", (x + 0.5, cy + 0.6, cz + 0.5), (x + 0.5, y + 1.2, z + 4.5), settle=8)
    R("gamemode spectator Cam2"); R("tp Cam2 240 250 300")
    R("execute as @e[tag=le.cspirit] at @s run function last_ember:cemetery/spirit_gone"); R("difficulty peaceful"); day()
def lodge():
    hx, hy, hz = LO["centre"]
    shot("lodge_out", (122, 201, 432), (104, 199, 444))
    # the falls between the steps of the stream (started by the datapack), along the stream from over the spring, and from the road: 193 -> 191
    shot("lodge_stream_a", (112.0, 200.5, 428.0), (112.0, 192.5, 438.5)); shot("lodge_stream_b", (115.5, 196.5, 441.5), (111.5, 192.5, 437.5))
    from PIL import Image
    sheet = Image.new("RGB", (1284, 362))
    for k, n in enumerate(("lodge_stream_a", "lodge_stream_b")):
        sheet.paste(Image.open(os.path.join(OUT, n + ".jpg")).resize((640, 360)), (k * 644, 1)); os.remove(os.path.join(OUT, n + ".jpg"))
    sheet.save(os.path.join(OUT, "lodge_stream.jpg"), quality=82)
    shot("lodge_room", (101.5, hy, 440.5), (109, hy + 0.5, 445))
    R(f"tp Cam {LO['lectern'][0] + 0.5} {LO['lectern'][1]} {LO['lectern'][2] - 2.5}")
    shot("lodge_attic", (LO["lectern"][0] + 0.5, LO["lectern"][1], LO["lectern"][2] - 3), (LO["lectern"][0] + 0.5, LO["lectern"][1] + 0.6, LO["lectern"][2] + 0.5))
    h = LO["holder"]; shot("lodge_shed", (h[0] - 3.5, h[1] - 1, h[2] + 0.5), (h[0] + 1, h[1], h[2] + 0.5))
def spyglass():
    night(); R("scoreboard players set #q le.cem 0")
    R("execute store result score Cam le.cspy run time query gametime"); R("scoreboard players add Cam le.cspy 6000")
    sp = M["spyglass"]; gs = [g for g in M["graves"] if g["kind"] in ("right", "thane")]
    shot("spyglass_floor", (210.5, 99, 474.5), (204.5, 110, 468.5), settle=5)        # over the floor: the columns over graves 1, 5 and Thane's
    # through the spyglass itself (held by the dev agent: !use_on) from the player's place on the pad by the post, at each of the six
    # columns (its top part: the hollow's humps and ridge hide the low part) -> spyglass_scope_<n>, montage spyglass_night
    R("gamemode survival Cam"); R("item replace entity Cam weapon.mainhand with minecraft:spyglass")
    se = M["spyglass_eye"]; eye = (se[0] + 0.5, se[1], se[2] + 0.5); names = []
    for g in gs:
        import cemetery_view as CV                       # aim at the middle of the part of the column seen from here
        if "G" not in CV.__dict__: CV.G = CV.grid(os.path.join(ROOT, "server/world"), (108, 436, 290, 530), M["W"] - 10, 200)
        vis = [y for y in range(g["y"] + 2, 141) if CV.seen(CV.G, (eye[0], eye[1] + 1.62, eye[2]), (g["x"] + 0.5, y, g["z"] + 0.5))]
        t = (g["x"] + 0.5, (min(vis) + 140) / 2 if vis else 134, g["z"] + 0.5)
        yw, pt = yawpitch((eye[0], eye[1] + 1.62, eye[2]), t)
        R(f"tp Cam {eye[0]} {eye[1]} {eye[2]} {yw:.1f} {pt:.1f}"); time.sleep(1); tc.act("Cam", "!use_on"); time.sleep(1)
        shot("spyglass_scope_%d" % g["n"], eye, t, spectator=False, settle=4); names.append("spyglass_scope_%d" % g["n"])
        tc.act("Cam", "!use_off"); time.sleep(0.5)
    R("clear Cam minecraft:spyglass")
    from PIL import Image
    sheet = Image.new("RGB", (3 * 644, 2 * 364))
    for k, n in enumerate(names): sheet.paste(Image.open(os.path.join(OUT, n + ".jpg")).resize((640, 360)), ((k % 3) * 644 + 2, (k // 3) * 364 + 2))
    sheet.save(os.path.join(OUT, "spyglass_night.jpg"), quality=82)
    for n in names: os.remove(os.path.join(OUT, n + ".jpg"))
    R("scoreboard players reset Cam le.cspy"); day()
def faded():
    R("function last_ember:region/gen/fade_r1"); time.sleep(6)
    shot("faded_cemetery", (215, M["hill_level"] + 6, 468), (237, M["hill_level"] + 2, 485))
    night(); shot("faded_lodge", (122, 201, 432), (104, 199, 444)); day()
    d = CR["door"]; shot("faded_keeper", (d[0] + 0.5, d[1] + 1, d[2] + 9), (d[0] + 0.5, d[1] + 1, d[2] + 2))
    R("function last_ember:region/gen/unfade_r1"); time.sleep(5)
def window():
    R("function last_ember:cemetery/reset"); R("gamemode survival Cam"); R("tp Cam 105.5 197 436.5"); time.sleep(4)
    tt = load("tt", "tools/test_cemetery.py")
    tt.talk("Cam"); time.sleep(1.5)
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
SHOTS = dict(gate=gate, descent=descent, hill=hill, swords=swords, chapel=chapel, grave=grave, barrow=barrow, crypt=crypt, mobs=mobs, spirits=spirits, lodge=lodge,
             spyglass=spyglass, faded=faded, window=window, cursed=cursed)
if __name__ == "__main__":
    setup()
    for n in sys.argv[1:] or list(SHOTS): SHOTS[n]()
    R("gamemode survival Cam2"); R("difficulty easy")
