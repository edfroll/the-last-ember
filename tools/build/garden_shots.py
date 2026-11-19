#!/usr/bin/env python3
"""T-025 frames of the Garden of Silence (server + client Cam as the camera, Cam2 as the model in the Creaking armour) -> docs/reports/T-025/*.jpg
Usage: python3 tools/build/garden_shots.py [garden orangery hearts faces sensor slope house armour asleep hud book]   (default: all, in this order)
  garden    the garden from the path at the house, by day and by night; the main alley to the orangery
  orangery  the orangery from outside (the great oak over the roof), from the path, inside (the pedestal), up to the vault, the hollow
  hearts    a living heart by day and by night (awake, 4 blocks)
  faces     a carved face by day from 4 and 8 (outward, eyes shut), by night from 8 (turned, eyes open), a trunk side from the alley
  sensor    a sensor with its bones and sign
  house     the gardener's house from outside (the armour in the window) and the stand inside
  armour    Cam2 in the full Creaking armour, front and back; the icons in the hotbar (enlarged)
  slope     the slope from the orangery up to the house (pale moss on the open sides)
  asleep    one point of the alley at night: the garden awake and asleep (eyeblossoms, faces; put back to awake afterwards)
  hud       the action bar: "hearts left" and "the garden fell asleep" (Cam in survival with the HUD)
  book      the gardener's notes open on the lectern, all 6 pages"""
import importlib.util, json, math, os, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
R = rc.run
OUT = os.path.join(ROOT, "docs/reports/T-025"); TMP = os.path.join(ROOT, "server/build/r1/shots_g"); os.makedirs(TMP, exist_ok=True); os.makedirs(OUT, exist_ok=True)
M = json.load(open(os.path.join(ROOT, "server/build/r1/garden.json")))
OCX, OCZ = (M["orangery"][0] + M["orangery"][2]) / 2 + 0.5, (M["orangery"][1] + M["orangery"][3]) / 2 + 0.5; FY = M["floor"]
def look(c, t):
    dx, dy, dz = t[0] - c[0], t[1] - c[1], t[2] - c[2]
    return round(math.degrees(math.atan2(-dx, dz)), 1), round(-math.degrees(math.atan2(dy, math.hypot(dx, dz))), 1)
def shot_eye(name, e, t, settle=12):
    yaw, pitch = look(e, t); return dict(name=name, x=e[0], y=round(e[1] - 1.62, 2), z=e[2], yaw=yaw, pitch=pitch, settle=settle)
def run(shots, time_="noon", tag=""):
    spec = os.path.join(TMP, f"shots{tag}.json"); json.dump({"time": time_, "weather": "clear", "shots": shots}, open(spec, "w"))
    subprocess.run([sys.executable, os.path.join(ROOT, "tools/screenshot.py"), spec, "--out", TMP, "--double"], check=True)
    for s in shots: jpg(s["name"])
def jpg(name, crop=None):
    pre = []
    if crop:      # (x, y, w, h) as fractions of the frame (the client window size may differ)
        W, H = (int(v) for v in subprocess.run(["identify", "-format", "%w %h", os.path.join(TMP, name + ".png")], capture_output=True, text=True).stdout.split())
        pre = ["-crop", "%dx%d+%d+%d" % (crop[2] * W, crop[3] * H, crop[0] * W, crop[1] * H), "+repage", "-filter", "point"]
    subprocess.run(["convert", os.path.join(TMP, name + ".png")] + pre + ["-resize", "1600x", "-quality", "82", os.path.join(OUT, name + ".jpg")], check=True)
def direct(name, hud=True, keep=False, clean=True, crop=None):
    """a frame of what Cam sees now (survival: the hotbar, an open book), through the agent directly; clean = without the chat lines"""
    tc.act("Cam", "%s %d%s%s" % (name, 1 if hud else 0, " keep" if keep else "", " clean" if clean else ""))
    for _ in range(100):
        if os.path.exists(os.path.join(ROOT, "server/client/screenshots", name + ".png")): break
        time.sleep(0.2)
    time.sleep(0.5); import shutil; shutil.copy(os.path.join(ROOT, "server/client/screenshots", name + ".png"), os.path.join(TMP, name + ".png")); jpg(name, crop)
def prep():
    R("gamerule advance_time false"); R("gamerule locator_bar false"); R("difficulty peaceful"); R("gamemode spectator Cam2"); R("tp Cam2 330 200 -350")
def heart_eye(h, d=5.0, up=0.6):
    """a point d blocks from heart h on the side with the most room (the camera eye), looking at the heart"""
    best = None
    for k in range(16):
        a = k * math.pi / 8; ex, ez = h["x"] + 0.5 + d * math.cos(a), h["z"] + 0.5 + d * math.sin(a)
        free = sum("passed" in R(f"execute if block {math.floor(h['x'] + 0.5 + t * math.cos(a))} {h['y']} {math.floor(h['z'] + 0.5 + t * math.sin(a))} #last_ember:garden_air") for t in (1.5, 2.5, 3.5, 4.5))
        if best is None or free > best[0]: best = (free, (ex, h["y"] + 0.5 + up, ez))
    return best[1]
def air(x, y, z): return "passed" in R(f"execute if block {math.floor(x)} {math.floor(y)} {math.floor(z)} #last_ember:garden_air")
def free_eye(t, dirs, dmax=8, dmin=3, up=0.5):
    """an eye point d (dmax..dmin) blocks from target t along one of the directions (in that order), up higher, with only air between"""
    for ox, oz in dirs:
        n = math.hypot(ox, oz); ox, oz = ox / n, oz / n
        for d in range(dmax, dmin - 1, -1):
            e = (t[0] + ox * d, t[1] + up, t[2] + oz * d)
            if all(air(t[0] + ox * k, t[1] + up * k / d, t[2] + oz * k) and air(t[0] + ox * k, t[1] + up * k / d + 1, t[2] + oz * k)
                   for k in [x * 0.5 for x in range(5, 2 * d + 1)]): return e      # from 2.5 out: past the trunk and the face itself
    return (t[0] + dirs[0][0] * dmin, t[1] + up, t[2] + dirs[0][1] * dmin)
ROUND = [(math.cos(k * math.pi / 8), math.sin(k * math.pi / 8)) for k in range(16)]
def face_info(f):
    import re
    txt = open(os.path.join(ROOT, f"datapack/data/last_ember/function/garden/gen/f/{f['id']}.mcfunction")).read()
    m = re.search(r"execute positioned (-?[\d.]+) (-?[\d.]+) (-?[\d.]+) as @a", txt); return tuple(float(v) for v in m.groups())

def garden():
    prep(); R("tp Cam 242 140 -262"); time.sleep(15)
    e = (242.5, 121 + 1.62 + 1.5, -263.5); t = (OCX, FY + 8, OCZ)
    run([shot_eye("g_path_house_day", e, t)], "noon", "_pd")
    run([shot_eye("g_path_house_night", e, t)], "midnight", "_pn")
    ent = M["entry"]; e2 = (ent[0] + 0.5, M["path"][min(range(len(M["path"])), key=lambda i: (M["path"][i][0] - ent[0]) ** 2 + (M["path"][i][1] - ent[1]) ** 2)][2] + 2.4, ent[1] + 0.5)
    run([shot_eye("g_alley", e2, (OCX, FY + 10, OCZ))], "noon", "_al")
def orangery():
    prep(); R(f"tp Cam {OCX} 150 {OCZ}"); time.sleep(15)
    run([shot_eye("g_orangery_out", (OCX + 52, FY + 34, OCZ + 40), (OCX, FY + 12, OCZ)),
         shot_eye("g_orangery_in", (M["orangery"][0] + 4.5, FY + 3.2, OCZ + 3), (M["pedestal"][0] + 0.5, FY + 1, M["pedestal"][2] + 0.5))], "noon", "_or")
    mid = (M["orangery"][0] + 8.5, FY + 1.62, OCZ + 4.0)
    run([shot_eye("g_orangery_up", mid, (OCX - 2, FY + 18, OCZ - 1)),
         shot_eye("g_orangery_vault", (M["orangery"][0] + 2.5, FY + 4.0, OCZ), (M["orangery"][2], FY + 15, OCZ))], "noon", "_ou")
    tx = M["trunk"][0]       # the hollow: 2x2 in the west face of the trunk, 4..5 over the floor
    run([shot_eye("g_tree_hollow", (tx - 4.0, FY + 5.2, -318.5), (tx, FY + 4.9, -321.0), 6)], "noon", "_th")
    P = M["path"]; i = min(range(len(P)), key=lambda k: abs(math.hypot(P[k][0] - OCX, P[k][1] - OCZ) - 45))
    run([shot_eye("g_tree_path", (P[i][0] + 0.5, P[i][2] + 1.62, P[i][1] + 0.5), (OCX, FY + 26, OCZ))], "noon", "_tp")
    run([shot_eye("g_orangery_in_night", (M["orangery"][0] + 4.5, FY + 3.2, OCZ + 3), (M["pedestal"][0] + 0.5, FY + 1, M["pedestal"][2] + 0.5))], "midnight", "_orn")
def hearts():
    prep(); h = M["hearts"][1]; R(f"tp Cam {h['x']} {h['y'] + 30} {h['z']}"); time.sleep(12)
    e = heart_eye(h, 4.0, 0.4); t = (h["x"] + 0.5, h["y"] + 0.5, h["z"] + 0.5)
    run([shot_eye("g_heart_day", e, t, 6)], "noon", "_hd")
    run([shot_eye("g_heart_night", e, t, 8)], "midnight", "_hn")
def faces():
    prep(); f = M["faces"][6]; c = face_info(f); ox, oz = f["out"]          # face 7 (by the orangery): open ground on both sides
    R(f"tp Cam {c[0]} {c[1] + 30} {c[2]}"); time.sleep(12)
    out = [(ox, oz), (ox + oz * 0.4, oz - ox * 0.4), (ox - oz * 0.4, oz + ox * 0.4)]
    R("time set noon"); time.sleep(3)
    run([shot_eye("g_face_day4", free_eye(c, out, 4, 4, 0.0), c, 4), shot_eye("g_face_day8", free_eye(c, out, 8, 7, 0.0), c, 4)], "noon", "_fd")
    # turn it in for the night shot while the camera is away (a watched face does not turn)
    R(f"tp Cam {c[0]} {c[1] + 60} {c[2]}"); R("time set midnight"); time.sleep(3)
    e2 = free_eye(c, [(-x, -z) for x, z in out], 8, 7, 0.0)     # the night face looks the other way: towards the orangery
    run([shot_eye("g_face_night", e2, c, 4)], "midnight", "_fn")
    R(f"tp Cam {c[0]} {c[1] + 60} {c[2]}"); R("time set noon"); time.sleep(3)
    # a face from the alley at its side: the trunk sides show bark only (no end rings)
    fa = [q for q in M["faces"] if q["kind"] == "alley"][0]; ca = face_info(fa); ax, az = fa["out"]
    side = [(az + ax * 0.5, -ax + az * 0.5), (-az + ax * 0.5, ax + az * 0.5)] + ROUND
    run([shot_eye("g_face_side", free_eye(ca, side, 7, 5, 0.3), ca, 6)], "noon", "_fs")
def sensor():
    prep(); s = [q for q in M["sensors"] if q["sign"]][1]
    R(f"tp Cam {s['x']} {s['y'] + 20} {s['z']}"); time.sleep(10)
    t = (s["x"] + 0.5, s["y"] + 1.0, s["z"] + 0.5); sx, sz = s["sign"][0], s["sign"][2]
    e = free_eye(t, [(s["x"] - sx + 0.6, s["z"] - sz + 0.6)] + ROUND, 7, 4, 2.6)
    run([shot_eye("g_sensor", e, (t[0] + (sx - s["x"]) * 0.4, t[1] + 0.6, t[2] + (sz - s["z"]) * 0.4), 6)], "noon", "_s")
def slope():
    prep(); R(f"tp Cam {OCX} 150 {OCZ}"); time.sleep(12)
    P = M["path"]; i = min(range(len(P)), key=lambda k: abs(math.hypot(P[k][0] - OCX, P[k][1] - OCZ) - 28))    # the path at the orangery's west side
    j = min(range(len(P)), key=lambda k: abs(math.hypot(P[k][0] - OCX, P[k][1] - OCZ) - 90))                  # up the slope, at the house
    e = (P[i][0] + 0.5, P[i][2] + 1.62 + 2.0, P[i][1] + 0.5); t = (P[j][0] + 0.5, P[j][2] + 1.0, P[j][1] + 0.5)
    run([shot_eye("g_slope", e, t, 8)], "noon", "_sl")
def house():
    prep(); R("tp Cam 242 140 -262"); time.sleep(12)
    wx, wy, wz = M["stand"]
    run([shot_eye("g_house_out", (wx + 0.5 - 2, 123.4, -263.0), (wx + 0.5, 122.5, -269.5), 6),
         shot_eye("g_house_stand", (240.5, 122.7, -273.0), (wx + 0.5, 122.0, wz + 0.5), 6)], "noon", "_h")
def armour():
    prep(); R("tp Cam 290 140 -300"); time.sleep(10)
    R("gamemode survival Cam2"); R("clear Cam2"); R("effect give Cam2 minecraft:resistance infinite 4 true")
    for sl, pc in (("head", "helmet"), ("chest", "chestplate"), ("legs", "leggings"), ("feet", "boots")):
        R(f"loot replace entity Cam2 armor.{sl} loot last_ember:item/creaking_{pc}")
    p = M["path"][70]; x, z, y = p[0] + 0.5, p[1] + 0.5, p[2]
    R(f"tp Cam2 {x} {y} {z}"); R("rotate Cam2 0 0"); time.sleep(2)
    run([shot_eye("g_armour_front", (x, y + 1.4, z + 3.2), (x, y + 1.0, z), 4)], "noon", "_af")
    R(f"tp Cam2 {x} {y} {z}"); R("rotate Cam2 180 0"); time.sleep(2)
    run([shot_eye("g_armour_back", (x, y + 1.4, z + 3.2), (x, y + 1.0, z), 4)], "noon", "_ab")
    # the icons in the hotbar of Cam (survival) looking at Cam2
    R("recipe give Cam *"); R("gamemode survival Cam"); R("clear Cam"); R(f"tp Cam {x} {y} {z + 3.2} 180 10")
    for k, pc in enumerate(("helmet", "chestplate", "leggings", "boots")): R(f"loot replace entity Cam hotbar.{k} loot last_ember:item/creaking_{pc}")
    R("item replace entity Cam hotbar.4 with minecraft:pale_oak_log"); R("item replace entity Cam hotbar.5 with minecraft:stripped_pale_oak_log")
    R("item replace entity Cam hotbar.6 with minecraft:leather_chestplate"); time.sleep(8)    # the recipe toast goes away
    direct("g_armour_icons", crop=(0.35, 0.925, 0.30, 0.075)); R("clear Cam"); R("gamemode spectator Cam")      # the hotbar only, enlarged
    R("clear Cam2"); R("gamemode spectator Cam2")
def alley_eye():
    P = M["path"]; i = min(range(len(P)), key=lambda k: abs(math.hypot(P[k][0] - OCX, P[k][1] - OCZ) - 40))
    return (P[i][0] + 0.5, P[i][2] + 1.62 + 0.6, P[i][1] + 0.5)
def asleep():
    prep(); e = alley_eye(); t = (OCX, FY + 6, OCZ)
    R(f"tp Cam {e[0]} {e[1] + 20} {e[2]}"); R("function last_ember:garden/reset"); R("time set midnight"); R("function last_ember:garden/gen/blooms_open"); time.sleep(12)
    run([shot_eye("g_alley_night_awake", e, t, 4)], "midnight", "_aw")
    R("function last_ember:garden/sleep_now"); R(f"tp Cam {e[0]} {e[1] + 40} {e[2]}"); time.sleep(8)     # away: the faces turn unwatched
    run([shot_eye("g_alley_night_asleep", e, t, 6)], "midnight", "_as")
    # a bunch of shut eyeblossoms in the open next to the path
    P = M["path"]
    def score(b):
        dp = min(math.hypot(b[0] - p[0], b[2] - p[1]) for p in P)
        return (dp > 5, -sum(1 for q in M["blooms"] if math.hypot(q[0] - b[0], q[2] - b[2]) < 5))
    b = min(M["blooms"], key=score); t = (b[0] + 0.5, b[1] + 0.2, b[2] + 0.5)
    R(f"tp Cam {t[0]} {t[1] + 20} {t[2]}"); time.sleep(8)
    e = free_eye(t, ROUND, 5, 3, 2.4)
    run([shot_eye("g_asleep_blooms", e, t, 6)], "midnight", "_asb")
    R("function last_ember:garden/reset"); R("gamemode spectator Cam2")
def hud():
    """the action bar after a heart is broken and after the last one (Cam in survival next to a heart)"""
    prep(); R("function last_ember:garden/reset"); R("time set noon")
    h = M["hearts"][0]; e = heart_eye(h, 4.0, 0.0)
    R("gamemode survival Cam"); R("effect give Cam minecraft:resistance infinite 4 true"); R(f"tp Cam {e[0]} {e[1] - 1.62 + 20} {e[2]}"); time.sleep(10)
    R(f"tp Cam {e[0]} {h['y']} {e[2]}"); R(f"execute as Cam at @s anchored eyes run tp @s ~ ~ ~ facing {h['x'] + 0.5} {h['y'] + 0.5} {h['z'] + 0.5}"); time.sleep(3)
    R(f"setblock {h['x']} {h['y']} {h['z']} minecraft:air destroy"); time.sleep(1.3)
    direct("g_hud_hearts_left"); time.sleep(12)        # the chat line "Saved screenshot" of this frame fades (10 s) before the next one
    for q in M["hearts"][1:]: R(f"forceload add {q['x']} {q['z']}"); R(f"setblock {q['x']} {q['y']} {q['z']} minecraft:air")
    time.sleep(2.0); direct("g_hud_asleep")
    for q in M["hearts"][1:]: R(f"forceload remove {q['x']} {q['z']}")
    R("function last_ember:garden/reset"); R("gamemode spectator Cam")
def book():
    prep(); lx, ly, lz = M["lectern"]
    R("gamemode survival Cam"); R(f"tp Cam {lx + 2.5} {ly} {lz + 0.5} 90 30"); time.sleep(8)
    R(f"execute as Cam at @s anchored eyes run tp @s ~ ~ ~ facing {lx + 0.5} {ly + 0.8} {lz + 0.5}"); time.sleep(1)
    for k in range(6):
        R(f"data modify block {lx} {ly} {lz} Page set value {k}")
        tc.act("Cam", "!use"); time.sleep(1.5)
        direct("g_book_p%d" % (k + 1), True, True)
    tc.act("Cam", "!fwd_off"); R("gamemode spectator Cam")
T = dict(garden=garden, orangery=orangery, hearts=hearts, faces=faces, sensor=sensor, slope=slope, house=house, armour=armour, asleep=asleep, hud=hud, book=book)
for n in (sys.argv[1:] or list(T)): T[n]()
