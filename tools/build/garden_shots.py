#!/usr/bin/env python3
"""T-025 frames of the Garden of Silence (server + client Cam as the camera, Cam2 as the model in the Creaking armour) -> docs/reports/T-025/*.jpg
Usage: python3 tools/build/garden_shots.py [garden orangery hearts faces sensor house armour asleep]   (default: all, in this order)
  garden    the garden from the path at the house, by day and by night; the main alley to the orangery
  orangery  the orangery from outside (the great oak over the roof) and inside (the pedestal with the candles)
  hearts    a living heart by day and by night (awake)
  faces     a carved face by day (outward, eyes shut) and by night (turned, eyes open)
  sensor    a sensor with its bones and sign
  house     the gardener's house from outside (the armour in the window) and the stand inside
  armour    Cam2 in the full Creaking armour, front and back
  asleep    the garden asleep at night (eyeblossoms shut; the state is put back to awake afterwards)"""
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
def jpg(name):
    subprocess.run(["convert", os.path.join(TMP, name + ".png"), "-resize", "1600x", "-quality", "82", os.path.join(OUT, name + ".jpg")], check=True)
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
    run([shot_eye("g_orangery_out", (OCX + 46, FY + 14, OCZ + 26), (OCX, FY + 14, OCZ)),
         shot_eye("g_orangery_in", (M["orangery"][0] + 4.5, FY + 3.2, OCZ + 3), (M["pedestal"][0] + 0.5, FY + 1, M["pedestal"][2] + 0.5))], "noon", "_or")
    run([shot_eye("g_orangery_in_night", (M["orangery"][0] + 4.5, FY + 3.2, OCZ + 3), (M["pedestal"][0] + 0.5, FY + 1, M["pedestal"][2] + 0.5))], "midnight", "_orn")
def hearts():
    prep(); h = M["hearts"][1]; R(f"tp Cam {h['x']} {h['y'] + 30} {h['z']}"); time.sleep(12)
    e = heart_eye(h); t = (h["x"] + 0.5, h["y"] + 0.5, h["z"] + 0.5)
    run([shot_eye("g_heart_day", e, t, 6)], "noon", "_hd")
    run([shot_eye("g_heart_night", e, t, 8)], "midnight", "_hn")
def faces():
    prep(); f = M["faces"][0]; c = face_info(f); ox, oz = f["out"]
    e = (c[0] + ox * 7 + 0.3, c[1] + 0.3, c[2] + oz * 7 + 0.3)
    R(f"tp Cam {e[0]} {e[1] + 30} {e[2]}"); time.sleep(12)
    R("time set noon"); time.sleep(3)
    run([shot_eye("g_face_day", e, c, 4)], "noon", "_fd")
    # turn it in for the night shot while the camera is away (a watched face does not turn)
    R(f"tp Cam {c[0]} {c[1] + 60} {c[2]}"); R("time set midnight"); time.sleep(3)
    e2 = (c[0] - ox * 7 + 0.3, c[1] + 0.3, c[2] - oz * 7 + 0.3)          # the night face looks the other way: towards the orangery
    run([shot_eye("g_face_night", e2, c, 4)], "midnight", "_fn")
def sensor():
    prep(); s = [q for q in M["sensors"] if q["sign"]][1]
    R(f"tp Cam {s['x']} {s['y'] + 20} {s['z']}"); time.sleep(10)
    sx, sy, sz = s["sign"]
    e = (s["x"] + 0.5 + (s["x"] - sx) * 3 + 1.5, s["y"] + 3.0, s["z"] + 0.5 + (s["z"] - sz) * 3 + 1.5)
    run([shot_eye("g_sensor", e, (s["x"] + 0.5, s["y"] + 1, s["z"] + 0.5), 6)], "noon", "_s")
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
    R(f"tp Cam2 {x} {y} {z} 0 0"); time.sleep(2)
    run([shot_eye("g_armour_front", (x, y + 1.4, z + 3.2), (x, y + 1.0, z), 4)], "noon", "_af")
    R(f"tp Cam2 {x} {y} {z} 180 0"); time.sleep(1)
    run([shot_eye("g_armour_back", (x, y + 1.4, z + 3.2), (x, y + 1.0, z), 4)], "noon", "_ab")
    R("clear Cam2"); R("gamemode spectator Cam2")
def asleep():
    prep(); R("function last_ember:garden/sleep_now"); R("tp Cam2 300 120 -330"); R("time set midnight"); time.sleep(8)
    R("tp Cam 242 140 -262"); time.sleep(10)
    e = (242.5, 121 + 1.62 + 1.5, -263.5); t = (OCX, FY + 8, OCZ)
    b = M["blooms"][len(M["blooms"]) // 2]
    run([shot_eye("g_asleep_night", e, t), shot_eye("g_asleep_blooms", (b[0] + 3.5, b[1] + 2.2, b[2] + 3.5), (b[0] + 0.5, b[1] + 0.2, b[2] + 0.5), 6)], "midnight", "_as")
    R("function last_ember:garden/reset"); R("gamemode spectator Cam2")
T = dict(garden=garden, orangery=orangery, hearts=hearts, faces=faces, sensor=sensor, house=house, armour=armour, asleep=asleep)
for n in (sys.argv[1:] or list(T)): T[n]()
