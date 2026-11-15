#!/usr/bin/env python3
"""T-024 frames of the Enchanted Maze (server + client Cam as the camera; Cam2 takes the key for the guard frames) -> docs/reports/T-024/*.jpg
Usage: python3 tools/build/maze_shots.py [outside inside cells heads key]   (default: all, in this order)
  outside  the gate from bonfire 3, the terrace from below (from the lake in the north, from the bay in the east), the maze from above (from outside the biome)
  inside   a corridor in the fog, the flowers of each quarter (m_flowers_ne|nw|sw|se), the sanctum with the key, the key close up
  cells    movable cell 1 in its three variants from above (camera 49 above the floor, lower the fog of the biome hides it; the frame is cropped to the cell)
  heads    a dead-end statue at eye level: from the front (3 blocks), the head at rest and following from 7 blocks
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
def shot_eye(name, e, t, settle=12):
    """like shot, the camera given by its eye (tp puts the feet 1.62 below)"""
    yaw, pitch = look(e, t); return dict(name=name, x=e[0], y=round(e[1] - 1.62, 2), z=e[2], yaw=yaw, pitch=pitch, settle=settle)
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

def _grid():
    """the walk grid (all movable cells in variant 1) and the flowers along the socle, from the generator itself"""
    sys.path.insert(0, os.path.join(ROOT, "tools/build")); import r1_maze as RM
    cells = RM.plan(); W = RM.walk_grid(cells, {c: 0 for c in RM.MOVABLE}); fl = {}
    for c, vs in cells.items():
        if c == (2, 2): continue
        ox, oz = RM.cell_origin(c)
        for (lx, ly, lz), st in RM.cell_blocks(c, vs[0]).items():
            if ly == 1 and any(f in st for f in ("poppy", "tulip", "lily_of", "cornflower", "orchid", "dandelion", "wildflowers")): fl[(ox + lx, oz + lz)] = st
    return RM, W, fl
DIRS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
def walk(RM, W, x, z): return RM.OX1 <= x <= RM.OX2 and RM.OZ1 <= z <= RM.OZ2 and W[z - RM.OZ1, x - RM.OX1]

def inside():
    RM, W, fl = _grid()
    # a corridor of each quarter: the straight run of 9 blocks with the most flowers along it, away from the sanctum
    fshots = []
    for q, name in (("NE", "red"), ("NW", "white"), ("SW", "blue"), ("SE", "yellow")):
        best = None
        for (x, z) in fl:
            if RM.quarter(x, z) != q or math.hypot(x - SX, z - SZ) < 26: continue
            for d, (dx, dz) in DIRS.items():
                run_ = [(x + dx * k, z + dz * k) for k in range(9)]
                if not all(walk(RM, W, *p) for p in run_) or any(RM.quarter(*p) != q for p in run_): continue
                n = sum((px + ox, pz + oz) in fl for px, pz in run_ for ox, oz in ((0, 0), (dz, dx), (-dz, -dx)))
                if not best or n > best[0]: best = (n, x, z, dx, dz)
        n, x, z, dx, dz = best; print("flowers", q, best)
        fshots.append(shot("m_flowers_%s" % q.lower(), (x + 0.5 - dx * 0.4, Y + 0.2, z + 0.5 - dz * 0.4), (x + 0.5 + dx * 7, Y - 0.6, z + 0.5 + dz * 7)))
    prep(); R("tp Cam -130 113 -400"); time.sleep(15)
    if "got: 1b" in R("data get storage last_ember:keys k.thread_labyrinth"):    # the key back on its pedestal for the frames (as in key())
        R("data modify storage last_ember:keys k.thread_labyrinth merge value {got:0b,st:0}"); R("clear Cam2"); R("clear Cam")
    R("function last_ember:maze/reset"); time.sleep(2)
    run([shot("m_corridor_fog", (-133.5, Y, -381.5), (-100, Y + 1.6, -381.5)),
         shot("m_sanctum_key", (-142.5, Y + 0.4, -423.5), (SX, Y + 1.8, SZ)),
         shot_eye("m_key_close", (SX + 0.35, 114.15, SZ + 1.6), (SX, 113.95, SZ))] + fshots, "noon", "_in"); done()

def cells():
    prep(); ox, oz = M["movable"][0]; cx, cz = ox + 12, oz + 12
    R(f"tp Cam {cx} 160 {cz}"); time.sleep(15)
    for v in (1, 2, 3):
        R(f"function last_ember:maze/set {{cell:1,var:{v}}}"); time.sleep(1)
        run([down(f"m_cell1_v{v}", cx, 160, cz, 6)], "noon", f"_c{v}", crop="400x400+440+160")
    R("function last_ember:maze/set {cell:1,var:1}"); done()

def heads():
    """a permanent dead-end statue with a straight way out of at least 8 blocks: from the front at 3 blocks (head at rest, in profile),
    and from 7 blocks (where the leaving player stands) at rest and turned after the player; camera at eye level"""
    RM, W, fl = _grid()
    for s in M["statues"]:
        if s["var"] is not None: continue
        dx, dz = DIRS[s["exit"]]; px, pz = abs(dz), abs(dx)          # across the dead end
        x, z = s["x"], s["z"]
        three = all(walk(RM, W, x + dx + k * px, z + dz + k * pz) for k in (-1, 0, 1)) and not walk(RM, W, x + dx + 2 * px, z + dz + 2 * pz) and not walk(RM, W, x + dx - 2 * px, z + dz - 2 * pz)
        if three and all(walk(RM, W, x + dx * k, z + dz * k) for k in range(1, 9)): break
    print("statue", s)
    head = (s["x"] + 0.5, Y + 2.4, s["z"] + 0.5)
    def at(d): return (s["x"] + 0.5 + dx * d, Y + 1.62, s["z"] + 0.5 + dz * d)
    prep(); R(f"tp Cam {at(5)[0]} {Y} {at(5)[2]}"); time.sleep(15)
    R(f"function last_ember:maze/gen/h/r{s['id']}")
    run([shot_eye("m_statue_front", at(3), head, 4), shot_eye("m_statue_head_straight", at(7), head, 4)], "noon", "_h1")
    R(f"function last_ember:maze/gen/h/t{s['id']}"); run([shot_eye("m_statue_head_follow", at(7), head, 4)], "noon", "_h2")
    R(f"function last_ember:maze/gen/h/r{s['id']}"); done()

def key():
    prep(); R("time set noon")
    R("data modify storage last_ember:keys k.thread_labyrinth merge value {got:0b,st:0}"); R("clear Cam2"); R("function last_ember:maze/reset")
    R("function last_ember:maze/gen/reset_guards"); R("difficulty easy")
    c = (-143.5, Y + 1.5, -423.5); yaw, pitch = look(c, (SX, Y + 1.5, SZ - 4))
    R("gamemode spectator Cam"); R(f"tp Cam {c[0]} {c[1]} {c[2]} {yaw} {pitch}"); time.sleep(15)
    R("gamemode survival Cam2"); R("effect give Cam2 minecraft:resistance infinite 4 true"); R(f"tp Cam2 {SX} {Y} {SZ + 3}"); time.sleep(2)
    tc.face("Cam2", SX, Y, SZ + 2.6, SX, M["key"][1] + 0.3, SZ); time.sleep(0.5); tc.act("Cam2", "!use"); time.sleep(0.35)
    tc.act("Cam", "m_guards_waking 0"); time.sleep(12)        # the chat line of the first screenshot fades out (~10 s); the guards stay awake
    tc.act("Cam", "m_guards_awake 0"); time.sleep(1.5)
    for n in ("m_guards_waking", "m_guards_awake"):
        src = os.path.join(ROOT, "server/client/screenshots", n + ".png")
        if os.path.exists(src): os.replace(src, os.path.join(TMP, n + ".png")); jpg(n)
    R("gamemode spectator Cam2"); R("tp Cam2 -149.5 140 -357.5"); time.sleep(3)
    run([shot("m_exit_open", (-150.5, Y + 0.2, -439.5), (-150.5, Y + 1.6, -480))], "noon", "_exit")
    R("difficulty peaceful"); done()

if __name__ == "__main__":
    for w in (sys.argv[1:] or ["outside", "inside", "cells", "heads", "key"]): globals()[w]()
    R("gamerule locator_bar true")
