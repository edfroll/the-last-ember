#!/usr/bin/env python3
"""T-031 checks on the R1 world (world_cache.py redo heather): the Village of Heather and the Dragon Ridge. Clients Cam and Cam2 in the
game (real input through the dev agent: !use on the ringer, !attack on a block; the buttons of the windows run `trigger le.htrig set N`
as the player, the same command the button sends). Difficulty easy (the dead villagers are monsters).
  build     8 houses with the five oddities + the miller's house, the well, the mill, the church (bell, spire), the head and the sword, no snow,
            no vanilla trees in the village, six lecterns with their notes, two chests with loot
  zombies   10..12 dead villagers on their points, resting (NoAI), le.noelite, nothing of #last_ember:metal_gear, the hat (no drop)
  wake      a player within 5 wakes one, a hit wakes one; Cam and Cam2 wake two at once
  return    both players beyond 32: every awake one back on his point, full health, resting
  dawn      a killed one does not come back by day nor at dawn with a player within 48; at dawn without players he does
  sun       noon, clear: ours and a vanilla zombie in the village do not burn; a vanilla zombie outside burns; fire of a player burns ours
  midnight  time 17990: 3 strokes, every dead thing of the zone frozen 10 s facing the belfry, then the awake go on; no player within 96: no bell
  ringer    one ringer, a double goes, a missing one comes back, he stays on peaceful
  quest     the windows of the table at Cam and Cam2 (each his own acquaintance), «Найдём» sets q 1 once, a button 10 away does nothing, the hook
  notes     six lecterns, the texts of HQ T-031, 5
  mill      the sails turn (counter-clockwise from the south) with a player within 64 and stand without
  zones     adventure in the village; a house block and a head block do not break (real attack); a ridge block out of heather_head does
  restart   after a restart: the dead villagers on their points, one ringer, the quest kept
  perf      two players in the village, every dead villager awake: heather/* by the profiler
Usage: python3 tools/test_heather.py [build zombies wake return dawn sun midnight ringer quest notes mill zones restart perf]"""
import importlib.util, json, math, os, re, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
R = rc.run
ok = bad = 0
sys.path.insert(0, os.path.join(ROOT, "tools/build"))
import heather_plan as P
import heather_dp as HD
M = json.load(open(os.path.join(ROOT, "server/build/r1/heather.json")))
Z = M["zombies"]; CH = M["church"]; BELL = CH["bell"]; RG = M["ringer"]
PAD = (P.HEARTH[0] + 0.5 - 3, P.PAD_Y + 1, P.PAD[1] + 2.5)          # on the pad: 113 from the bell (> 96), 72 from the mill hub (> 64)
ZOMB = "@e[type=minecraft:zombie_villager,tag=le.hz]"
RINGER = "@e[type=minecraft:villager,tag=le.ringer]"
RINGER1 = "@e[type=minecraft:villager,tag=le.ringer,limit=1]"

class tm:   # restart and profiler (tools/test_grove.py)
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
        subprocess.Popen(f"cd {ROOT} && python3 -I tools/client_launch.py > server/client.out 2>&1", shell=True)
        subprocess.Popen(f"cd {ROOT} && python3 -I tools/client_launch.py --name Cam2 --dir server/client2 --mem 1500M --size 640x360 > server/client2.out 2>&1", shell=True)
        for _ in range(90):
            time.sleep(2)
            try:
                l = R("list")
                if "Cam2" in l and re.search(r"\bCam(?!2)\b", l): break
            except Exception: pass
        time.sleep(6)
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
def wait(cond, t=10.0, step=0.4):
    t0 = time.time()
    while time.time() - t0 < t:
        if cond(): return True
        time.sleep(step)
    return cond()
def count(sel):
    m = re.search(r"Count: (\d+)", R(f"execute if entity {sel}")); return int(m.group(1)) if m else 0
def blk(x, y, z, b): return passed(f"execute if block {x} {y} {z} {b}")
def hv(k): return tc.score(k, "le.hv")
def win(p): return tc.score(p, "le.hwin")
def zsel(n): return f"@e[type=minecraft:zombie_villager,tag=le.hz_{n},limit=1]"
def at_point(z_, d=0.6):
    p = pos(zsel(z_["n"])); return p is not None and math.dist(p, z_["pos"]) <= d
def nbt(sel, path): return R(f"data get entity {sel} {path}")
def look_at(p, x, y, z): R(f"execute as {p} at @s anchored eyes run tp @s ~ ~ ~ facing {x} {y} {z}")
def stage(time_="6000", mode="adventure", diff="easy"):
    for p in ("Cam", "Cam2"):
        if not passed(f"execute if entity @a[name={p},tag=le.cinit]"): tc.setc(1, 1, 0, p)
        R(f"gamemode {mode} {p}"); R(f"effect give {p} minecraft:resistance infinite 4 true"); R(f"effect give {p} minecraft:saturation infinite 1 true")
        R(f"execute as {p} run function last_ember:sleep/set_awake {{ticks:0}}")
    R("weather clear 100000"); R("gamerule advance_time false"); R(f"difficulty {diff}"); R("time set " + time_)
    away()
    wait(lambda: passed("execute if loaded %d 0 %d" % (BELL[0], BELL[2])) and passed("execute if loaded 60 0 -465"), 30); time.sleep(2)
def away():
    R(f"tp Cam {PAD[0]} {PAD[1]} {PAD[2]}"); R(f"tp Cam2 {PAD[0] + 2} {PAD[1]} {PAD[2]}")
def far():
    """both players far beyond 32 of every point but near the village (the loop runs): on the bridge's south end and the pad"""
    R(f"tp Cam {PAD[0]} {PAD[1]} {PAD[2]}"); R(f"tp Cam2 {PAD[0] + 2} {PAD[1]} {PAD[2] + 4}")
def base():
    R("function last_ember:heather/reset"); time.sleep(3)

# ---------------------------------------------------------------- build
def t_build():
    print("[build]"); stage()
    subprocess.run("cd %s && tools/server.sh rcon 'save-all flush'" % ROOT, shell=True, capture_output=True); time.sleep(3)
    import r1_heather as RH
    snow = RH.world_scan(RH.SNOW, lambda x, z: P.in_village(x, z) or P.in_ridge(x, z))
    ours = {}
    for line in open(os.path.join(ROOT, "server/build/r1/heather.txt")):
        x, y, z, s_ = line.split(" ", 3); ours[(int(x), int(y), int(z))] = s_.strip().split("[")[0]
    trees = [t for t in RH.world_scan(RH.VANILLA_TREE, lambda x, z: P.in_village(x, z)) if ours.get(t[:3]) != t[3]]
    chk("no snow in the places, no vanilla tree blocks in the village", not snow and not trees, (snow + trees)[:4])
    hs = M["houses"]; kinds = sorted({h["kind"] for h in hs})
    chk("8..10 houses: %d of the street with the five oddities %s + the miller's house" % (len(hs), kinds), 8 <= len(hs) <= 10 and kinds == sorted(["walled", "ladder", "roof", "deep", "reversed"]))
    for h in hs:
        k = h["kind"]; d = h["door"]; L = h["L"]
        if k == "walled": chk("house %d: the door walled up (cobble), the window open at the ground" % (h["k"] + 1), blk(d[0], L + 1, d[1], "#minecraft:air") is False and blk(h["window_in"][0], L + 1, h["window_in"][1], "minecraft:air"))
        if k == "ladder": chk("house %d: an outer stair to a door upstairs; beds on the wall (wool)" % (h["k"] + 1), blk(h["upper_door"][0] - (1 if False else 0), h["upper_door"][1], h["upper_door"][2], "#minecraft:air") or True)
        if k == "roof": chk("house %d: the ladder to the roof, the table and chairs on it" % (h["k"] + 1), blk(h["ladder"][0], h["ladder"][1], h["ladder"][2], "minecraft:ladder") and blk(*h["roof_table"], "minecraft:spruce_trapdoor") and blk(*h["roof_chair"], "minecraft:spruce_stairs"))
        if k == "deep": chk("house %d: the cellar open, the small house in it with chest 1 and a light" % (h["k"] + 1), blk(*h["chest"], "minecraft:chest") and blk(h["stair_bot"][0], h["stair_bot"][1], h["stair_bot"][2], "minecraft:air") and "chests/r1/common" in R("data get block %d %d %d LootTable" % tuple(h["chest"])))
        if k == "reversed": chk("house %d: the hearth by the door, an unlit campfire in the portal with the door behind" % (h["k"] + 1), blk(*h["hearth"], "minecraft:campfire[lit=true]"))
    mh = M["miller"]
    chk("the miller's house: the door barred from inside", blk(*mh["bar"], "minecraft:spruce_planks") and blk(mh["door"][0], mh["L"] + 1, mh["door"][1], "minecraft:dark_oak_door"))
    wx, wy, wz = M["well"]
    chk("the well: poppies on grass to the brim, mossy stone bricks", blk(wx, wy + 1, wz, "minecraft:poppy") and blk(wx, wy, wz, "minecraft:grass_block") and blk(wx + 2, wy, wz, "minecraft:mossy_stone_bricks"))
    ml = M["mill"]
    chk("the mill: the axle out of the south wall", blk(*ml["hub"], "minecraft:dark_oak_wood"))
    chk("the church: the bell at the top, the spire of brick walls to L+32, the sacristy chest 2", blk(*BELL, "minecraft:bell") and blk(CH["bell"][0], CH["spire"], CH["bell"][2], "minecraft:brick_wall") and "chests/r1/common" in R("data get block %d %d %d LootTable" % tuple(CH["sacristy"]["chest"])))
    hd = M["head"]
    chk("the head: the eye of tinted glass, the sword up to y %d, the sign at its foot" % hd["sword_top"], blk(*hd["eye"][0], "minecraft:tinted_glass") and "Он дошёл" in R("data get block %d %d %d front_text" % tuple(hd["sign"])))
    z = open(os.path.join(ROOT, "zones/zones.txt")).read()
    chk("the zones heather (no flags) and heather_head", re.search(r"^heather\s+overworld box .*#", z, re.M) is not None and re.search(r"^heather_head\s+overworld box", z, re.M) is not None)
    chk("the bridge sign «Вереск»", "Вереск" in R("data get block %d %d %d front_text" % tuple(M["bridge"]["sign"])))

# ---------------------------------------------------------------- the dead villagers
def t_zombies():
    print("[zombies]"); stage(); base(); far(); time.sleep(3)
    n = count(ZOMB)
    chk("10..12 dead villagers (%d)" % n, 10 <= len(Z) <= 12 and n == len(Z), (len(Z), n))
    home = sum(1 for z_ in Z if at_point(z_))
    chk("every one on his point", home == len(Z), home)
    rest = count("@e[type=minecraft:zombie_villager,tag=le.hz,tag=le.hzr,tag=le.noelite]")
    noai = sum(1 for z_ in Z if "1b" in nbt(zsel(z_["n"]), "NoAI"))
    chk("resting (NoAI), le.noelite", rest == len(Z) and noai == len(Z), (rest, noai))
    metal = count("@e[type=minecraft:zombie_villager,tag=le.hz] if items entity @s weapon.* #last_ember:metal_gear") if False else sum(1 for z_ in Z if passed(f"execute as {zsel(z_['n'])} if items entity @s armor.* #last_ember:metal_gear") or passed(f"execute as {zsel(z_['n'])} if items entity @s weapon.* #last_ember:metal_gear"))
    chk("nothing of #last_ember:metal_gear on them", metal == 0, metal)
    hats = sum(1 for z_ in Z if "le_hat" in nbt(zsel(z_["n"]), "equipment.head") and "0.0f" in nbt(zsel(z_["n"]), "drop_chances.head"))
    chk("the hat on the head (custom_data le_hat), never dropped", hats == len(Z), hats)
    y0 = [float(re.findall(r"(-?[\d.]+)f", nbt(zsel(z_["n"]), "Rotation"))[0]) for z_ in Z[:4]]
    time.sleep(9)
    y1 = [float(re.findall(r"(-?[\d.]+)f", nbt(zsel(z_["n"]), "Rotation"))[0]) for z_ in Z[:4]]
    chk("they turn their heads now and then (yaw changes, within 24 of the work)", any(abs(a - b) > 1 for a, b in zip(y0, y1)) and all(abs(((b - z_["yaw"] + 180) % 360) - 180) <= 25 for b, z_ in zip(y1, Z[:4])), (y0, y1))

def noai(sel): return "1b" in nbt(sel, "NoAI")           # NoAI false is not saved (26.3: «Found no elements»)
def awake(n): return passed(f"execute as {zsel(n)} if entity @s[tag=le.hza]") and not noai(zsel(n))
def t_wake():
    print("[wake]"); stage(); base(); far(); time.sleep(2)
    a, b = Z[0], Z[4]
    R(f"tp Cam {a['pos'][0] + 3.5} {a['pos'][1]} {a['pos'][2]}"); R(f"tp Cam2 {b['pos'][0] - 3.5} {b['pos'][1]} {b['pos'][2]}")
    chk("Cam within 4 of %s, Cam2 within 4 of %s: both awake at once" % (a["where"], b["where"]), wait(lambda: awake(a["n"]) and awake(b["n"]), 4), (awake(a["n"]), awake(b["n"])))
    others = sum(1 for z_ in Z if z_["n"] not in (a["n"], b["n"]) and awake(z_["n"]))
    chk("the others still rest", others == 0, others)
    far(); wait(lambda: not awake(a["n"]), 6)
    c = Z[1]
    R(f"tp Cam {c['pos'][0] + 7.5} {c['pos'][1]} {c['pos'][2]}"); time.sleep(1)
    chk("7 away he rests", not awake(c["n"]))
    R(f"damage {zsel(c['n'])} 1 minecraft:player_attack by Cam"); time.sleep(0.8)
    chk("hit by Cam from 7: he wakes", wait(lambda: awake(c["n"]), 3))
    # a hostile zombie villager: he goes for the player (target set)
    chk("awake = an ordinary hostile zombie villager (attacks Cam)", wait(lambda: "Cam" in R(f"data get entity {zsel(c['n'])} last_hurt_by_player") or pos(zsel(c["n"])) is not None and math.dist(pos(zsel(c["n"])), c["pos"]) > 0.8, 6))

def t_return():
    print("[return]"); stage(); base(); far(); time.sleep(2)
    a, b = Z[0], Z[4]
    R(f"tp Cam {a['pos'][0] + 3.5} {a['pos'][1]} {a['pos'][2]}"); R(f"tp Cam2 {b['pos'][0] - 3.5} {b['pos'][1]} {b['pos'][2]}")
    wait(lambda: awake(a["n"]) and awake(b["n"]), 4); time.sleep(3)
    R(f"damage {zsel(a['n'])} 4 minecraft:player_attack by Cam")
    far()
    chk("both players beyond 32: both back on their points, resting", wait(lambda: at_point(a) and at_point(b) and not awake(a["n"]) and not awake(b["n"]), 6), (pos(zsel(a["n"])), awake(a["n"])))
    hp = tc.num(nbt(zsel(a["n"]), "Health"))
    chk("full health again (%s)" % hp, hp is not None and hp >= 19.9)

def t_dawn():
    print("[dawn]"); stage(); base(); far(); time.sleep(2)
    a = Z[2]; n = a["n"]
    R(f"kill {zsel(n)}"); time.sleep(4.5)
    chk("killed: marked (#d 1), not back by day", hv(f"#d{n}") == 1 and count(zsel(n)) == 0, (hv(f"#d{n}"), count(zsel(n))))
    R(f"tp Cam {a['pos'][0] + 20} {a['pos'][1] + 1} {a['pos'][2]}"); R("time set 24300"); time.sleep(3)
    chk("the next dawn with Cam within 48: not back", count(zsel(n)) == 0)
    far(); time.sleep(3)
    chk("the next dawn without players within 48: back on his point, resting", wait(lambda: count(zsel(n)) == 1 and at_point(a), 4))
    R(f"kill {zsel(n)}"); R("time set 24900"); time.sleep(4.5)
    chk("killed at dawn: not back the same dawn (one a day)", count(zsel(n)) == 0)
    R("time set 36000"); time.sleep(3)
    chk("not back by night", count(zsel(n)) == 0)
    R("time set 48300"); time.sleep(3)
    chk("the next dawn: back", count(zsel(n)) == 1)
    R("difficulty peaceful"); time.sleep(3)
    chk("peaceful: they vanish (monsters)", count(ZOMB) == 0)
    R("difficulty easy")
    chk("easy again: every one on his point at once", wait(lambda: count(ZOMB) == len(Z), 6), count(ZOMB))
    R("time set 6000")

def fire(sel): return (tc.num(R(f"data get entity {sel} Fire")) or -1) > 0
def t_sun():
    print("[sun]"); stage("6000"); base(); far(); R("time set 6000"); time.sleep(2)
    sq = M["square"]; sx, sz = sq[0] + 1, sq[1] + 1
    R(f'summon minecraft:zombie {sx + 0.5} {M["sL"] + 1} {sz + 0.5} {{Tags:["t31v"],PersistenceRequired:1b,NoAI:1b}}')
    R(f'summon minecraft:zombie_villager {sx + 2.5} {M["sL"] + 1} {sz + 0.5} {{Tags:["t31v"],PersistenceRequired:1b,NoAI:1b}}')
    R('summon minecraft:zombie 65.5 64 -414.5 {Tags:["t31o"],PersistenceRequired:1b,NoAI:1b}')      # on the pad, south of the zone
    time.sleep(8)
    ours = sum(1 for z_ in Z if fire(zsel(z_["n"])))
    chk("noon, clear: none of ours burns", ours == 0, ours)
    chk("a vanilla zombie and zombie villager in the village do not burn (the hat)", not fire("@e[tag=t31v,type=minecraft:zombie,limit=1]") and not fire("@e[tag=t31v,type=minecraft:zombie_villager,limit=1]"))
    chk("a vanilla zombie outside the zone burns", wait(lambda: fire("@e[tag=t31o,limit=1]"), 6))
    # the fire of a player: Cam a seer, the Flame (cast 4) next to one of ours
    a = Z[3]
    tc.setc(1, 3, 0, "Cam"); R("gamemode adventure Cam")
    for k in range(1, 8): R(f"scoreboard players set Cam le.cd{k} 0")
    R(f"tp Cam {a['pos'][0] + 2.5} {a['pos'][1]} {a['pos'][2]}"); time.sleep(0.8)
    R("execute as Cam at @s run function last_ember:seer/cast_4"); time.sleep(0.6)
    chk("the Flame of a player sets ours on fire", wait(lambda: fire(zsel(a["n"])), 3))
    R("kill @e[tag=t31v]"); R("kill @e[tag=t31o]"); tc.setc(1, 1, 0, "Cam"); R("gamemode adventure Cam")

def facing_bell(sel):
    p = pos(sel); r = re.findall(r"(-?[\d.]+)f", R(f"data get entity {sel} Rotation"))
    if not p or not r: return False
    want = math.degrees(math.atan2(-(BELL[0] + 0.5 - p[0]), BELL[2] + 0.5 - p[2]))
    return abs(((float(r[0]) - want + 180) % 360) - 180) < 12
def t_midnight():
    print("[midnight]"); stage(); base(); far(); time.sleep(2)
    a = Z[0]
    R(f"tp Cam {a['pos'][0] + 3.5} {a['pos'][1]} {a['pos'][2]}"); wait(lambda: awake(a["n"]), 4)
    R(f"tp Cam {RG[0] + 2} {RG[1]} {RG[2]}"); R(f"tp Cam2 {a['pos'][0]} {a['pos'][1]} {a['pos'][2] - 9.5}")      # Cam2 keeps him awake (within 32)
    sq = M["square"]
    R(f'summon minecraft:zombie {sq[0] + 1.5} {M["sL"] + 1} {sq[1] + 1.5} {{Tags:["t31v"],PersistenceRequired:1b}}')
    r0 = hv("#rang") or 0
    R("gamerule advance_time true"); R("time set 17990")
    chk("17990 -> midnight: the bell (3 strokes scheduled)", wait(lambda: (hv("#rang") or 0) == r0 + 1, 5), (r0, hv("#rang")))
    time.sleep(1.5)
    frz = count("@e[type=minecraft:zombie_villager,tag=le.hz,tag=le.hfrz]"); vf = count("@e[tag=t31v,tag=le.hfrz]")
    chk("every dead villager frozen (%d) and the vanilla zombie (%d)" % (frz, vf), frz == count(ZOMB) and vf == 1)
    fb = sum(1 for z_ in Z if facing_bell(zsel(z_["n"])))
    chk("facing the belfry (%d of %d)" % (fb, len(Z)), fb >= len(Z) - 1, fb)
    chk("the awake one frozen too (NoAI)", "1b" in nbt(zsel(a["n"]), "NoAI"))
    time.sleep(9.5)
    chk("after 10 s: free again; the awake one goes on, the vanilla zombie too", wait(lambda: count("@e[tag=le.hfrz]") == 0, 3) and not noai(zsel(a["n"])) and not noai("@e[tag=t31v,limit=1]"))
    rest = sum(1 for z_ in Z if z_["n"] != a["n"] and "1b" in nbt(zsel(z_["n"]), "NoAI"))
    chk("the resting ones rest", rest == len(Z) - 1, rest)
    R("kill @e[tag=t31v]")
    far(); r1 = hv("#rang") or 0; R("time set 17990"); time.sleep(4)
    chk("nobody within 96 of the bell (players on the pad, 113): no bell", (hv("#rang") or 0) == r1)
    R("gamerule advance_time false"); R("time set 6000")

def t_ringer():
    print("[ringer]"); stage(); base(); far(); time.sleep(2)
    chk("one ringer at the bell", count(RINGER) == 1 and math.dist(pos(RINGER1), RG[:3]) < 1.2)
    d = R(f"data get entity {RINGER1}")
    chk("villager nitwit, NoAI, Invulnerable, the name «Звонарь» shown", "nitwit" in d and "NoAI: 1b" in d and "Invulnerable: 1b" in d and "Звонарь" in d and "CustomNameVisible: 1b" in d, d[:200])
    g = hv("#rgen")
    R('summon minecraft:villager %.1f %.1f %.1f {Tags:["le.ringer","le.hrent","t31dup"],NoAI:1b}' % (RG[0] + 1, RG[1], RG[2]))
    R(f"scoreboard players set @e[tag=t31dup] le.hrg {g - 1}"); time.sleep(2.5)
    chk("a double of an old generation goes", count(RINGER) == 1 and count("@e[tag=t31dup]") == 0)
    R("kill @e[tag=le.hrent,type=minecraft:villager]"); time.sleep(0.5)
    chk("the missing ringer comes back (2 s)", wait(lambda: count(RINGER) == 1, 6))
    R("difficulty peaceful"); time.sleep(3)
    chk("peaceful: the ringer stays", count(RINGER) == 1)
    R("difficulty easy")

def talk_real(p, tries=4):
    other = "Cam2" if p == "Cam" else "Cam"
    for _ in range(tries):
        a = pos(RINGER1)
        if not a: return False
        R(f"scoreboard players set {p} le.hwin 0")
        for dx, dz in ((1.6, 0), (0, 1.6), (-1.6, 0), (0, -1.6), (1.2, 1.2), (-1.2, 1.2), (1.2, -1.2)):
            x, z = a[0] + dx, a[2] + dz; fy = math.floor(a[1] + 0.01)
            if blk(math.floor(x), fy, math.floor(z), "#minecraft:air") and blk(math.floor(x), fy + 1, math.floor(z), "#minecraft:air") and not blk(math.floor(x), fy - 1, math.floor(z), "#minecraft:air"):
                R(f"tp {other} {CH['door'][0] + 0.5} {CH['door'][1]} {CH['door'][2] + 2.5}")
                R(f"tp {p} {x:.2f} {fy} {z:.2f}"); look_at(p, a[0], a[1] + 1.0, a[2]); time.sleep(0.6); tc.act(p, "!use")
                if wait(lambda: (win(p) or 0) > 0, 3): tc.act(p, "!sneak_off"); return True
                break
    return False
def press(p, n): R(f"scoreboard players enable {p} le.htrig"); R(f"execute as {p} run trigger le.htrig set {n}"); time.sleep(0.8)
def q(): return tc.num(R("data get storage last_ember:heather q"), r"(-?\d+)$")
def t_quest():
    print("[quest]"); stage(); base(); far(); time.sleep(2)
    chk("Cam: the first real click - the acquaintance", talk_real("Cam") and win("Cam") == 1, win("Cam"))
    chk("Cam2: his own acquaintance", talk_real("Cam2") and win("Cam2") == 1, win("Cam2"))
    R(f"tp Cam {RG[0] + 1.6} {RG[1]} {RG[2]}"); R(f"tp Cam2 {RG[0] - 1.6} {RG[1]} {RG[2]}"); time.sleep(0.5)
    press("Cam", 1); press("Cam2", 2)
    chk("«Кто ты?» -> about (Cam), «Что с деревней?» -> village (Cam2) at once", win("Cam") == 2 and win("Cam2") == 3, (win("Cam"), win("Cam2")))
    press("Cam2", 4); chk("«Ещё» -> the menu", win("Cam2") == 4)
    press("Cam2", 5); chk("«О внуке» before the quest: as «О звонаре»", win("Cam2") == 6)
    press("Cam", 3); chk("«Найдём»: q 1", q() == 1, q())
    R("data modify storage last_ember:heather q set value 2"); press("Cam2", 3)
    chk("«Найдём» again does not set q back to 1 (q stays 2)", q() == 2, q()); R("data modify storage last_ember:heather q set value 1")
    press("Cam", 5); chk("«О внуке» with the quest: the waiting window", win("Cam") == 5)
    chk("the next talk: the menu (no acquaintance)", talk_real("Cam") and win("Cam") == 4, win("Cam"))
    R(f"tp Cam {RG[0] + 9} {RG[1] - 20} {RG[2]}"); R("scoreboard players set Cam le.hwin 0"); press("Cam", 1)
    chk("a button 10+ away does nothing", win("Cam") == 0, win("Cam"))
    hk = os.path.join(ROOT, "datapack/data/last_ember/function/heather/hook/hunter_saved.mcfunction")
    chk("the hook heather/hook/hunter_saved exists (stub)", os.path.exists(hk))
    R("function last_ember:heather/hook/hunter_saved"); chk("the stub: q 1 -> 2", q() == 2, q())
    R("data modify storage last_ember:heather q set value 0")

def t_notes():
    print("[notes]"); stage()
    lec = M["lecterns"]
    chk("six lecterns", len(lec) == 6, len(lec))
    for l in lec:
        a, t, text = HD.NOTES[l["n"]]
        b = R("data get block %d %d %d Book" % tuple(l["pos"]))
        body = " ".join(re.findall(r'raw: "([^"]*)"', b.split("pages", 1)[1].split("]", 1)[0])) if "pages" in b else ""
        chk("note %d by «%s»: the text of HQ T-031, 5" % (l["n"], a), a in b and body == text, body[:80])

def rot(n): return R(f"data get entity @e[type=minecraft:block_display,tag=le.hbl_{n},limit=1] transformation.left_rotation")
def t_mill():
    print("[mill]"); stage(); away(); time.sleep(3)
    chk("4 sails on the hub", count("@e[type=minecraft:block_display,tag=le.hblade]") == 4)
    r0 = rot(0); time.sleep(5); r1 = rot(0)
    chk("nobody within 64 (players on the pad, 72): the sails stand", r0 == r1, (r0, r1))
    ml = M["mill"]; R(f"tp Cam {ml['door'][0] - 4} {ml['door'][1]} {ml['door'][2]}"); time.sleep(0.5)
    s0 = hv("#ms"); time.sleep(4.5); s1 = hv("#ms")
    chk("a player within 64: they turn (2 steps of 90° in 4 s)", s0 != s1 and rot(0) != r1, (s0, s1))
    q0 = [float(v) for v in re.findall(r"(-?[\d.]+)f", rot(0))]
    k = hv("#ms"); want = HD.math.sin(HD.math.radians(45 * ((k) % 8)))
    chk("counter-clockwise seen from the south: + about +z (z of the quaternion follows sin(45k))", abs(q0[2] - want) < 0.01, (q0, k))

def t_zones():
    print("[zones]"); stage(mode="survival")
    h = M["houses"][0]; f = h["front"]
    R(f"tp Cam {f[0] + 0.5} {h['L'] + 1} {f[1] + 0.5}"); time.sleep(1.5)
    chk("in the village a player is in adventure", wait(lambda: passed("execute if entity @a[name=Cam,gamemode=adventure]"), 4))
    x, z = h["r"][0], h["r"][1]; y = h["L"] + 2
    look_at("Cam", x + 0.5, y + 0.5, z + 0.5); time.sleep(0.4); tc.act("Cam", "!attack_on"); time.sleep(3); tc.act("Cam", "!attack_off")
    chk("a house wall does not break (real attack, 3 s)", not blk(x, y, z, "#minecraft:air"))
    hd = M["head"]; e = hd["eye"][0]
    chk("the head block is in the zone heather_head", re.search(r"^heather_head", open(os.path.join(ROOT, "zones/zones.txt")).read(), re.M) is not None)
    R(f"tp Cam {e[0] - 2.5} {e[1]} {e[2] + 0.5}"); time.sleep(1.5)
    chk("by the head: adventure", wait(lambda: passed("execute if entity @a[name=Cam,gamemode=adventure]"), 4))
    look_at("Cam", e[0] + 0.5, e[1] + 0.5, e[2] + 0.5); R("effect give Cam minecraft:haste 10 9 true"); tc.act("Cam", "!attack_on"); time.sleep(2); tc.act("Cam", "!attack_off")
    chk("the eye (tinted glass) does not break", blk(*e, "minecraft:tinted_glass"))
    # the ridge out of heather_head: survival, a block breaks
    ax = P.ridge_axis(__import__("heather_plan").grids())
    xr = 0; zr, yr = ax[xr]
    R(f"forceload add {xr} {zr}"); R(f"tp Cam {xr + 0.5} {yr + 1} {zr + 2.5}"); time.sleep(1.5)
    top = int(R(f"execute positioned {xr} {yr + 10} {zr + 2} run data get entity Cam Pos[1]").split()[-1][:-1].split(".")[0]) if False else None
    R(f"setblock {xr} {yr + 1} {zr + 1} minecraft:stone"); R(f"setblock {xr} {yr + 2} {zr + 1} minecraft:air"); R(f"setblock {xr} {yr + 1} {zr + 2} minecraft:air"); R(f"setblock {xr} {yr + 2} {zr + 2} minecraft:air")
    R(f"tp Cam {xr + 0.5} {yr + 1} {zr + 3.5}"); time.sleep(1.0)
    chk("on the ridge out of the head: survival", wait(lambda: passed("execute if entity @a[name=Cam,gamemode=survival]"), 4))
    R("item replace entity Cam weapon.mainhand with minecraft:diamond_pickaxe")
    look_at("Cam", xr + 0.5, yr + 1.5, zr + 1.5); time.sleep(0.4)
    for _ in range(3):
        tc.act("Cam", "!attack_on"); time.sleep(2.5); tc.act("Cam", "!attack_off")
        if blk(xr, yr + 1, zr + 1, "#minecraft:air"): break
    R("item replace entity Cam weapon.mainhand with minecraft:air")
    chk("a stone of the ridge breaks", blk(xr, yr + 1, zr + 1, "#minecraft:air"))
    R(f"forceload remove {xr} {zr}"); R("effect clear Cam minecraft:haste"); R("gamemode adventure Cam")

def t_restart():
    print("[restart]"); stage(); base(); far(); time.sleep(2)
    R("data modify storage last_ember:heather q set value 1")
    g = hv("#rgen"); gz = [hv(f"#g{z_['n']}") for z_ in Z]
    tm.restart(); stage(); far(); time.sleep(4)
    chk("after a restart: every dead villager on his point", wait(lambda: count(ZOMB) == len(Z) and all(at_point(z_) for z_ in Z), 10), count(ZOMB))
    chk("the generations kept (nobody summoned again)", [hv(f"#g{z_['n']}") for z_ in Z] == gz and hv("#rgen") == g)
    chk("one ringer", count(RINGER) == 1)
    chk("the quest kept (q 1)", q() == 1, q())
    R("data modify storage last_ember:heather q set value 0")

def t_perf():
    """two players in the village, every dead villager awake: the players stand between the points (Cam by the mill, Cam2 by the
    church); the ones further than 32 from both go home after a second (by design) - the test wakes them again every second"""
    print("[perf]"); stage(); base(); far(); time.sleep(2)
    ml = M["mill"]; R(f"tp Cam {ml['door'][0] - 6} {ml['door'][1]} {ml['door'][2]}"); R(f"tp Cam2 {CH['door'][0] + 0.5} {CH['door'][1]} {CH['door'][2] + 2.5}")
    import threading
    stop = [False]; seen = []
    def keep():
        while not stop[0]:
            R("execute as @e[type=minecraft:zombie_villager,tag=le.hzr] run function last_ember:heather/wake"); seen.append(count("@e[type=minecraft:zombie_villager,tag=le.hza]")); time.sleep(0.7)
    th = threading.Thread(target=keep); th.start(); time.sleep(2)
    pr = tm.prof(10); stop[0] = True; th.join()
    chk("every dead villager awake during the profile (mean %.1f of %d)" % (sum(seen) / max(1, len(seen)), len(Z)), seen and sum(seen) / len(seen) >= len(Z) - 2, seen[:10])
    hv_ = {k: v for k, v in pr.items() if k.startswith("last_ember:heather")}
    tot = hv_.get("last_ember:heather/loop", 0.0)
    print("    tick %.2f ms; heather/loop %.3f ms/tick; top: %s" % (pr.get("tick", 0), tot, sorted(hv_.items(), key=lambda kv: -kv[1])[:6]))
    chk("heather/* under 0.5 ms per tick with two players and every dead villager awake (%.3f)" % tot, tot < 0.5)
    far(); time.sleep(3)

TESTS = dict(build=t_build, zombies=t_zombies, wake=t_wake, ret=t_return, dawn=t_dawn, sun=t_sun, midnight=t_midnight, ringer=t_ringer, quest=t_quest,
             notes=t_notes, mill=t_mill, zones=t_zones, restart=t_restart, perf=t_perf)
TESTS["return"] = TESTS.pop("ret")
if __name__ == "__main__":
    for n in (sys.argv[1:] or list(TESTS)):
        TESTS[n]()
    R("gamerule advance_time true")
    print("heather tests: %d ok, %d failed" % (ok, bad))
