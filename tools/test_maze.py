#!/usr/bin/env python3
"""T-024 checks on the R1 world (tools/build/rebuild.sh): the Enchanted Maze. Clients Cam and Cam2 in the game.
  layout   every movable cell in each of its 3 variants: placed, probe reads it back, storage follows; maze/set, maze/status
  shuffle  rebuild of free cells (another variant), a cell with a player / an ash trail / a dropped key is skipped;
           2 players in 2 movable cells at once; the rustle comes 1 s before; the automatic shuffle 45 s
  stay     3 game minutes (tick rate x5) with players standing in two movable cells: those never change, the others do
  mobs     a mob standing where a hedge of the next variant goes ends up on a path (not inside leaves)
  gaze     a dead-end statue looked at for 1 s (<= 4 blocks, <= 20 deg) rebuilds the nearest movable cell; 20 s per statue, 5 s global;
           looking from the side or from 6 blocks does nothing
  heads    the head turns after the player (near, then away > 6), turns back 60 s after nobody is within 16
  key      Call before the key -> the sanctum; the key by right click (T-013 generation), the pedestal empty, the exit open,
           guards wake 1 s later (4, named, elite), all players > 32 -> stone, back in r10 -> wake again, a killed guard stays dead,
           Call after the key does not lead here, the key stands on its pedestal in the Circle of the Weepers
  bypass   Blink fails in the maze, chorus never carries a player more than 1 block, a pearl over a hedge stays in the corridor,
           above the barrier ceiling or on the dome -> bonfire 3
  zones    blocks cannot be broken (adventure in the zone), no monsters in the sanctum
  restart  variants, key, exit, guards survive a restart
  perf     tick with 2 players in the maze while 2 cells rebuild, client FPS (!fps)
Usage: python3 tools/test_maze.py [layout shuffle stay mobs gaze heads key bypass zones restart perf]"""
import importlib.util, json, math, os, re, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
R = rc.run
ok = bad = 0
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n, flush=True)
    else: bad += 1; print("  FAIL", n, e, flush=True)
M = json.load(open(os.path.join(ROOT, "server/build/r1/maze.json")))
G = M["G"]; Y = G + 1; CEIL = M["ceil"]
SX, SZ = -150, -430                                           # sanctum centre (block corner)
MOV = [tuple(c) for c in M["movable"]]                        # origins of the movable cells 1..6
def mz(n): return tc.score(n, "le.mz")
def passed(cmd): return "passed" in R(cmd)
def pos(sel):
    v = re.findall(r"(-?\d+\.?\d*)d", R(f"data get entity {sel} Pos")); return [float(x) for x in v] if len(v) == 3 else None
def wait(cond, t=10.0, step=0.3):
    t0 = time.time()
    while time.time() - t0 < t:
        if cond(): return True
        time.sleep(step)
    return cond()
def probe_k(k):
    R(f"execute in minecraft:overworld store result score #prt le.mz run function last_ember:maze/gen/probe_{k}"); return mz("#prt")
def free_spot(k):
    """a path cell of movable cell k that is a path in every variant: the inside end of one of its ports"""
    ox, oz = MOV[k - 1]
    for x, z in ((ox + 12, oz + 1), (ox + 22, oz + 12), (ox + 12, oz + 22), (ox + 1, oz + 12)):
        if walkable(x, Y, z): return x, z
    return None
def stage(p2=True):
    for p in ("Cam", "Cam2"):
        if not passed(f"execute if entity {p}[tag=le.cinit]"): tc.setc(1, 1, 0, p)
    R("difficulty peaceful"); R("weather clear 100000"); R("time set noon"); R("gamerule advance_time false")
    for p in ("Cam", "Cam2"):
        R(f"gamemode survival {p}"); R(f"effect give {p} minecraft:resistance infinite 4 true"); R(f"effect give {p} minecraft:saturation infinite 1 true")
    R("tp Cam -149.5 112 -364.5 180 0"); R("tp Cam2 -147.5 112 -364.5 180 0" if p2 else "gamemode spectator Cam2")
    R("forceload add -224 -504 -76 -356"); wait(lambda: all(passed(f"execute if loaded {x} {Y} {z}") for x, z in MOV), 30)
    R("kill @e[type=minecraft:item,x=-215,y=90,z=-495,dx=130,dy=50,dz=130]")
    R("scoreboard players set #shuf le.mz -100000")             # no automatic shuffle during the checks
    R("scoreboard players set #gcd le.mz 0")
def unstage(): R("forceload remove -224 -504 -76 -356"); R("scoreboard players set #shuf le.mz 0")
def state(): return [mz(f"#v{k}") for k in range(1, 7)]

def t_layout():
    print("[layout: 6 movable cells x 3 variants]"); stage()
    for k in range(1, 7):
        good = []
        for v in (1, 2, 3):
            R(f"function last_ember:maze/set {{cell:{k},var:{v}}}"); time.sleep(0.2)
            good.append(probe_k(k) == v and mz(f"#v{k}") == v and f"c{k}: {v}" in R("data get storage last_ember:maze v"))
        chk(f"cell {k}: variants 1..3 placed and read back (probe, score, storage)", all(good), good)
    R("function last_ember:maze/reset"); time.sleep(0.3)
    chk("maze/reset: all cells variant 1", state() == [1] * 6, state())
    # what stands follows the state: break the state on purpose, the sync of the second puts the template back
    R("scoreboard players set #v3 le.mz 2"); R("data modify storage last_ember:maze v.c3 set value 2")
    okk = wait(lambda: probe_k(3) == 2, 8)
    diag = "" if okk else "pv3 %s, busy %s, items %s" % (mz("#pv3"), (R("execute in minecraft:overworld store result score #b3 le.mz run function last_ember:maze/gen/busy_3"), mz("#b3"))[1],
                                                      R("execute as @e[type=minecraft:item,x=-188,y=109,z=-420,dx=27,dy=12,dz=27] run data get entity @s Item.id"))
    chk("sync each second: a state changed behind its back is placed", okk, diag)
    R("function last_ember:maze/reset"); unstage()

def t_shuffle():
    print("[shuffle: free cells rebuild, busy cells are skipped]"); stage(); R("function last_ember:maze/reset"); time.sleep(0.5)
    # Cam in cell 1, an ash trail entity in cell 2, a dropped key (item) in cell 3, Cam2 in cell 4; 5 and 6 free
    s = [free_spot(k) for k in range(1, 7)]
    R(f"tp Cam {s[0][0] + 0.5} {Y} {s[0][1] + 0.5}"); R(f"tp Cam2 {s[3][0] + 0.5} {Y} {s[3][1] + 0.5}")
    R(f"summon minecraft:interaction {s[1][0] + 0.5} {Y} {s[1][1] + 0.5} {{Tags:[\"le.ashclick\",\"le.mztest\"],width:1f,height:1f}}")
    R(f"summon minecraft:item {s[2][0] + 0.5} {Y} {s[2][1] + 0.5} {{Item:{{id:\"minecraft:ominous_trial_key\",count:1}},PickupDelay:32767,Age:-32768,Tags:[\"le.mztest\"]}}")
    time.sleep(1.0)
    rounds = 0; before = state(); changed = set()
    for _ in range(8):
        r0 = mz("#rebuilds") or 0; b = state()
        R("function last_ember:maze/shuffle"); t0 = time.time()
        pend = [k for k in range(1, 7) if (mz(f"#pv{k}") or 0) > 0]
        time.sleep(0.4); still = [k for k in pend if probe_k(k) == b[k - 1]]
        wait(lambda: (mz("#rebuilds") or 0) >= r0 + len(pend), 3); a = state(); rounds += 1
        for k in range(1, 7):
            if a[k - 1] != b[k - 1]: changed.add(k)
        if pend and not (1 <= len(pend) <= 2 and still == pend and all(a[k - 1] != b[k - 1] and probe_k(k) == a[k - 1] for k in pend)):
            chk("a round: 1..2 cells, rustle first (old variant stands 0.4 s after), then another variant", False, (pend, still, b, a)); break
    chk(f"{rounds} rounds: only the free cells 5 and 6 ever rebuild", changed and changed <= {5, 6}, (changed, before, state()))
    R("kill @e[tag=le.mztest]"); time.sleep(0.6)
    # nothing in 2 and 3 now: a few rounds reach them
    R("tp Cam -149.5 112 -364.5"); R("tp Cam2 -147.5 112 -364.5"); changed = set()
    for _ in range(10):
        b = state(); r0 = mz("#rebuilds") or 0; R("function last_ember:maze/shuffle"); time.sleep(1.6); a = state()
        changed |= {k for k in range(1, 7) if a[k - 1] != b[k - 1]}
    chk(f"all players outside: every cell can rebuild ({sorted(changed)})", len(changed) >= 5, changed)
    # a cell that becomes busy during the rustle is not rebuilt
    R("function last_ember:maze/reset"); time.sleep(0.4)
    for _ in range(10):
        R("function last_ember:maze/shuffle"); pend = [k for k in range(1, 7) if (mz(f"#pv{k}") or 0) > 0]
        if pend: break
    k = pend[0]; sp = free_spot(k); R(f"tp Cam {sp[0] + 0.5} {Y} {sp[1] + 0.5}"); time.sleep(1.5)
    chk(f"cell {k} became busy during the rustle: not rebuilt", probe_k(k) == 1 and mz(f"#v{k}") == 1, (probe_k(k), mz(f"#v{k}")))
    # 45 s auto shuffle with players inside
    R("tp Cam -149.5 112 -364.5"); R(f"tp Cam2 {s[0][0] + 0.5} {Y} {s[0][1] + 0.5}"); R("scoreboard players set #shuf le.mz 880"); r0 = mz("#rebuilds") or 0
    chk("automatic shuffle 45 s after (players inside)", wait(lambda: (mz("#rebuilds") or 0) > r0, 6), (r0, mz("#rebuilds")))
    R("function last_ember:maze/reset"); unstage()

def t_stay():
    print("[3 minutes in a movable cell (automatic shuffle, tick rate x5)]"); stage(); R("function last_ember:maze/reset"); time.sleep(0.5)
    a, b = free_spot(1), free_spot(4)
    R(f"tp Cam {a[0] + 0.5} {Y} {a[1] + 0.5}"); R(f"tp Cam2 {b[0] + 0.5} {Y} {b[1] + 0.5}"); R("scoreboard players set #shuf le.mz 0")
    hist = {k: set() for k in range(1, 7)}; r0 = mz("#rebuilds") or 0
    R("tick rate 100"); t0 = time.time()
    try:
        while time.time() - t0 < 36.5:
            for k, v in enumerate(state(), 1): hist[k].add(v)
            time.sleep(0.5)
    finally: R("tick rate 20")
    n = (mz("#rebuilds") or 0) - r0
    chk(f"3 game minutes, players stand in cells 1 and 4: those never change, the others do ({n} rebuilds)",
        hist[1] == {1} and hist[4] == {1} and n >= 3 and any(len(hist[k]) > 1 for k in (2, 3, 5, 6)), ({k: sorted(v) for k, v in hist.items()}, n))
    R("function last_ember:maze/reset"); unstage()

def walkable(x, y, z):
    """feet and head free (flowers, moss carpet count as free), something under the feet"""
    solid = ("#minecraft:leaves", "minecraft:mossy_cobblestone", "minecraft:mossy_stone_bricks", "minecraft:calcite", "minecraft:polished_diorite",
             "#minecraft:stairs", "minecraft:barrier")
    c = " ".join(f"unless block {x} {y} {z} {b} unless block {x} {y + 1} {z} {b}" for b in solid)
    return passed(f"execute {c} unless block {x} {y - 1} {z} minecraft:air")
def t_mobs():
    print("[mobs on a rebuilt cell go to the path]"); stage(); R("difficulty easy"); R("function last_ember:maze/reset"); time.sleep(0.4)
    for k in (1, 5):
        ox, oz = MOV[k - 1]
        # path cells of variant 1 that are hedge in variant 2
        cand = []
        for lx in range(2, 22, 2):
            for lz in range(2, 22, 2):
                if walkable(ox + lx, Y, oz + lz): cand.append((ox + lx, oz + lz))
        R(f"function last_ember:maze/set {{cell:{k},var:2}}"); time.sleep(0.2)
        hit = [c for c in cand if not walkable(c[0], Y, c[1])][:6]
        R(f"function last_ember:maze/set {{cell:{k},var:1}}"); time.sleep(0.2)
        for i, (x, z) in enumerate(hit):
            R(f"summon minecraft:husk {x + 0.5} {Y} {z + 0.5} {{NoAI:1b,PersistenceRequired:1b,Silent:1b,Tags:[\"le.mztest\",\"le.keep\",\"le.mzm{i}\"]}}")
        time.sleep(0.3); R(f"function last_ember:maze/set {{cell:{k},var:2}}"); time.sleep(0.4)
        res = []
        for i in range(len(hit)):
            p = pos(f"@e[tag=le.mzm{i},limit=1]"); res.append(p is not None and walkable(math.floor(p[0]), round(p[1]), math.floor(p[2])))
        chk(f"cell {k}: {len(hit)} husks where the hedge of variant 2 grows: all on a path after the rebuild", hit and all(res), (hit, res, [pos(f"@e[tag=le.mzm{i},limit=1]") for i in range(len(hit))]))
        R("kill @e[tag=le.mztest]")
    R("function last_ember:maze/reset"); unstage()

def statue(sid): return [s for s in M["statues"] if s["id"] == sid][0]
DIRS = {"N": (0, -1), "S": (0, 1), "W": (-1, 0), "E": (1, 0)}
def stand_at(s, d=3, side=0.0):
    dx, dz = DIRS[s["exit"]]; return s["x"] + 0.5 + dx * d - dz * side, s["z"] + 0.5 + dz * d + dx * side
def look(p, s, d=3, side=0.0):
    x, z = stand_at(s, d, side); tc.face(p, round(x, 2), Y, round(z, 2), s["x"] + 0.5, Y + 2.5, s["z"] + 0.5)
def t_gaze():
    print("[the gaze of a dead-end statue]"); stage(False); R("function last_ember:maze/reset"); time.sleep(0.4)
    fixed = [s for s in M["statues"] if s["var"] is None and s["cell"] != [2, 2]]
    s1, s2 = fixed[0], fixed[5]
    for s in (s1, s2):
        if not walkable(int(math.floor(stand_at(s)[0])), Y, int(math.floor(stand_at(s)[1]))): print("     (statue", s["id"], "has no free stand 3 blocks out)")
    l0 = mz("#looks") or 0
    look("Cam", s1, 6); time.sleep(1.6); chk("from 6 blocks: nothing", (mz("#looks") or 0) == l0)
    x, z = stand_at(s1, 3); tc.face("Cam", round(x, 2), Y, round(z, 2), s1["x"] + 0.5 + 3 * DIRS[s1["exit"]][1], Y + 2.5, s1["z"] + 0.5 - 3 * DIRS[s1["exit"]][0])
    time.sleep(1.6); chk("3 blocks away looking 45 deg aside: nothing", (mz("#looks") or 0) == l0)
    k = s1["near"]; v0 = mz(f"#v{k}"); r0 = mz("#rebuilds") or 0
    look("Cam", s1, 3); time.sleep(0.6); chk("looked at for 0.5 s: not yet", (mz("#looks") or 0) == l0)
    time.sleep(1.0); chk(f"looked at for 1 s: statue {s1['id']} fires", (mz("#looks") or 0) == l0 + 1, (l0, mz("#looks"))); t1 = time.time()
    look("Cam", s2, 3); time.sleep(1.6); chk("another statue within 5 s: nothing (global cooldown)", (mz("#looks") or 0) == l0 + 1, mz("#looks"))
    chk(f"... and the nearest movable cell {k} rebuilt into another variant", wait(lambda: (mz("#rebuilds") or 0) > r0, 3) and mz(f"#v{k}") != v0 and probe_k(k) == mz(f"#v{k}"), (v0, mz(f"#v{k}")))
    look("Cam", s1, 3); time.sleep(2.0)
    chk("the same statue again within 20 s: nothing", (mz("#looks") or 0) == l0 + 1, mz("#looks"))
    time.sleep(max(0, 5.5 - (time.time() - t1))); look("Cam", s2, 2.5, 0.2); time.sleep(0.2); look("Cam", s2, 3); time.sleep(1.8)
    chk("another statue after 5 s: fires", (mz("#looks") or 0) == l0 + 2, mz("#looks"))
    R("function last_ember:maze/reset"); unstage()

def head_turned(s): return mz(f"#h{s['id']}") == 1
def t_heads():
    print("[the head of a dead-end statue]"); stage(False); R("function last_ember:maze/reset"); R("function last_ember:maze/heads_reset"); time.sleep(0.4)
    s = [q for q in M["statues"] if q["var"] is None][3]
    look("Cam", s, 2); time.sleep(1.0); chk("a player passes by: the head is still straight", not head_turned(s))
    face_rest = {"N": "east", "E": "south", "S": "west", "W": "north"}[{"N": "S", "S": "N", "E": "W", "W": "E"}[s["exit"]]]
    face_follow = {"N": "south", "S": "north", "E": "west", "W": "east"}[s["exit"]]
    chk("the head at rest: turned aside (in profile from the way out)", passed(f"execute if block {s['x']} {Y + 2} {s['z']} minecraft:polished_diorite_stairs[facing={face_rest}]"))
    x, z = stand_at(s, 9); R(f"tp Cam {x:.2f} {Y} {z:.2f}"); time.sleep(1.6)
    chk("the player went away (> 6): the head turns after", head_turned(s) and passed(f"execute if block {s['x']} {Y + 2} {s['z']} minecraft:tuff_stairs[facing={face_follow}]"), mz(f"#h{s['id']}"))
    R("tp Cam -149.5 112 -364.5"); R("tick sprint 1250"); time.sleep(4)
    chk("60 s with nobody within 16: straight again", wait(lambda: not head_turned(s), 6), mz(f"#h{s['id']}"))
    unstage()

def call_target():
    R("scoreboard players set #cur le.alt 1"); R("execute as Cam at @s run function last_ember:altar/gen/call_target"); return tc.score("#tx", "le.alt"), tc.score("#tz", "le.alt")
def guards(): R("execute store result score #ng le.mz if entity @e[type=minecraft:zombie,tag=le.mzguard]"); return mz("#ng")
def gstate(): return [mz(f"#g_{n}") for n in "nesw"]
def t_key():
    print("[the Thread of the Labyrinth, the exit, the guards]"); stage(); R("difficulty easy")
    R("function last_ember:altar/reset {chapter:1}"); R("function last_ember:altar/set_chapters {n:0}")
    R("data modify storage last_ember:keys k.thread_labyrinth merge value {got:0b,st:0}"); R("clear Cam"); R("clear Cam2")
    R("function last_ember:maze/reset"); time.sleep(1.5)
    chk("before: the key on its pedestal, the exit closed, 4 statues", mz("#key") == 1 and mz("#exit") == 0 and gstate() == [0] * 4
        and passed("execute if entity @e[type=minecraft:interaction,tag=le.mzkey]") and not passed(f"execute if block -151 {G + 4} -466 minecraft:air"), (mz("#key"), mz("#exit"), gstate()))
    tx, tz = call_target(); chk("the Call before the key leads to the sanctum", tx is not None and abs(tx - SX) <= 1 and abs(tz - SZ) <= 1, (tx, tz))
    kx, ky, kz = M["key"]
    R(f"tp Cam {SX} {Y} {SZ + 3}"); R(f"tp Cam2 {SX + 2} {Y} {SZ + 4}"); time.sleep(0.5)
    tc.face("Cam", SX, Y, SZ + 2.6, SX, ky + 0.3, SZ); time.sleep(0.4); tc.act("Cam", "!use"); time.sleep(0.4)
    chk("right click: the key in the inventory (current generation), the pedestal empty", mz("#key") == 2 and passed("execute if items entity Cam container.* minecraft:ominous_trial_key[minecraft:custom_data~{le_key:\"thread_labyrinth\"}]")
        and not passed("execute if entity @e[tag=le.mzkey]"), mz("#key"))
    chk("the exit is open", wait(lambda: passed(f"execute if block -151 {G + 4} -466 minecraft:air"), 2), mz("#exit"))
    chk("1 s later: 4 guards awake", wait(lambda: guards() == 4, 3), (guards(), gstate()))
    dt = (mz("#glt") or 0) - (mz("#ktk") or 0); chk(f"... they came to life {dt} ticks after the key was taken (1 s of dust)", 18 <= dt <= 26, dt)
    nm = R("data get entity @e[type=minecraft:zombie,tag=le.mzg_n,limit=1] CustomName")
    sc = R("attribute @e[type=minecraft:zombie,tag=le.mzg_n,limit=1] minecraft:scale get")
    chk("named «Страж сада», the stats of an elite (scale 1.3)", "Страж сада" in nm and "1.3" in sc, (nm, sc))
    chk("the pedestals are empty", passed(f"execute if block -151 {Y + 2} -436 minecraft:air"))
    tx, tz = call_target(); chk("the Call after the key does not lead here", not (tx is not None and abs(tx - SX) <= 1 and abs(tz - SZ) <= 1), (tx, tz))
    R("tp Cam -149.5 112 -364.5"); R("tp Cam2 -147.5 112 -364.5")
    chk("all players > 32 from the sanctum: the guards are stone again", wait(lambda: guards() == 0 and gstate() == [0] * 4, 4), (guards(), gstate()))
    chk("... the statues stand on their pedestals", passed(f"execute unless block -151 {Y + 2} -436 minecraft:air"))
    R(f"tp Cam {SX} {Y} {SZ + 9}"); time.sleep(0.3)
    chk("back in the sanctum (r 10): they wake again", wait(lambda: guards() == 4, 4), guards())
    R("kill @e[type=minecraft:zombie,tag=le.mzg_n]"); time.sleep(1.5)
    chk("a killed guard is marked killed", mz("#g_n") == 2, gstate())
    R("tp Cam -149.5 112 -364.5"); R("tp Cam2 -147.5 112 -364.5"); wait(lambda: guards() == 0, 4)
    R(f"tp Cam {SX} {Y} {SZ + 9}"); wait(lambda: guards() == 3, 4); time.sleep(1.0)
    chk("the killed one stays dead, the other three wake", guards() == 3 and not passed("execute if entity @e[tag=le.mzg_n]") and mz("#g_n") == 2, (guards(), gstate()))
    chk("the empty pedestal of the killed guard", passed(f"execute if block -151 {Y + 2} -436 minecraft:air"))
    R("tp Cam -149.5 112 -364.5"); R("tp Cam2 -147.5 112 -364.5"); wait(lambda: guards() == 0, 4)
    # the key taken from the pedestal goes to the Circle of the Weepers and stands on its pedestal
    src = open(os.path.join(ROOT, "tools/test_weepers.py")).read(); src = src[:src.index("T = {")]
    g = {"__file__": os.path.join(ROOT, "tools/test_weepers.py"), "__name__": "tw"}; exec(src, g)
    slot = re.search(r"Slot: (\d+)b[^}]*?le_key: \"thread_labyrinth\"", R("data get entity Cam Inventory"))
    if slot and int(slot.group(1)) != 0: R(f"item replace entity Cam hotbar.0 from entity Cam container.{slot.group(1)}"); R(f"item replace entity Cam container.{slot.group(1)} with minecraft:air")
    R("tp Cam -416.5 111 -185.5"); wait(lambda: passed("execute if loaded -420 111 -180"), 15); time.sleep(2)
    f0 = g["filled"](); g["click"]("Cam", "thread_labyrinth"); time.sleep(0.5)
    chk("the key from the maze stands on its pedestal in the Circle", g["filled"]() == f0 + 1 and "filled: 1b" in R("data get storage last_ember:altars p"), (f0, g["filled"]()))
    g["click"]("Cam", "thread_labyrinth"); R("tp Cam -149.5 112 -357.5")
    unstage()

def t_bypass():
    print("[bypasses: Blink, chorus, the roof]"); stage(False); R("function last_ember:maze/reset")
    s = free_spot(1); ox, oz = MOV[0]
    tc.setc(1, 3, 6, "Cam"); R(f"tp Cam {s[0] + 0.5} {Y} {s[1] + 0.5}"); time.sleep(0.6)
    for k in range(1, 8): R(f"scoreboard players set Cam le.cd{k} 0")
    R("scoreboard players set Cam le.spsel 0"); p0 = pos("Cam"); R("execute as Cam at @s run function last_ember:seer/cast_2"); time.sleep(0.4); p1 = pos("Cam")
    chk("Blink in the maze: fails, no cooldown", p0 and p1 and math.dist(p0, p1) < 0.3 and (tc.score("Cam", "le.cd2") or 0) == 0, (p0, p1, tc.score("Cam", "le.cd2")))
    hops = back = 0
    for i in range(8):
        R(f"tp Cam {s[0] + 0.5} {Y} {s[1] + 0.5}"); R("clear Cam"); R("item replace entity Cam weapon.mainhand with minecraft:chorus_fruit 4"); time.sleep(0.4)
        a = pos("Cam"); tc.act("Cam", "!use_on"); time.sleep(2.0); tc.act("Cam", "!use_off"); time.sleep(0.6); b = pos("Cam")
        if math.dist(a, b) <= 1.2: back += 1
        if "count: 3" in R("data get entity Cam SelectedItem") or "count: 4" not in R("data get entity Cam SelectedItem"): hops += 1
    chk(f"chorus in the maze: {hops} of 8 fruits eaten, {back} of 8 end within 1 block of the eat point", hops >= 6 and back == 8, (back, hops))
    # an ender pearl thrown over a hedge: the barrier tube stops it, the player stays in the corridor
    tc.setc(1, 1, 0, "Cam"); far = 0
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        R(f"tp Cam {s[0] + 0.5} {Y} {s[1] + 0.5}"); time.sleep(0.4); a = pos("Cam")
        R(f'execute as Cam at @s anchored eyes run summon minecraft:ender_pearl ^ ^ ^ {{Motion:[{dx * 1.2}d,0.9d,{dz * 1.2}d],Tags:["le.mztest"]}}')
        R('execute as @e[type=minecraft:ender_pearl,tag=le.mztest] run data modify entity @s Owner set from entity Cam UUID'); time.sleep(2.5); b = pos("Cam")
        n = int(math.hypot(b[0] - a[0], b[2] - a[2]) * 2) + 1           # every block on the line a -> b is a path: no hedge crossed
        line = {(math.floor(a[0] + (b[0] - a[0]) * i / n), math.floor(a[2] + (b[2] - a[2]) * i / n)) for i in range(n + 1)}
        hedge = [(x, z) for x, z in line if passed(f"execute if block {x} {Y + 2} {z} #minecraft:leaves")]    # a hedge crossed (a statue's shoulder is not one)
        if b[1] > G + 7.5 or hedge: far += 1; print("     pearl", (dx, dz), a, b, hedge)
        else: print("     pearl", (dx, dz), "landed %.1f blocks away along the corridor" % math.hypot(b[0] - a[0], b[2] - a[2]))
        R("kill @e[type=minecraft:ender_pearl]")
    chk("ender pearls thrown over the hedges (4 directions): never over a hedge, never on top", far == 0, far)
    R("clear Cam"); R(f"tp Cam {ox + 12 + 0.5} {CEIL + 2} {oz + 12 + 0.5}"); time.sleep(0.8); p = pos("Cam")
    chk("on the barrier ceiling: sent to bonfire 3", p and abs(p[2] - (-357.5)) < 2 and abs(p[0] + 149.5) < 2, p)
    R(f"tp Cam {SX} {G + 16} {SZ}"); time.sleep(0.8); p = pos("Cam")
    chk("on the dome: sent to bonfire 3", p and abs(p[2] - (-357.5)) < 2, p)
    R(f"tp Cam {SX + 5} {G + 8} {SZ}"); time.sleep(0.8); p = pos("Cam")
    chk("inside the dome (on the ring of the rotunda): stays", p and abs(p[2] - SZ) < 1, p)
    tc.setc(1, 1, 0, "Cam"); unstage()

def t_zones():
    print("[zones]"); stage(False); s = free_spot(1)
    R(f"tp Cam {s[0] + 0.5} {Y} {s[1] + 0.5}"); time.sleep(1.0)
    chk("in the maze: adventure (blocks cannot be broken)", passed("execute if entity @a[name=Cam,gamemode=adventure]"))
    chk("zone flags: no_blink, no_chorus", passed("execute if entity @a[name=Cam,tag=le.zf.no_blink,tag=le.zf.no_chorus]"))
    # the terrace (zone maze_terrace): the band on top by the parapet, and the foot of the north retaining wall
    R("tp Cam -215.5 112 -430.5"); time.sleep(1.0)
    chk("on the band of the terrace by the parapet: adventure (the parapet cannot be broken)", passed("execute if entity @a[name=Cam,gamemode=adventure]"))
    fy = next((y + 1 for y in range(108, 40, -1) if not passed(f"execute if block -150 {y} -501 minecraft:air") and not passed(f"execute if block -150 {y} -501 minecraft:water")), None)
    R(f"tp Cam -149.5 {fy} -500.5"); time.sleep(1.0)
    chk(f"at the foot of the north retaining wall (y {fy}): adventure (the wall cannot be broken)", fy and passed("execute if entity @a[name=Cam,gamemode=adventure]"), fy)
    R("difficulty normal"); R(f"tp Cam {SX + 0.5} {Y} {SZ - 10 + 0.5}"); time.sleep(1.0); R(f"summon minecraft:zombie {SX} {Y} {SZ + 6} {{Tags:[\"le.mztest\"],PersistenceRequired:1b}}"); time.sleep(2.0)
    chk("a monster in the sanctum is removed (sent down into the void)", wait(lambda: not passed("execute if entity @e[tag=le.mztest,y=100,dy=40]"), 3), R("data get entity @e[tag=le.mztest,limit=1] Pos"))
    R("kill @e[tag=le.mztest]"); R("difficulty peaceful"); R("tp Cam -149.5 140 -330.5"); time.sleep(1.5)
    chk("outside: survival again", passed("execute if entity @a[name=Cam,gamemode=survival]")); unstage()

def restart():
    subprocess.run([os.path.join(ROOT, "tools/server.sh"), "stop"], capture_output=True); time.sleep(8)
    subprocess.Popen(f"cd {ROOT} && tools/server.sh start > server/console.out 2>&1", shell=True)
    for _ in range(90):
        time.sleep(2)
        try:
            if "players online" in R("list"): break
        except Exception: pass
    subprocess.run("pkill -f net.minecraft.client.main.Main", shell=True); time.sleep(3)
    subprocess.Popen(f"cd {ROOT} && python3 -I tools/client_launch.py > server/client.out 2>&1", shell=True)
    subprocess.Popen(f"cd {ROOT} && python3 -I tools/client_launch.py --name Cam2 --dir server/client2 --mem 1500M --size 640x360 > server/client2.out 2>&1", shell=True)
    for _ in range(90):
        time.sleep(2)
        try:
            l = R("list")
            if "Cam2" in l and re.search(r"\bCam(?!2)\b", l): break
        except Exception: pass
    time.sleep(6)
def t_restart():
    print("[restart]"); stage()
    want = [2, 3, 1, 3, 2, 1]
    for k, v in enumerate(want, 1): R(f"function last_ember:maze/set {{cell:{k},var:{v}}}")
    key0, exit0, g0 = mz("#key"), mz("#exit"), gstate()
    restart(); stage()
    chk("after a restart: the variants are kept and stand", state() == want and all(probe_k(k) == v for k, v in enumerate(want, 1)), (state(), [probe_k(k) for k in range(1, 7)]))
    chk("after a restart: key, exit and guards as before", (mz("#key"), mz("#exit"), gstate()) == (key0, exit0, g0), ((key0, exit0, g0), (mz("#key"), mz("#exit"), gstate())))
    R("function last_ember:maze/reset"); unstage()

def mspt():
    m = re.search(r"([0-9.]+)\s*ms", R("tick query")); return float(m.group(1)) if m else None
def fps(p="Cam"):
    d = os.path.join(ROOT, tc.DIR[p]); v = []
    for _ in range(4):
        df = os.path.join(d, "shot-done.txt")
        if os.path.exists(df): os.remove(df)
        open(os.path.join(d, "shot-request.txt"), "w").write("!fps\n")
        for _ in range(60):
            if os.path.exists(df): break
            time.sleep(0.05)
        m = re.search(r"fps (\d+)", open(df).read()) if os.path.exists(df) else None
        if m: v.append(int(m.group(1)))
        time.sleep(0.5)
    return v
def prof(sec=10, during=None):
    """the profiler for sec seconds: ms per tick of the last_ember functions run from the schedule (as test_contracts.prof)"""
    import glob, zipfile, threading
    before = set(glob.glob(os.path.join(ROOT, "server/debug/profiling/*.zip"))); R("perf start")
    if during: during()
    time.sleep(sec + 1); R("perf stop"); new = []
    for _ in range(40):
        new = sorted(set(glob.glob(os.path.join(ROOT, "server/debug/profiling/*.zip"))) - before)
        if new: break
        time.sleep(0.5)
    if not new: return {}
    time.sleep(1.0); t = zipfile.ZipFile(new[-1]).read("server/profiling.txt").decode()
    span = float(re.search(r"Time span: (\d+) ms", t).group(1)); ticks = float(re.search(r"Tick span: (\d+) ticks", t).group(1))
    out = {"tick": span / ticks}
    for m in re.finditer(r"\[05\][ |]*function (last_ember:[a-z_/]+)\(\d+/\d+\) - [0-9.]+%/([0-9.]+)%", t): out[m.group(1)] = span * float(m.group(2)) / 100 / ticks
    return out
def t_perf():
    print("[perf]"); stage(); R("function last_ember:maze/reset")
    a, b = free_spot(1), free_spot(4)
    R(f"tp Cam {MOV[4][0] + 12 + 0.5} {Y} {MOV[4][1] - 2 + 0.5} 180 0")     # Cam looks at cell 5 from the cell north of it
    R(f"tp Cam2 {b[0] + 0.5} {Y} {b[1] + 0.5}"); time.sleep(20)
    idle = [mspt() for _ in range(4) if not time.sleep(1.5)]; f0 = fps()
    rb = []; fr = []
    for i in range(4):
        R("scoreboard players set #gcd le.mz 0"); R("function last_ember:maze/shuffle"); time.sleep(0.9)
        fr += fps(); rb.append(mspt()); time.sleep(2)
    after = [mspt() for _ in range(3) if not time.sleep(1.5)]
    p0 = prof(10)
    def shuffles():
        for i in range(3): R("function last_ember:maze/shuffle"); time.sleep(3)
    p1 = prof(10, shuffles)
    l0, l1 = p0.get("last_ember:maze/loop", 0), p1.get("last_ember:maze/loop", 0)
    print(f"     profiler: maze/loop {l0:.3f} ms per tick with 2 players inside, {l1:.3f} ms per tick over 10 s with 3 rebuild rounds (tick {p0.get('tick', 0):.1f} / {p1.get('tick', 0):.1f} ms)")
    chk("maze/loop with 2 players inside < 0.3 ms per tick, with rebuilds < 1 ms", l0 < 0.3 and l1 < 1.0, (l0, l1))
    print(f"     mspt (average of the last 100 ticks): idle {idle}, around rebuilds {rb}, after {after}; client fps idle {f0}, around rebuilds {fr}")
    chk("tick with 2 players in the maze under 15 ms (the whole server with 2 software-GL clients; the maze share is the profiler line)", max(x for x in idle if x) < 15, idle)
    chk("rebuilds keep the tick under 15 ms", max(x for x in rb if x) < 15, rb)
    chk("client fps around rebuilds within 30% of idle", fr and f0 and min(fr) >= 0.7 * (sum(f0) / len(f0)), (f0, fr))
    R("function last_ember:maze/reset"); unstage()

T = {"layout": t_layout, "shuffle": t_shuffle, "stay": t_stay, "mobs": t_mobs, "gaze": t_gaze, "heads": t_heads, "key": t_key, "bypass": t_bypass,
     "zones": t_zones, "restart": t_restart, "perf": t_perf}
for n in (sys.argv[1:] or ["layout", "shuffle", "stay", "mobs", "gaze", "heads", "key", "bypass", "zones"]): T[n]()
print(f"\n{ok} ok, {bad} failed")
