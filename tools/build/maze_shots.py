#!/usr/bin/env python3
"""T-024 frames of the Enchanted Maze (server + client Cam as the camera; Cam2 takes the key for the guard frames) -> docs/reports/T-024/*.jpg
Usage: python3 tools/build/maze_shots.py [outside inside cells heads key]   (default: all, in this order)
  outside  the gate from bonfire 3, the terrace from below (from the lake in the north, from the bay in the east), the maze from above (from outside the biome)
  inside   a corridor in the fog, the flowers of the south-east quarter (yellow), the sanctum with the key
  cells    movable cell 1 in its three variants from above (camera 49 above the floor, lower the fog of the biome hides it; the frame is cropped to the cell)
  heads    a dead-end statue: the head straight and following
  key      Cam2 takes the key: the guards waking, the secret exit open (state reset to the key on its pedestal afterwards if nobody had it)"""
import importlib.util, json, math, os, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
R = rc.run
OUT = os.path.join(ROOT, "docs/reports/T-024"); TMP = os.path.join(ROOT, "server/build/r1/shots_m"); os.makedirs(TMP, exist_ok=True); os.makedirs(OUT, exist_ok=True)
M = json.load(open(os.path.join(ROOT, "server/build/r1/maze.json"))); G = M["G"]; Y = G + 1
SX, SZ = -150, -430
def look(c, t):
    dx, dy, dz = t[0] - c[0], t[1] - c[1], t[2] - c[2]
    return round(math.degrees(math.atan2(-dx, dz)), 1), round(-math.degrees(math.atan2(dy, math.hypot(dx, dz))), 1)
def shot(name, c, t, settle=12): yaw, pitch = look(c, t); return dict(name=name, x=c[0], y=c[1], z=c[2], yaw=yaw, pitch=pitch, settle=settle)
def down(name, x, y, z, settle=14): return dict(name=name, x=x, y=y, z=z, yaw=180, pitch=90, settle=settle)
def run(shots, time_="noon", tag="", crop=None):
    spec = os.path.join(TMP, f"shots{tag}.json"); json.dump({"time": time_, "weather": "clear", "shots": shots}, open(spec, "w"))
    subprocess.run([sys.executable, os.path.join(ROOT, "tools/screenshot.py"), spec, "--out", TMP, "--double"], check=True)
    for s in shots: jpg(s["name"], crop)
def jpg(name, crop=None):
    subprocess.run(["convert", os.path.join(TMP, name + ".png")] + (["-crop", crop, "+repage", "-filter", "point"] if crop else []) + ["-resize", "800x" if crop else "1600x", "-quality", "82", os.path.join(OUT, name + ".jpg")], check=True)
def prep():
    R("gamerule advance_time false"); R("gamerule locator_bar false"); R("difficulty peaceful"); R("gamemode spectator Cam2"); R("tp Cam2 -149.5 140 -357.5")
    R("scoreboard players set #shuf le.mz -100000")
def done(): R("scoreboard players set #shuf le.mz 0")
def ground(x, z, lo=40, hi=200):
    """the first non-air block from above (RCON probes): the y to stand on"""
    for y in range(hi, lo, -1):
        if "passed" not in R(f"execute if block {x} {y} {z} minecraft:air") and "passed" not in R(f"execute if block {x} {y} {z} minecraft:water"): return y + 1
    return lo
def water_y(x, z):
    for y in range(120, 30, -1):
        if "passed" in R(f"execute if block {x} {y} {z} minecraft:water"): return y + 1
    return None

def outside():
    prep(); R("tp Cam -150 140 -430"); time.sleep(20)
    run([shot("m_gate_from_bonfire3", (-149.5, Y + 0.6, -355.5), (-150, Y + 3, -370)),
         shot("m_from_above", (-150.5, 215, -305.5), (-150, G, -440), 25)], "noon", "_out")    # from outside the biome: its fog is the camera's
    # the terrace from below: from the water of the lake north of the place and of the bay east of it
    lake = next(((x, z, w) for z in range(-580, -620, -2) for x in (-150, -165, -135, -180, -120) if (w := water_y(x, z))), None)
    bay = next(((x, z, w) for x in range(-30, -6, 2) for z in (-430, -440, -420, -410, -450) if (w := water_y(x, z))), None)
    shots = []
    if lake: x, z, w = lake; shots.append(shot("m_terrace_from_lake", (x + 0.5, w + 6, z + 0.5), (-150, G - 22, -499)))
    else: shots.append(shot("m_terrace_from_lake", (-150.5, 90, -540.5), (-150, G - 18, -499)))
    if bay: x, z, w = bay; shots.append(shot("m_terrace_from_bay", (x + 0.5, w + 6, z + 0.5), (-86, G - 22, -430)))
    else: shots.append(shot("m_terrace_from_bay", (-55.5, 70, -430.5), (-82, G - 15, -430)))
    print("lake", lake, "bay", bay)
    run(shots, "noon", "_terrace"); done()

def inside():
    prep(); R("tp Cam -130 113 -400"); time.sleep(15)
    run([shot("m_corridor_fog", (-133.5, Y, -381.5), (-100, Y + 1.6, -381.5)),
         shot("m_flowers_se", (-128.5, Y + 0.4, -381.5), (-120, Y - 0.5, -383.5)),
         shot("m_sanctum_key", (-149.5, Y + 0.4, -420.5), (SX, Y + 2.2, SZ))], "noon", "_in"); done()

def cells():
    prep(); ox, oz = M["movable"][0]; cx, cz = ox + 12, oz + 12
    R(f"tp Cam {cx} 160 {cz}"); time.sleep(15)
    for v in (1, 2, 3):
        R(f"function last_ember:maze/set {{cell:1,var:{v}}}"); time.sleep(1)
        run([down(f"m_cell1_v{v}", cx, 160, cz, 6)], "noon", f"_c{v}", crop="400x400+440+160")
    R("function last_ember:maze/set {cell:1,var:1}"); done()

def heads():
    prep(); s = [q for q in M["statues"] if q["id"] == 67][0]
    cam = (s["x"] + 0.5, Y + 4.2, s["z"] + 0.5 - 4.5); head = (s["x"] + 0.5, Y + 2.3, s["z"] + 0.5)    # above and in front: the slope of the head stair shows
    R(f"tp Cam {cam[0]} {cam[1]} {cam[2]}"); time.sleep(15)
    R(f"function last_ember:maze/gen/h/r{s['id']}"); run([shot("m_statue_head_straight", cam, head, 4)], "noon", "_h1")
    R(f"function last_ember:maze/gen/h/t{s['id']}"); run([shot("m_statue_head_follow", cam, head, 4)], "noon", "_h2")
    R(f"function last_ember:maze/gen/h/r{s['id']}"); done()

def key():
    prep(); R("time set noon")
    R("data modify storage last_ember:keys k.thread_labyrinth merge value {got:0b,st:0}"); R("clear Cam2"); R("function last_ember:maze/reset")
    R("function last_ember:maze/gen/reset_guards"); R("difficulty easy")
    c = (-143.5, Y + 1.5, -423.5); yaw, pitch = look(c, (SX, Y + 1.5, SZ - 4))
    R("gamemode spectator Cam"); R(f"tp Cam {c[0]} {c[1]} {c[2]} {yaw} {pitch}"); time.sleep(15)
    R("gamemode survival Cam2"); R("effect give Cam2 minecraft:resistance infinite 4 true"); R(f"tp Cam2 {SX} {Y} {SZ + 3}"); time.sleep(2)
    tc.face("Cam2", SX, Y, SZ + 2.6, SX, M["key"][1] + 0.3, SZ); time.sleep(0.5); tc.act("Cam2", "!use"); time.sleep(0.35)
    tc.act("Cam", "m_guards_waking 0"); time.sleep(2.5); tc.act("Cam", "m_guards_awake 0"); time.sleep(1.5)
    for n in ("m_guards_waking", "m_guards_awake"):
        src = os.path.join(ROOT, "server/client/screenshots", n + ".png")
        if os.path.exists(src): os.replace(src, os.path.join(TMP, n + ".png")); jpg(n)
    R("gamemode spectator Cam2"); R("tp Cam2 -149.5 140 -357.5"); time.sleep(3)
    run([shot("m_exit_open", (-150.5, Y + 0.2, -439.5), (-150.5, Y + 1.6, -480))], "noon", "_exit")
    R("difficulty peaceful"); done()

if __name__ == "__main__":
    for w in (sys.argv[1:] or ["outside", "inside", "cells", "heads", "key"]): globals()[w]()
    R("gamerule locator_bar true")
