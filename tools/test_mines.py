#!/usr/bin/env python3
"""T-033 checks on the R1 world (world_cache.py redo mines): the Iron Ore Mines. Clients Cam and Cam2 in the game (real input through the
dev agent: walking (!fwd_on), sneaking, breaking blocks (!attack_on), the trade window (!trade_sel, !trade_take)). Difficulty easy.
  build    the yard (headframe, office with the 2 lecterns and the chest, the store, the spoil heap, the rails), the shaft (platforms,
           ladders), the three horizons, the inclines, 5 barrels with their loot, 3 sensors, the props, 4 carts; no ore in the box before
           the step; tools/build/mines_check.py on the saved world (ore, entities, walks, shaft)
  ore      the ore of the world by type and horizon as HQ T-033, 2 (mines_check); a coal, iron, copper and lapis ore mined by Cam with a
           pickaxe: the vanilla drop (coal, raw iron, raw copper, lapis)
  caves    Cam walks into cave-in 1: the warning (actionbar, dust), 2 s later it falls, Cam pushed out of the zone, hurt but not under 1
           heart (full health: damage <= 2 hearts; 3 hearts: kept over 1 heart); Cam breaks a block 6 from cave-in 2 while sneaking -> it
           falls; a zombie landing in cave-in 3 with no player within 10 -> the sensor active, no fall; a fallen cave-in never again
  sneak    Cam2 sneaks through cave-in 2: no fall
  bypass   with all three down: the bot's routes n_bypass round them (tools/build/mines_walk.sh bypass) and the BFS of mines_check
  shaft    the client Cam climbs the ladders of the shaft from H3 to the deck (<= 40 s); into the deck's opening: down to the next
           platform without damage; the highest fall between platforms <= 1.5 hearts
  dead     5 dead miners resting on their points (helmet, pickaxe, NoAI); Cam and Cam2 wake two at once; a hit wakes one; all beyond 32:
           back, full health, resting; a killed one is back 20 min of game time later with nobody within 48 (not at 10 min); a vanilla
           zombie in the workings gets the miner's helmet and a pickaxe, an elite does not
  cap      14 zombies at once in the workings: 10 stay
  carts    4 carts; one moved, Cam beyond 32: back, no doubles; a double goes; the cart from the top of the adit rolls down to H1
  bran     his knock is heard on H3 in front of the big collapse (counted); the crawl dug: he wakes for Cam; killed by Cam: his pickaxe, his
           letter, the trophy, bran 2; he does not come back
  peace    peaceful: no dead miners, no Bran, his pickaxe and letter lie in the pocket (Age -32768), bran 2; easy: the dead miners back
  smith    a real purchase at Halvard: Bran's letter -> «Шлем подмастерья»; a paper named otherwise is not taken; the second time the deal
           is used up
  zones    the headframe: adventure, its post stays; the yard and a drift: Cam breaks a block
  restart  after a restart: the cave-ins, Bran, the dead miners, the carts in their state, no doubles
  perf     two players on H3 in a fight, every dead miner awake: mines/* by the profiler
Usage: python3 tools/test_mines.py [build ore caves sneak bypass shaft dead cap carts bran peace zones smith restart perf]"""
import importlib.util, json, math, os, re, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
R = rc.run
ok = bad = 0
sys.path.insert(0, os.path.join(ROOT, "tools/build"))
M = json.load(open(os.path.join(ROOT, "server/build/r1/mines.json")))
LV = {int(k): v for k, v in M["levels"].items()}; Y = M["Y"]
PTS = M["points"]; DEAD = PTS["dead"]; BRAN = PTS["bran"]; CARTS = PTS["carts"]; CAVES = {c["n"]: c for c in M["caves"]}
B = {}
for line in open(os.path.join(ROOT, "server/build/r1/mines.txt")):
    x, y, z, s_ = line.split(" ", 3); B[(int(x), int(y), int(z))] = s_.strip()
YARD = (258.5, Y + 1, -65.5)          # the yard, west part (the loop runs; beyond 48 of the H3 points)
YARDW = (254.5, Y + 1, -72.5)
FAR = (300.5, LV[1] + 1, -42.5)       # H1, the south-east corner (beyond 32 of the yard's carts)

class tm:   # restart and profiler (tools/test_spiders.py)
    @staticmethod
    def relaunch(name):
        if name == "Cam": subprocess.Popen(f"cd {ROOT} && python3 -I tools/client_launch.py > server/client.out 2>&1", shell=True)
        else: subprocess.Popen(f"cd {ROOT} && python3 -I tools/client_launch.py --name Cam2 --dir server/client2 --mem 1500M --size 640x360 > server/client2.out 2>&1", shell=True)
    @staticmethod
    def restart():
        subprocess.run([os.path.join(ROOT, "tools/server.sh"), "stop"], capture_output=True); time.sleep(8)
        subprocess.Popen(f"cd {ROOT} && tools/server.sh start > server/console.out 2>&1", shell=True)
        for _ in range(90):
            time.sleep(2)
            try:
                if "players online" in R("list"): break
            except Exception: pass
        subprocess.run("pkill -f net.minecraft.client.main.Main", shell=True); time.sleep(3)
        tm.relaunch("Cam"); tm.relaunch("Cam2")
        for _ in range(90):
            time.sleep(2)
            try:
                l = R("list")
                if "Cam2" in l and re.search(r"\bCam(?!2)\b", l): break
            except Exception: pass
        time.sleep(6)
    @staticmethod
    def fresh():
        """the clients relaunched in the usual order (Cam, then Cam2: the focus stays with Cam2; a focused Cam turns by itself): after an
        hour of input the client Cam stops trading or breaking blocks"""
        subprocess.run("pkill -f net.minecraft.client.main.Main", shell=True); time.sleep(4)
        for name in ("Cam", "Cam2"):
            tm.relaunch(name)
            for _ in range(60):
                time.sleep(3)
                try:
                    l = R("list")
                    if (name == "Cam2" and "Cam2" in l) or (name == "Cam" and re.search(r"\bCam(?!2)\b", l)): break
                except Exception: pass
            time.sleep(6)
        time.sleep(25)                     # right after joining the clicks of a client miss (T-032): let it settle, one idle click each
        for name in ("Cam", "Cam2"): tc.act(name, "!sneak_off"); tc.act(name, "!use"); time.sleep(1)
    @staticmethod
    def prof(sec=10):
        import glob, zipfile
        before = set(glob.glob(os.path.join(ROOT, "server/debug/profiling/*.zip"))); R("perf start")
        time.sleep(sec + 1); R("perf stop"); new = []
        for _ in range(40):
            new = sorted(set(glob.glob(os.path.join(ROOT, "server/debug/profiling/*.zip"))) - before)
            if new: break
            time.sleep(0.5)
        if not new: return {}
        time.sleep(1.0); t = zipfile.ZipFile(new[-1]).read("server/profiling.txt").decode()
        span = float(re.search(r"Time span: (\d+) ms", t).group(1)); ticks = float(re.search(r"Tick span: (\d+) ticks", t).group(1))
        out = {"tick": span / ticks}
        for m in re.finditer(r"\[05\][ |]*function (last_ember:[a-z_/0-9]+)\(\d+/\d+\) - [0-9.]+%/([0-9.]+)%", t): out[m.group(1)] = span * float(m.group(2)) / 100 / ticks
        return out
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n, flush=True)
    else: bad += 1; print("  FAIL", n, e, flush=True)
def passed(cmd): return "passed" in R(cmd)
def pos(sel):
    v = re.findall(r"(-?\d+\.?\d*(?:E-?\d+)?)d", R(f"data get entity {sel} Pos")); return [float(x) for x in v] if len(v) == 3 else None
def wait(cond, t=10.0, step=0.3):
    t0 = time.time()
    while time.time() - t0 < t:
        if cond(): return True
        time.sleep(step)
    return cond()
def count(sel):
    m = re.search(r"Count: (\d+)", R(f"execute if entity {sel}")); return int(m.group(1)) if m else 0
def blk(x, y, z, b): return passed(f"execute if block {x} {y} {z} {b}")
def mn(k): return tc.score(k, "le.mn")
def nbt(sel, path): return R(f"data get entity {sel} {path}")
def stor(k): return tc.num(R(f"data get storage last_ember:mines {k}"), r"(-?\d+)$")
def tpp(p, x, y, z, yaw=0, pitch=0): R(f"tp {p} {x} {y} {z} {yaw} {pitch}")
def dsel(k): return f"@e[type=minecraft:zombie,tag=le.mn_{k},limit=1]"
BRAN_E = "@e[type=minecraft:zombie,tag=le.mn_bran,limit=1]"
def noai(sel): return "1b" in nbt(sel, "NoAI")
def at_point(k, d=0.8):
    p = pos(dsel(k)); return p is not None and math.dist(p, DEAD[k - 1][:3]) <= d
def hp(p): return tc.hp(p)
def stage(mode="survival", diff="easy", prot=True):
    for p in ("Cam", "Cam2"):
        if not passed(f"execute if entity @a[name={p},tag=le.cinit]"): tc.setc(1, 1, 0, p)
        R(f"gamemode {mode} {p}"); R(f"effect clear {p}")
        if prot: R(f"effect give {p} minecraft:resistance infinite 4 true"); R(f"effect give {p} minecraft:regeneration infinite 4 true")
        R(f"effect give {p} minecraft:saturation infinite 1 true"); R(f"effect give {p} minecraft:night_vision infinite 0 true")
        R(f"execute as {p} run function last_ember:sleep/set_awake {{ticks:0}}")
        tc.act(p, "!sneak_off"); tc.act(p, "!fwd_off"); tc.act(p, "!attack_off")
    R("weather clear 100000"); R("gamerule advance_time false"); R(f"difficulty {diff}"); R("time set 6000")
    tpp("Cam", *YARD); tpp("Cam2", *YARDW)
    wait(lambda: passed("execute if loaded 290 78 -45") and passed("execute if loaded 300 100 -80") and passed("execute if loaded 262 78 -72"), 30); time.sleep(1)
def base():
    R("function last_ember:mines/reset"); R("kill @e[type=minecraft:item]"); R("kill @e[type=#last_ember:monsters,tag=!le.mn_dead,tag=!le.mn_bran,x=240,y=60,z=-100,dx=80,dy=80,dz=80]"); time.sleep(2)
def walk(p, secs):
    tc.act(p, "!fwd_on"); time.sleep(secs); tc.act(p, "!fwd_off")
def mine(p, x, y, z, t=6.0):
    """real left click held on block (x, y, z) until it is gone"""
    tc.act(p, "!attack_on"); r = wait(lambda: blk(x, y, z, "#minecraft:air"), t, 0.1); tc.act(p, "!attack_off"); return r
def inv(p): return R(f"data get entity {p} Inventory")
def gametime(): return tc.num(R("time query gametime"), r"(\d+) tick")
def sprint(n):
    """n ticks at full speed (tick sprint), waited for by the game time"""
    g0 = gametime(); R("tick sprint %d" % n); wait(lambda: gametime() >= g0 + n, 300, 1)
def no_dead():
    """the dead miners away (their steps are heard by the sensors when a player is near: a woken one would make the cave-ins fall)"""
    R("execute as @e[type=minecraft:zombie,tag=le.mn_dead] run function last_ember:mines/vanish"); time.sleep(1)
def restore(cells, r=1):
    """the blocks of the step (mines.txt) back round the given cells (what a test mined or broke)"""
    done = set()
    for (x, y, z) in cells:
        for a in range(-r, r + 1):
            for b_ in range(-r, r + 1):
                for e in range(-r, r + 1):
                    q = (x + a, y + b_, z + e); s_ = B.get(q)
                    if s_ is None or q in done or "{" in s_: continue
                    done.add(q); R("setblock %d %d %d %s" % (q + (s_,)))
def restore_ore():
    """every ore block of the step in its place again (earlier runs of the tests mined some)"""
    for q, s_ in B.items():
        if s_.endswith("_ore"): R("setblock %d %d %d %s" % (q + (s_,)))
SNEAKING = '{type:"minecraft:entity_properties",entity:"this",predicate:{flags:{is_sneaking:true}}}'
def sneaking(p): return passed(f"execute as {p} if predicate {SNEAKING}")
def sneak(p):
    """sneak on and checked before a tp near a sensor (right after a tp the client makes a step: heard unless sneaking)"""
    for _ in range(3):
        tc.act(p, "!sneak_on"); time.sleep(0.8)
        if sneaking(p): return True
    return False

# ---------------------------------------------------------------- build
def t_build():
    print("[build]"); stage(); base(); restore_ore()
    x1, z1, x2, z2 = M["headframe"]
    chk("the headframe: 4 posts 20 high, the sheave's axle, chains to the deck", all(blk(x, Y + k, z, "minecraft:spruce_log") for x in (x1, x2) for z in (z1, z2) for k in (1, 10, 20))
        and blk(274, Y + 21, -72, "minecraft:spruce_log") and blk(274, Y + 10, -72, "minecraft:iron_chain"))
    of = M["office"]
    jb = R("data get block %d %d %d Book" % tuple(of["journal"])); nb = R("data get block %d %d %d Book" % tuple(of["note"]))
    chk("the office: the journal (4 pages, «Штейгер») and Bran's note («Бран») on lecterns, the chest with chests/r1/miner",
        "Журнал выработки" in jb and "Штейгер" in jb and "Первый горизонт" in jb and "Сегодня ушли все" in jb and "Бран" in nb and "Записка" in nb and "chests/r1/miner" in R("data get block %d %d %d LootTable" % tuple(of["chest"])), (jb[:120], nb[:80]))
    br = M["barrels"]
    chk("5 barrels: 2 chests/r1/miner (store, H1), 2 empty (H2, H3), the pocket chests/r1/common", len(br) == 5 and all(blk(*b_["pos"], "minecraft:barrel") and ((b_["loot"] or "~") in R("data get block %d %d %d LootTable" % tuple(b_["pos"])) if b_["loot"] else "LootTable" not in R("data get block %d %d %d" % tuple(b_["pos"]))) for b_ in br)
        and sum(1 for b_ in br if b_["loot"] == "last_ember:chests/r1/miner") == 2 and sum(1 for b_ in br if b_["loot"] is None) == 2)
    chk("3 sculk sensors 2 into the rock over the cave-ins", all(blk(*c["sensor"], "minecraft:sculk_sensor") and not blk(c["sensor"][0], c["sensor"][1] - 1, c["sensor"][2], "#minecraft:air") for c in CAVES.values()))
    pl = M["shaft_info"]["platforms"] if "shaft_info" in M else M["shaft"]["platforms"]
    chk("the shaft: platforms %s, ladders, exits on H1 H2 H3" % pl, all(blk(273, p, -72, "minecraft:spruce_planks") for p in pl[:-1]) and blk(274, LV[1] + 2, -71, "minecraft:air") and blk(274, LV[2] + 2, -71, "minecraft:air") and blk(274, LV[3] + 2, -69, "minecraft:air"))
    chk("the horizons: H1 (A1, A2, A3), H2 (B1, B2), H3 (D1 with the water, D2), the pocket - air at their middles",
        all(blk(x, LV[h] + 2, z, "minecraft:air") for (x, z, h) in ((299, -60, 1), (280, -41, 1), (265, -72, 1), (263, -65, 2), (300, -59, 2), (305, -50, 2), (270, -45, 3), (274, -55, 3), (264, -73, 3)))
        and blk(282, LV[3], -45, "minecraft:water") and blk(277, LV[3], -45, "minecraft:tuff_slab[waterlogged=true]"))
    chk("the adit 3 wide: stairs 2 lanes, the rail lane ascending; the inclines with stairs", blk(286, Y - 3, -65, "#minecraft:stairs") and blk(286, Y - 3, -66, "minecraft:rail[shape=ascending_west]")
        and blk(263, LV[1] - 3, -46, "#minecraft:stairs") and blk(301, LV[2] - 3, -45, "#minecraft:stairs"))
    chk("the props: the lunch (3), the pickaxe on the big collapse, the dead torch (5 item_display); 4 carts", count("@e[type=minecraft:item_display,tag=le.mnprop]") == 5 and count("@e[type=minecraft:minecart,tag=le.mn_cart]") == 4)
    import numpy as np
    d = np.load(os.path.join(ROOT, "server/build/r1/mines_under.npz"), allow_pickle=True)
    ores = sum(1 for n in d["name"] if str(n).endswith("_ore"))
    chk("no ore in the box of the place before the step (the world's blocks under it, first scan): %d" % ores, ores == 0)
    R("save-all flush"); time.sleep(4)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools/build/mines_check.py")], capture_output=True, text=True)
    print("   " + "\n   ".join(r.stdout.strip().split("\n")[-6:]))
    chk("mines_check.py on the saved world (ore, block entities, walks, the shaft)", r.returncode == 0, r.stdout[-400:])

# ---------------------------------------------------------------- ore
def ore_cell(kind, h, far_from_caves=12):
    """an ore block of the kind on horizon h at the feet row with a free drift cell beside it (far from the cave-ins' sensors)"""
    for (x, y, z), s_ in sorted(B.items()):
        if s_ != "minecraft:" + kind or y != LV[h] + 2: continue
        if any(math.dist((x, y, z), c["sensor"]) < far_from_caves for c in CAVES.values()): continue
        for (a, e) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if B.get((x + a, y, z + e)) == "minecraft:air" and B.get((x + a, y - 1, z + e)) == "minecraft:air" and B.get((x + a, y - 2, z + e)) not in (None, "minecraft:air"):
                return (x, y, z), (x + a + 0.5, y - 1, z + e + 0.5)
    return None, None
def t_ore():
    print("[ore]"); stage(); base(); restore_ore()
    R("save-all flush"); time.sleep(4)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools/build/mines_check.py")], capture_output=True, text=True)
    line = [l for l in r.stdout.split("\n") if l.startswith("ore found")]
    chk("the ore by type and horizon exactly as HQ T-033, 2 (box of the place + 32): %s" % (line[0][11:] if line else "?"), "FAIL ore" not in r.stdout and line)
    chk("every ore block in the walls of the workings, a face to their air", "no face" not in r.stdout and "outside the place" not in r.stdout)
    R("clear Cam"); R("give Cam minecraft:iron_pickaxe"); R("effect give Cam minecraft:haste 60 3 true")
    for kind, h, drop in (("coal_ore", 1, "minecraft:coal"), ("copper_ore", 1, "minecraft:raw_copper"), ("iron_ore", 3, "minecraft:raw_iron"), ("lapis_ore", 4, "minecraft:lapis_lazuli")):
        cell, stand = ore_cell(kind, h, 12 if h != 4 else 0)
        if cell is None: chk("an ore %s to mine on H%d" % (kind, h), False); continue
        R("clear Cam minecraft:coal"); R("clear Cam minecraft:raw_copper"); R("clear Cam minecraft:raw_iron"); R("clear Cam minecraft:lapis_lazuli")
        tc.face("Cam", stand[0], stand[1], stand[2], cell[0] + 0.5, cell[1] + 0.5, cell[2] + 0.5); time.sleep(1.0)
        tc.face("Cam", stand[0], stand[1], stand[2], cell[0] + 0.5, cell[1] + 0.5, cell[2] + 0.5); time.sleep(0.4)
        gone = mine("Cam", *cell)
        got = wait(lambda: drop in inv("Cam") or drop in R("execute as @e[type=minecraft:item,x=%d,y=%d,z=%d,distance=..3] run data get entity @s Item.id" % cell), 4)
        tc.act("Cam", "!attack_off")
        chk("Cam mines %s at %s with a pickaxe: the block gone, %s in his inventory (the vanilla drop)" % (kind, cell, drop), gone and got)
        R("kill @e[type=minecraft:item]"); restore([cell], 2)
    base()

# ---------------------------------------------------------------- caves
def cave_walk_in(p, n, back=4):
    """to `back` cells before the zone, sneaking (no step heard right after the tp), then standing up (silent)"""
    c = CAVES[n]; x1, z1, x2, z2 = c["rect"]; f = c["floor"]
    sneak(p)
    if c["axis"] == "x": tpp(p, x1 - back + 0.5, f + 1, (z1 + z2) // 2 + 0.5, -90, 10)
    else: tpp(p, (x1 + x2) // 2 + 0.5, f + 1, z1 - back + 0.5, 0, 10)
    time.sleep(1.5); tc.act(p, "!sneak_off"); time.sleep(0.5)
def in_zone(p, n):
    c = CAVES[n]; x1, z1, x2, z2 = c["rect"]; q = pos(p)
    return q and x1 <= q[0] < x2 + 1 and z1 <= q[2] < z2 + 1
def t_caves():
    print("[caves]"); stage(prot=False); base(); no_dead(); R("effect clear Cam")
    f0 = mn("#falls") or 0
    R("effect give Cam minecraft:instant_health 1 5 true"); time.sleep(0.5)
    cave_walk_in("Cam", 1, 5); time.sleep(1.5)
    h0 = hp("Cam"); cg = mn("#caught") or 0
    zx = CAVES[1]["rect"][0] + 1.5                  # walks in and stops in the zone (at 4.3 blocks/s he would be through it in 1.2 s: the 2 s
    tc.act("Cam", "!fwd_on"); wait(lambda: (pos("Cam") or [0])[0] >= zx, 4, 0.05); tc.act("Cam", "!fwd_off")   # of the warning are to run out)
    warned = wait(lambda: (mn("#w1") or 0) > 0 or mn("#c1") == 1, 3, 0.1)
    fell = wait(lambda: mn("#c1") == 1, 5, 0.2)
    time.sleep(0.6); h1 = hp("Cam"); q = pos("Cam"); e = CAVES[1]["ends"]
    inz = (mn("#caught") or 0) > cg
    chk("Cam walks into cave-in 1: the warning starts, it falls with him in the zone (caught: %s; #c1 1, storage caves.c1 1)" % inz, inz and warned and fell and stor("caves.c1") == 1)
    chk("Cam pushed out to an end of the zone (%s)" % q, q is not None and min(math.dist(q, x) for x in e) < 1.2 and not in_zone("Cam", 1))
    chk("Cam hurt, at most 2 hearts (%.1f -> %.1f)" % (h0 or -1, h1 or -1), h0 and h1 and 0 < h0 - h1 <= 4.01)
    x1, z1, x2, z2 = CAVES[1]["rect"]; f = CAVES[1]["floor"]
    chk("the zone closed by the template `after` (no air at the feet rows)", not any(blk(x, y, z, "minecraft:air") for x in range(x1, x2 + 1) for z in range(z1, z2 + 1) for y in (f + 1, f + 2)))
    # 3 hearts: kept above one heart (trap/shield)
    R("function last_ember:mines/gen/restore_3"); R("effect give Cam minecraft:instant_health 1 5 true"); time.sleep(2.5)
    tpp("Cam", 290.5, LV[3] + 1, -44.5, 90, 10); time.sleep(1)       # D1a east of the water: the dead miner's point nearby is fine
    R("damage Cam 14 minecraft:generic_kill"); time.sleep(0.5); h0 = hp("Cam")
    c = CAVES[3]; zx = (c["rect"][0] + c["rect"][2]) / 2 + 0.5
    tpp("Cam", zx, LV[3] + 1, -44.5, 90, 10); time.sleep(0.3)
    R("summon minecraft:zombie %.1f %d %.1f {Tags:[\"t33z\",\"le.keep\",\"le.rolled\",\"le.noelite\"],NoAI:1b,Silent:1b}" % (zx + 1, LV[3] + 3, -44.5))
    fell = wait(lambda: mn("#c3") == 1, 6, 0.2); time.sleep(0.6); h1 = hp("Cam")
    chk("cave-in 3 over Cam with 3 hearts: it falls, Cam over 1 heart (%.1f -> %.1f), slowness" % (h0 or -1, h1 or -1), fell and h0 <= 9.0 and h1 and h1 >= 2.0 and not in_zone("Cam", 3) and "slowness" in R("data get entity Cam active_effects"))
    R("kill @e[tag=t33z]")
    # cave-in 2: Cam sneaks 6 from the zone and breaks a block: the vibration -> it falls
    R("effect give Cam minecraft:instant_health 1 5 true"); R("give Cam minecraft:iron_pickaxe"); R("effect give Cam minecraft:haste 60 3 true")
    c = CAVES[2]; x1, z1, x2, z2 = c["rect"]; f = c["floor"]
    sneak("Cam")
    sx, sz = x1 + 0.5, z2 + 6 + 0.5                       # 6 south of the zone in B2d
    tpp("Cam", sx, f + 1, sz, 180, 0); time.sleep(3)
    quiet = mn("#c2") == 0 and (mn("#w2") or 0) == 0
    tx, ty, tz = x1 - 1, f + 2, z2 + 5                     # the wall block beside the drift, 5 from the zone
    if blk(tx, ty, tz, "#minecraft:air"): tx = x2 + 1
    tc.face("Cam", sx, f + 1, sz, tx + 0.5, ty + 0.5, tz + 0.5); time.sleep(0.8)
    gone = mine("Cam", tx, ty, tz)
    fell = wait(lambda: mn("#c2") == 1, 6, 0.2)
    tc.act("Cam", "!sneak_off")
    chk("Cam sneaking 6 from cave-in 2: no fall while still (%s); he breaks a wall block (%s): it falls" % (quiet, gone), quiet and gone and fell)
    restore([(tx, ty, tz)], 2)
    # a mob alone: the sensor hears it, nothing falls
    R("function last_ember:mines/gen/restore_3"); time.sleep(0.5)
    tpp("Cam", *YARD); time.sleep(1)
    c = CAVES[3]; zx = (c["rect"][0] + c["rect"][2]) / 2 + 0.5
    R("summon minecraft:zombie %.1f %d %.1f {Tags:[\"t33z\",\"le.keep\",\"le.rolled\",\"le.noelite\"],PersistenceRequired:1b}" % (zx, LV[3] + 3, -44.5))
    act = wait(lambda: blk(*c["sensor"], "minecraft:sculk_sensor[sculk_sensor_phase=active]"), 3, 0.1)
    time.sleep(4)
    chk("a zombie lands in cave-in 3, no player within 10: the sensor wakes (%s), nothing falls" % act, act and mn("#c3") == 0 and (mn("#w3") or 0) == 0)
    R("kill @e[tag=t33z]")
    # once a world: cave-in 1 down (storage 1); its template `before` and sensor put back by hand: Cam walks in -> nothing
    c = CAVES[1]
    R("place template last_ember:mines/cave_1_before %d %d %d" % tuple(c["origin"])); R("setblock %d %d %d minecraft:sculk_sensor" % tuple(c["sensor"]))
    f1 = mn("#falls")
    cave_walk_in("Cam", 1, 5); time.sleep(1); tc.act("Cam", "!fwd_on"); wait(lambda: (pos("Cam") or [0])[0] >= c["rect"][0] + 1.5, 4, 0.05); tc.act("Cam", "!fwd_off"); time.sleep(4)
    chk("a cave-in falls once a world: cave-in 1 (down) standing again by hand, Cam walks in: nothing (falls %d -> %d)" % (f1, mn("#falls")), mn("#falls") == f1 and mn("#c1") == 1)
    base()

def t_sneak():
    print("[sneak]"); stage(); base(); no_dead()
    c = CAVES[2]; x1, z1, x2, z2 = c["rect"]; f = c["floor"]
    sneak("Cam2")
    tpp("Cam2", x1 + 0.5, f + 1, z2 + 4 + 0.5, 180, 10); time.sleep(1.5)
    sn = sneaking("Cam2")
    walk("Cam2", 7.0)
    q = pos("Cam2"); time.sleep(3)
    tc.act("Cam2", "!sneak_off")
    chk("Cam2 sneaks (%s) through cave-in 2 (now at z %.1f, the zone z %d..%d): no warning, no fall" % (sn, q[2] if q else 99, z1, z2), sn and q and q[2] < z1 and mn("#c2") == 0 and (mn("#w2") or 0) == 0 and mn("#falls") is not None)
    base()

# ---------------------------------------------------------------- bypass
def t_bypass():
    print("[bypass]"); stage(); base()
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools/build/mines_check.py")], capture_output=True, text=True)
    ls = [l for l in r.stdout.split("\n") if "round cave-in" in l or "all three cave-ins down" in l]
    chk("BFS without jumps: round each cave-in and from the yard to the big collapse with all three down (%d lines)" % len(ls), len(ls) == 9 and all(l.endswith("OK") for l in ls), ls)
    r = subprocess.run(["bash", os.path.join(ROOT, "tools/build/mines_walk.sh"), "bypass"], capture_output=True, text=True)
    log = open(os.path.join(ROOT, "server/build/walk/mines_walk.log")).read()
    lines = [l for l in log.split("\n") if l.strip()]
    good = [l for l in lines if "RETRY" not in l and "PROBLEM" not in l] + [l for l in lines if "RETRY" in l and "PROBLEM" not in l]
    chk("the bot walks round all three cave-ins (down) without jumps: %s" % " | ".join(l[:60] for l in lines), lines and all(("PROBLEM" not in l) or any(("RETRY" in m and m.split()[0] == l.split()[0] and "PROBLEM" not in m) for m in lines) for l in lines if "RETRY" not in l))
    stage(); base()

# ---------------------------------------------------------------- dead miners
def t_dead():
    print("[dead]"); stage(); base(); time.sleep(2)
    n = count("@e[type=minecraft:zombie,tag=le.mn_dead]")
    helm = all("3877402" in nbt(dsel(k), "equipment.head") and "pickaxe" in nbt(dsel(k), "equipment.mainhand") for k in range(1, 6))
    chk("5 dead miners on their points, resting (NoAI), helmet and pickaxe (%d)" % n, n == 5 and all(at_point(k) and noai(dsel(k)) for k in range(1, 6)) and helm)
    k1, k2 = 1, 3
    for p, k in (("Cam", k1), ("Cam2", k2)):
        x, y, z = DEAD[k - 1][:3]; tpp(p, x + 3.0, y, z)
    both = wait(lambda: not noai(dsel(k1)) and not noai(dsel(k2)), 3)
    others = all(noai(dsel(k)) for k in (2, 4, 5))
    chk("Cam and Cam2 wake two at once (dead %d and %d), the others rest" % (k1, k2), both and others)
    tpp("Cam", *YARD); tpp("Cam2", *YARDW)
    x, y, z = DEAD[4][:3]; tpp("Cam", x + 10.5, y, z)
    time.sleep(1); R("damage %s 1 minecraft:player_attack by Cam" % dsel(5))
    chk("a hit by Cam from 10 wakes dead miner 5", wait(lambda: not noai(dsel(5)), 3))
    tpp("Cam", *YARD); tpp("Cam2", *YARDW)
    R("damage %s 4 minecraft:generic" % dsel(k1))
    back = wait(lambda: all(at_point(k) and noai(dsel(k)) for k in (k1, k2, 5)), 8)
    chk("all players beyond 32: the awake ones back on their points, resting, full health", back and tc.hp(dsel(k1)) >= 19.9)
    # a killed one: back 20 min of game time later with nobody within 48
    tpp("Cam", *YARDW); tpp("Cam2", *YARDW)
    k = 3; R("kill %s" % dsel(k)); time.sleep(5)
    chk("dead miner %d killed: marked (#d%d 1)" % (k, k), mn("#d%d" % k) == 1 and count("@e[type=minecraft:zombie,tag=le.mn_%d]" % k) == 0)
    sprint(12000); time.sleep(3)
    none = count("@e[type=minecraft:zombie,tag=le.mn_%d]" % k) == 0
    sprint(12100); wait(lambda: count("@e[type=minecraft:zombie,tag=le.mn_%d]" % k) == 1, 10, 1)
    chk("not back after 10 min of game time; back after 20 min with nobody within 48", none and count("@e[type=minecraft:zombie,tag=le.mn_%d]" % k) == 1 and at_point(k))
    # the helmets of the vanilla zombies of the workings, not of the elites
    R("kill @e[tag=t33v]")
    x, y, z = 270.5, LV[3] + 1, -44.5
    R('summon minecraft:zombie %.1f %d %.1f {Tags:["t33v","t33a","le.noelite"],PersistenceRequired:1b}' % (x, y, z))   # its elite roll (T-014) passes it by: not an elite
    R('summon minecraft:zombie %.1f %d %.1f {Tags:["t33v","t33e"],PersistenceRequired:1b}' % (x + 2, y, z))
    R("execute as @e[tag=t33e] at @s run function last_ember:elite/make")
    time.sleep(2.5)
    ha = nbt("@e[tag=t33a,limit=1]", "equipment"); he = nbt("@e[tag=t33e,limit=1]", "equipment")
    chk("a vanilla zombie in the workings: the miner's helmet and a pickaxe, drop 0; an elite keeps the helmet of its region", "3877402" in ha and "pickaxe" in ha and "3877402" not in he and "leather_helmet" in he, (ha[:150], he[:150]))
    R("kill @e[tag=t33v]")
    base()

def t_cap():
    print("[cap]"); stage(); base()
    R("kill @e[type=#last_ember:monsters,tag=!le.mn_dead,tag=!le.mn_bran,x=240,y=60,z=-100,dx=80,dy=80,dz=80]"); time.sleep(1)
    for i in range(14): R('summon minecraft:zombie %.1f %d %.1f {Tags:["t33c","le.noelite","le.rolled"],PersistenceRequired:1b,NoAI:1b}' % (279.5 - (i % 7), LV[1] + 1, -72.5 + (i // 7) * 0))
    time.sleep(2.5)
    n = count("@e[tag=t33c]") - count("@e[tag=t33c,x=0,y=-2000,z=0,dx=1000000,dy=1990,dz=1000000]") - count("@e[tag=t33c,x=-1000000,y=-2000,z=-1000000,dx=1000000,dy=1990,dz=1000000]")
    chk("14 zombies at once in the workings: %d stay (10), the others gone" % n, n == 10)
    R("kill @e[tag=t33c]")

# ---------------------------------------------------------------- carts
def cart(c): return f"@e[type=minecraft:minecart,tag=le.mnc{c},limit=1]"
def t_carts():
    print("[carts]"); stage(); base(); time.sleep(2)
    chk("4 carts at their places", all(count(f"@e[type=minecraft:minecart,tag=le.mnc{c}]") == 1 and math.dist(pos(cart(c)), CARTS[c - 1]) < 1 for c in range(1, 5)))
    tpp("Cam", CARTS[0][0] + 2, CARTS[0][1], CARTS[0][2])
    R("execute as %s at @s run tp @s ~4 ~ ~" % cart(1)); time.sleep(2)
    moved = math.dist(pos(cart(1)), CARTS[0]) > 2
    tpp("Cam", *FAR); tpp("Cam2", *FAR)
    back = wait(lambda: math.dist(pos(cart(1)) or (0, 0, 0), CARTS[0]) < 1.0, 5)
    chk("cart 1 moved by Cam (%s); all beyond 32: back at its place, one of it" % moved, moved and back and count("@e[type=minecraft:minecart,tag=le.mnc1]") == 1)
    R('summon minecraft:minecart %.1f %.1f %.1f {Tags:["le.mn_cart","le.mnc2"]}' % (CARTS[1][0] + 3, CARTS[1][1], CARTS[1][2]))
    chk("a double of cart 2 (as from a chunk loaded late) goes", wait(lambda: count("@e[type=minecraft:minecart,tag=le.mnc2]") == 1, 4) and math.dist(pos(cart(2)), CARTS[1]) < 1)
    tpp("Cam", CARTS[2][0] - 2, CARTS[2][1], CARTS[2][2] + 1.5)
    R("data merge entity %s {Motion:[0.6d,0.0d,0.0d]}" % cart(3)); time.sleep(9)
    p = pos(cart(3))
    chk("the cart at the top of the adit rolls down to H1 (now %s, H1 rails at y %d)" % ([round(v, 1) for v in p] if p else None, LV[1] + 1), p and p[1] < LV[1] + 1.5 and p[0] > 296)
    tpp("Cam", *FAR); tpp("Cam2", *FAR)
    chk("... and comes back to the top when nobody is within 32", wait(lambda: math.dist(pos(cart(3)) or (0, 0, 0), CARTS[2]) < 1.0, 6))
    stage()

# ---------------------------------------------------------------- Bran
def t_bran():
    print("[bran]"); stage(); base(); time.sleep(2)
    chk("Bran resting in his pocket: an elite named «Бран», the miner's helmet, his pickaxe, NoAI", count("@e[type=minecraft:zombie,tag=le.mn_bran]") == 1 and noai(BRAN_E)
        and "Бран" in nbt(BRAN_E, "CustomName") and "3877402" in nbt(BRAN_E, "equipment.head") and "Кирка Брана" in nbt(BRAN_E, "equipment.mainhand") and "le.elite" in nbt(BRAN_E, "Tags"))
    def shown(): return nbt(BRAN_E, "CustomNameVisible").strip().endswith("1b")
    chk("T-034: resting, his name is hidden (CustomNameVisible 0: it showed through the rock)", not shown() and "0b" in nbt(BRAN_E, "CustomNameVisible"))
    bf = M["big_rect"]; f3 = LV[3]
    front = (264.5, f3 + 1, bf[3] + 2.5)
    tpp("Cam", *front); tpp("Cam2", *YARD)
    k0 = mn("#knocks") or 0; time.sleep(12); k1 = mn("#knocks") or 0
    d = math.dist(front, BRAN[:3])
    chk("his knock heard on H3 in front of the big collapse (%.1f from him, <= 20): %d knocks in 12 s, he rests" % (d, k1 - k0), d <= 20 and k1 - k0 >= 2 and noai(BRAN_E))
    # the crawl dug out (its gravel gone): Cam comes into the pocket -> he wakes
    cr = M["big"]["crawl"]
    R("fill %d %d %d %d %d %d minecraft:air replace minecraft:gravel" % (cr[0], cr[1], cr[2], cr[3], cr[4], cr[5]))
    tpp("Cam", 264.5, f3 + 1, -68.5)
    chk("the crawl dug: Cam in it near the pocket - Bran wakes (bran 1)", wait(lambda: not noai(BRAN_E), 4) and stor("bran") == 1)
    chk("T-034: awake, his name is shown (CustomNameVisible 1)", shown())
    tpp("Cam", *YARD); tpp("Cam2", *YARD)
    chk("T-034: nobody within 32 -> back on his point resting, the name hidden again (CustomNameVisible 0)", wait(lambda: noai(BRAN_E) and stor("bran") == 0, 6) and not shown())
    tpp("Cam", 264.5, f3 + 1, -68.5)
    chk("Cam back in the pocket: he wakes again (bran 1)", wait(lambda: not noai(BRAN_E), 4) and stor("bran") == 1)
    R("kill @e[type=minecraft:item]")
    R("damage %s 1000 minecraft:player_attack by Cam" % BRAN_E); time.sleep(2)
    IB = "type=minecraft:item,x=250,y=65,z=-85,dx=25,dy=25,dz=30"
    def has(n): return count("@e[%s,nbt={Item:%s}]" % (IB, n)) >= 1
    pick = has('{components:{"minecraft:custom_data":{le_bran_pick:1b}}}'); letter = has('{components:{"minecraft:custom_data":{le_bran_letter:1b}}}')
    trophy = has('{components:{"minecraft:custom_data":{le_trophy:"r1"}}}')
    chk("killed by Cam: «Кирка Брана» (%s) and «Письмо Брана» (%s) dropped, the trophy of r1 (%s), bran 2" % (pick, letter, trophy), pick and letter and trophy and stor("bran") == 2)
    R("kill @e[type=minecraft:item]")
    time.sleep(4)
    chk("he does not come back (no Bran after 4 s with the pocket loaded)", count("@e[type=minecraft:zombie,tag=le.mn_bran]") == 0 and stor("bran") == 2)

def t_peace():
    print("[peace]"); stage(); base(); time.sleep(2)
    R("difficulty peaceful"); tpp("Cam", 290.5, LV[3] + 1, -44.5); time.sleep(4)
    its = [R("data get entity @e[type=minecraft:item,tag=le.mnbi,limit=1,sort=random] Item") for _ in range(10)]
    ages = R("data get entity @e[type=minecraft:item,tag=le.mnbi,limit=1] Age")
    chk("peaceful: no dead miners, no Bran; his pickaxe and letter in the pocket (Age -32768), bran 2",
        count("@e[type=minecraft:zombie,tag=le.mn_dead]") == 0 and count("@e[type=minecraft:zombie,tag=le.mn_bran]") == 0 and count("@e[type=minecraft:item,tag=le.mnbi]") == 2
        and "Кирка Брана" in " ".join(its) and "Письмо Брана" in " ".join(its) and "-32768" in ages and stor("bran") == 2)
    R("difficulty easy"); time.sleep(4)
    chk("easy again: the dead miners on their points at once (5), Bran stays gone", count("@e[type=minecraft:zombie,tag=le.mn_dead]") == 5 and count("@e[type=minecraft:zombie,tag=le.mn_bran]") == 0)
    base()

# ---------------------------------------------------------------- Halvard
SMITH = (58.5, 101, 27.5)
def uses(idx): return tc.num(R("data get entity @e[tag=le.tr_smith,limit=1] Offers.Recipes[%d].uses" % idx), r"(\d+)$") or 0     # 0 is not saved
def trade(p, idx):
    tpp(p, 58.5, 101, 25.3); tc.face(p, 58.5, 101, 25.3, 58.5, 101.9, 27.5); time.sleep(0.6)
    tc.act(p, "!use"); time.sleep(1.0); tc.act(p, f"!trade_sel {idx}"); time.sleep(0.7); tc.act(p, "!trade_take"); time.sleep(0.9); tc.act(p, "!sneak_off"); time.sleep(1.0)
def t_smith():
    print("[smith]"); tm.fresh(); stage()
    R('function last_ember:trader/reset {id:"smith"}'); time.sleep(3)
    offers = R("data get entity @e[tag=le.tr_smith,limit=1] Offers.Recipes")
    idx = offers.count("buy:") - 1
    chk("Halvard has the deal «Письмо Брана» -> «Шлем подмастерья» (uses 1, the last of %d)" % (idx + 1), "Письмо Брана" in R("data get entity @e[tag=le.tr_smith,limit=1] Offers.Recipes[%d].buy" % idx) and "Шлем подмастерья" in R("data get entity @e[tag=le.tr_smith,limit=1] Offers.Recipes[%d].sell" % idx))
    for p in ("Cam", "Cam2"): R(f"clear {p}")
    R('give Cam2 minecraft:paper[custom_name={text:"Письмо",italic:false},lore=[{text:"Мастеру Хальварду, в Приют.",color:"gray",italic:false}],custom_data={le_bran_letter:1b}]')
    trade("Cam2", idx)
    chk("a paper named otherwise is not taken (Cam2: no helmet, deal not used)", "iron_helmet" not in inv("Cam2") and uses(idx) == 0)
    R("loot give Cam loot last_ember:mines/bran_letter"); R("loot give Cam loot last_ember:mines/bran_letter")
    for _ in range(3):
        trade("Cam", idx)
        if "iron_helmet" in inv("Cam"): break
    iv = inv("Cam")
    chk("a real purchase: Bran's letter (from his death table) -> «Шлем подмастерья» (iron, Protection I)", "Шлем подмастерья" in iv and "protection" in iv and uses(idx) == 1, iv[:200])
    trade("Cam", idx); iv = inv("Cam")
    chk("the second time the deal is used up (one letter left, one helmet)", iv.count("Шлем подмастерья") == 1 and "Письмо Брана" in iv)
    for p in ("Cam", "Cam2"): R(f"clear {p}")
    R('function last_ember:trader/reset {id:"smith"}')
    stage()

# ---------------------------------------------------------------- zones
def t_zones():
    print("[zones]"); tm.fresh(); stage(); base()
    R("give Cam minecraft:iron_axe"); R("effect give Cam minecraft:haste 60 3 true")
    x1, z1, x2, z2 = M["headframe"]
    tpp("Cam", x1 - 0.5 + 1.2, Y + 1, z2 + 1.5); time.sleep(1.5)
    adv = passed("execute if entity @a[name=Cam,gamemode=adventure]")
    tc.face("Cam", x1 + 0.7, Y + 1, z2 + 1.5, x1 + 0.5, Y + 2.5, z2 + 0.5); time.sleep(0.5)
    tc.act("Cam", "!attack_on"); time.sleep(2.5); tc.act("Cam", "!attack_off")
    chk("the headframe's zone: Cam in adventure (%s), its post stays" % adv, adv and blk(x1, Y + 2, z2, "minecraft:spruce_log"))
    tpp("Cam", 262.5, Y + 1, -63.5); time.sleep(1.5)
    surv = passed("execute if entity @a[name=Cam,gamemode=survival]")
    R("item replace entity Cam weapon.mainhand with minecraft:iron_pickaxe")
    R("setblock 262 %d -62 minecraft:cobblestone" % (Y + 1))
    tc.face("Cam", 262.5, Y + 1, -63.5, 262.5, Y + 1.5, -61.5); time.sleep(0.5)
    g1 = mine("Cam", 262, Y + 1, -62)
    R("give Cam minecraft:iron_pickaxe"); R("item replace entity Cam weapon.mainhand with minecraft:iron_pickaxe")
    w = (301, LV[1] + 2, -52)                  # a rock cell of A1's wall (not a post of the timbering: z -50)
    restore([w], 2)
    tpp("Cam", 299.5, LV[1] + 1, -51.5); time.sleep(1); tc.face("Cam", 299.5, LV[1] + 1, -51.5, w[0] + 0.5, w[1] + 0.5, w[2] + 0.5); time.sleep(0.5)
    g2 = mine("Cam", *w)
    chk("the yard and a drift are breakable: Cam (survival: %s) breaks a block in the yard (%s) and a wall of A1 (%s)" % (surv, g1, g2), surv and g1 and g2)
    restore([w], 2); R("setblock 262 %d -62 minecraft:air" % (Y + 1)); restore([(262, Y + 1, -62)], 1)
    R("clear Cam"); stage()

# ---------------------------------------------------------------- the shaft (the bot does not climb ladders: the client Cam)
def t_shaft():
    print("[shaft]"); stage(prot=False); base()
    ld = M["shaft"]["ladders"]
    R("effect give Cam minecraft:instant_health 1 5 true"); time.sleep(0.5)
    lx = ld[-1]["x"]; tpp("Cam", lx + 0.5, LV[3] + 1, -73.5, 180, -20); time.sleep(1.5)
    h0 = hp("Cam"); t0 = time.time(); okc = True
    for k in range(len(ld) - 1, -1, -1):
        top = ld[k]["top"]; x = ld[k]["x"]
        R("rotate Cam 180 -20"); tc.act("Cam", "!fwd_on")
        up = wait(lambda: (pos("Cam") or [0, 0])[1] >= top + 0.9, 12, 0.15)
        tc.act("Cam", "!fwd_off")
        if not up: okc = False; print("   stuck under", top, pos("Cam")); break
        if k == 0: break
        q = pos("Cam"); tpp("Cam", q[0], q[1], -73.45, -90 if ld[k - 1]["x"] > x else 90, 0)   # off the wall (pressed against it the ladder's box beside blocks)
        nx = ld[k - 1]["x"]; time.sleep(0.2)
        tc.act("Cam", "!fwd_on"); wait(lambda: abs((pos("Cam") or [0])[0] - (nx + 0.5)) < 0.35, 4, 0.05); tc.act("Cam", "!fwd_off"); time.sleep(0.2)
        q = pos("Cam"); tpp("Cam", nx + 0.5, q[1], q[2], 180, -20)      # centred on the next ladder's column (the drift of a step off)
    dt = time.time() - t0; q = pos("Cam")
    chk("Cam climbs the shaft from H3 to the deck by the ladders (forward into a ladder, 2 sideways on each platform): %.1f s (<= 40), at y %.1f" % (dt, q[1] if q else -1), okc and q and q[1] >= Y + 0.9 and dt <= 40)
    chk("no damage on the way up (%.1f -> %.1f)" % (h0 or -1, hp("Cam") or -1), abs((h0 or 0) - (hp("Cam") or 0)) < 0.01)
    # a fall: from the deck's opening down the ladder column to the platform 6 below; from mid-air over a platform
    R("effect give Cam minecraft:instant_health 1 5 true"); time.sleep(0.5); h0 = hp("Cam")
    tpp("Cam", ld[0]["x"] + 0.5, Y + 1.2, -73.5, 180, 60); time.sleep(3); q = pos("Cam")
    chk("into the deck's opening: down the ladders to the platform under it (y %.1f >= %d), no damage" % (q[1] if q else -1, ld[0]["bottom"] + 1), q and q[1] >= ld[0]["bottom"] + 0.9 and abs(h0 - hp("Cam")) < 0.01)
    R("effect give Cam minecraft:instant_health 1 5 true"); time.sleep(0.5); h0 = hp("Cam")
    P = M["shaft"]["platforms"]; gap = max(a - b for a, b in zip(P, P[1:]))
    k = [i for i in range(len(P) - 1) if P[i] - P[i + 1] == gap][0]
    tpp("Cam", 276.5, P[k] - 0.9, -70.5); time.sleep(3); h1 = hp("Cam")
    chk("the highest fall in the shaft: just under platform %d onto %d (%d): %.1f hearts lost (<= 1.5)" % (P[k], P[k + 1], gap, (h0 - h1) / 2), h0 - h1 <= 3.01)
    stage()

# ---------------------------------------------------------------- restart
def t_restart():
    print("[restart]"); stage(); base(); time.sleep(2)
    R("function last_ember:mines/gen/fall_1")
    x, y, z = DEAD[0][:3]; tpp("Cam", x + 3, y, z); wait(lambda: not noai(dsel(1)), 3)
    tpp("Cam", *YARD)
    R("save-all flush"); time.sleep(2)
    tm.restart(); stage(); time.sleep(4)
    tpp("Cam", 282.5, LV[3] + 1, -44.5); time.sleep(4)          # H3, 8 from the nearest dead miner (they wake within 6)
    chk("after a restart: cave-in 1 down (storage, blocks), the others standing", stor("caves.c1") == 1 and stor("caves.c2") == 0 and not blk(292, LV[2] + 1, -60, "minecraft:air") and mn("#c1") == 1)
    chk("after a restart: 5 dead miners, one Bran, 4 carts, 5 props - no doubles",
        count("@e[type=minecraft:zombie,tag=le.mn_dead]") == 5 and count("@e[type=minecraft:zombie,tag=le.mn_bran]") == 1 and count("@e[type=minecraft:minecart,tag=le.mn_cart]") == 4 and count("@e[type=minecraft:item_display,tag=le.mnprop]") == 5)
    chk("after a restart: the dead miners on their points or back to them (none awake with nobody near)", wait(lambda: all(at_point(k) and noai(dsel(k)) for k in range(1, 6)), 8))
    base()

def t_perf():
    print("[perf]"); stage(); base(); time.sleep(2)
    tpp("Cam", 285.5, LV[3] + 1, -44.5); tpp("Cam2", 274.5, LV[3] + 1, -55.5)
    R("execute as @e[type=minecraft:zombie,tag=le.mnr] run function last_ember:mines/wake")
    for i in range(6): R('summon minecraft:zombie %.1f %d -44.5 {Tags:["t33p"],PersistenceRequired:1b}' % (288.5 - i, LV[3] + 1))
    time.sleep(3)
    pr = tm.prof(10)
    ms = {k: v for k, v in pr.items() if "mines" in k}
    tot = sum(v for k, v in ms.items() if k in ("last_ember:mines/loop", "last_ember:mines/second", "last_ember:mines/gen/scan"))
    print("   ", {k.replace("last_ember:", ""): round(v, 4) for k, v in sorted(ms.items(), key=lambda kv: -kv[1])[:8]}, "tick %.2f ms" % pr.get("tick", 0))
    chk("mines/* with two players on H3 in a fight, every dead miner awake: %.3f ms per tick (<= 0.3)" % tot, tot <= 0.3)
    R("kill @e[tag=t33p]"); base()

# smith after the groups with clicks: after the trade window the client Cam no longer breaks blocks (until it is relaunched); restart
# relaunches the clients (their clicks miss right after: only perf follows)
ORDER = ["build", "ore", "caves", "sneak", "bypass", "shaft", "dead", "cap", "carts", "bran", "peace", "zones", "smith", "restart", "perf"]
if __name__ == "__main__":
    want = sys.argv[1:] or ORDER
    for t in ORDER:
        if t in want: globals()["t_" + t]()
    print("RESULT: %d ok, %d failed" % (ok, bad))
    sys.exit(1 if bad else 0)
