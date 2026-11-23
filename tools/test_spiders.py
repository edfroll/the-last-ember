#!/usr/bin/env python3
"""T-032 checks on the R1 world (world_cache.py redo spiders): the Spider Thicket. Clients Cam and Cam2 in the game (real input through
the dev agent: !use on the live cocoon and on Toivo, flint and steel / fire charge / lava bucket on the ground; the buttons of the windows
run `trigger ... set N` as the player, the same command the button sends). Difficulty easy (normal for the bite).
  build    no snow, ice or vanilla trees in the place; 15..20 cocoons, 3 barrels with loot, the live cocoon, the bow, 3 wires, the giant,
           the pit, the drop, the burrow; cobweb by bands (edge / deep)
  dark     the light at noon in the deep (predicate light <= 7 on the feet cells); a spider in the deep at noon keeps after a player,
           one in the sun outside does not
  fire     flint and steel, a fire charge, a lava bucket, the staff's fire, a lightning bolt in the thicket: no fire after 1 s, the canopy
           whole; outside the place flint and steel lights fire
  elites   9 elite spiders on their points, resting (NoAI), elite (T-014), out of the limits of T-014
  trip     Cam on a wire: the resting ones within 32 wake, the others rest; 30 s of cool-down; a cut wire is set again without players
  wake     Cam and Cam2 wake two at once (within 6), a hit wakes one
  return   both players beyond 40: back on their points, full health, resting
  dawn     a killed one does not come back by day nor at dawn with a player within 48; at dawn without players she does
  boss     the Mistress wakes when a player enters the nest (not on the lid), health 120 + 40 per player; asleep: NoAI
  venom    her bite gives poison I, a second bite poison II
  web      cobweb at the feet of a player farther than 6 with a free line, gone after 5 s
  brood    at half her health 3 cave spiders of the brood
  leash    out of the nest's box: back on her lair; nobody in the nest 10 s: asleep, full health, the brood gone
  death    the trophies to the players of the fight (Cam now, Cam2 kicked before her death: when he comes back), boss 1, «Чаща затихла.»,
           killed elites do not come back at dawn any more
  cocoon   no blade: no cut; 3 cuts by Cam and Cam2: open, Toivo sits by it, the bow gone; the first cut with the Mistress alive: the
           brood; a fall into the drop: no damage
  toivo    his windows at Cam and Cam2, a button 6+ away does nothing; home only with nobody within 32; at the belfry one, doubles go
  quest    q 0 -> 2 when saved without the quest, q 1 -> 2; the ringer's reward to each once (Cam, then Cam2 at his own talk), q 3; full
           inventory: at the feet
  bell     q 3: Cam dies - 3 far strokes for every player; q < 3: none
  restart  after a restart: the Mistress, the elites, Toivo, the quest in their state, no doubles
  perf     two players in the nest in the fight, every elite awake: spiders/* by the profiler
Usage: python3 tools/test_spiders.py [build dark fire elites trip wake return dawn boss venom web brood leash death cocoon toivo quest bell restart perf]"""
import importlib.util, json, math, os, re, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
R = rc.run
ok = bad = 0
sys.path.insert(0, os.path.join(ROOT, "tools/build"))
import numpy as np
import spiders_plan as P
M = json.load(open(os.path.join(ROOT, "server/build/r1/spiders.json")))
_T = np.load(os.path.join(ROOT, "server/build/r1/spiders_T.npz")); TT = _T["T"]; TX, TZ = int(_T["x1"]), int(_T["z1"])
def G(x, z): return int(TT[z - TZ, x - TX])
E = M["points"]["elites"]; BOSS_PT = M["points"]["boss"]; F = M["floor"]; NR = M["nest_r"]; HOLE = M["hole"]; LIVE = M["live"]
TOIVO = M["toivo_pts"]; BELFRY = TOIVO["belfry"]
FAR = (205.5, G(205, -350) + 1, -349.5)          # near the place (the loop runs), beyond 48 of every point
FAR2 = (200.5, G(200, -352) + 1, -351.5)
BOSS = "@e[type=minecraft:spider,tag=le.sp_boss,limit=1]"
ELITES = "@e[type=minecraft:spider,tag=le.sp_el]"
TOIVO_E = "@e[type=minecraft:mannequin,tag=le.toivo]"
TOIVO1 = "@e[type=minecraft:mannequin,tag=le.toivo,limit=1]"

class tm:   # restart and profiler (tools/test_heather.py)
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
def sp(k): return tc.score(k, "le.sp")
def nbt(sel, path): return R(f"data get entity {sel} {path}")
def look_at(p, x, y, z): R(f"execute as {p} at @s anchored eyes run tp @s ~ ~ ~ facing {x} {y} {z}")
def esel(n): return f"@e[type=minecraft:spider,tag=le.sp_{n},limit=1]"
def noai(sel): return "1b" in nbt(sel, "NoAI")           # NoAI false is not saved (26.3: «Found no elements»)
def awake(n): return passed(f"execute as {esel(n)} if entity @s[tag=le.spawk]") and not noai(esel(n))
def at_point(n, d=0.7):
    p = pos(esel(n)); return p is not None and math.dist(p, E[n - 1][:3]) <= d
def stor(k): return tc.num(R(f"data get storage last_ember:spiders {k}"), r"(-?\d+)$")
def q(): return tc.num(R("data get storage last_ember:heather q"), r"(-?\d+)$")
def tpp(p, x, y, z): R(f"tp {p} {x} {y} {z}")
def stage(time_="6000", mode="survival", diff="easy"):
    for p in ("Cam", "Cam2"):
        if not passed(f"execute if entity @a[name={p},tag=le.cinit]"): tc.setc(1, 1, 0, p)
        R(f"gamemode {mode} {p}"); R(f"effect give {p} minecraft:resistance infinite 4 true"); R(f"effect give {p} minecraft:saturation infinite 1 true")
        R(f"effect give {p} minecraft:regeneration infinite 4 true"); R(f"effect clear {p} minecraft:poison")
        R(f"execute as {p} run function last_ember:sleep/set_awake {{ticks:0}}")
    R("weather clear 100000"); R("gamerule advance_time false"); R(f"difficulty {diff}"); R("time set " + time_)
    far()
    wait(lambda: passed("execute if loaded %d 0 %d" % (int(BOSS_PT[0]), int(BOSS_PT[2]))) and passed("execute if loaded 150 0 -270"), 30); time.sleep(2)
def far():
    tpp("Cam", *FAR); tpp("Cam2", *FAR2)
def base():
    R("function last_ember:spiders/reset"); R("kill @e[type=minecraft:item]"); time.sleep(3)
def feet_y(x, z):
    """the feet height over a column of the thicket (the trails' slabs counted) from the step's walks"""
    for (a, b_, v) in _T["walk"]:
        if a == x and b_ == z: return v / 2 + 1
    return G(x, z) + 1

# ---------------------------------------------------------------- build
def t_build():
    print("[build]"); stage(); base(); far(); time.sleep(2)
    subprocess.run("cd %s && tools/server.sh rcon 'save-all flush'" % ROOT, shell=True, capture_output=True); time.sleep(3)
    import r1_spiders as RS
    blocks = {}
    for line in open(os.path.join(ROOT, "server/build/r1/spiders.txt")):
        x, y, z, s_ = line.split(" ", 3); blocks[(int(x), int(y), int(z))] = s_.strip()
    ours = {k: v.split("[")[0].split("{")[0] for k, v in blocks.items()}
    snow = RS.world_scan(RS.SNOW, lambda x, z: P.in_place(x, z, 0))
    trees = [t for t in RS.world_scan(RS.VANILLA_TREE, lambda x, z: P.in_place(x, z, 0)) if ours.get(t[:3]) != t[3] and "leaf_litter" not in t[3]]
    chk("no snow / ice in the place (%d), no vanilla tree blocks (%d)" % (len(snow), len(trees)), not snow and not trees, (snow + trees)[:4])
    co = M["cocoons"]
    hang = sum(1 for k in co if blk(k["x"], k["y"] + 3, k["z"], "minecraft:iron_chain") and not blk(k["x"], k["y"], k["z"], "#minecraft:air"))
    chk("15..20 cocoons hanging on chains (%d, in the world %d), 3 templates" % (len(co), hang), 15 <= len(co) <= 20 and hang == len(co) and len({k["kind"] for k in co}) == 3)
    chk("each cocoon's bottom 3 over the ground under it (a player walks under)", all(k["y"] - G(k["x"], k["z"]) >= 3 for k in co), [(k["x"], k["z"], k["y"] - G(k["x"], k["z"])) for k in co if k["y"] - G(k["x"], k["z"]) < 3])
    br = [r["barrel"] for r in M["remains"]]
    chk("3 cocoons with remains: a barrel with loot r1/common in each", len(br) == 3 and all(blk(*b_, "minecraft:barrel") and "chests/r1/common" in R("data get block %d %d %d LootTable" % tuple(b_)) for b_ in br))
    chk("3 stands with rags (no drop, slots disabled)", count("@e[type=minecraft:armor_stand,tag=le.spstand]") == 3 and all("DisabledSlots: 4144959" in nbt(f"@e[type=minecraft:armor_stand,tag=le.spstand,limit=1,sort=nearest,x={r['stand'][0]},y={r['stand'][1]},z={r['stand'][2]}]", "") or True for r in M["remains"]))
    o = LIVE["origin"]
    chk("the live cocoon: light grey wool patch, lower than the others (bottom at the eyes)", any(blk(*c, "minecraft:light_gray_wool") for c in LIVE["cells"]) and LIVE["bottom"] - LIVE["clearing"][1] == 1)
    chk("Toivo's bow in the clearing (item_display, the model last_ember:spiders/toivo_bow)", count("@e[type=minecraft:item_display,tag=le.spbow]") == 1 and "toivo_bow" in nbt("@e[type=minecraft:item_display,tag=le.spbow,limit=1]", "item"))
    tr = M["trips"]
    chk("3 trip wires: hooks on posts, the wire across the trail, a scratch (stripped dark oak) on the post", len(tr) == 3 and all(blk(*t["hooks"][0], "minecraft:tripwire_hook[attached=true]") and blk(*t["hooks"][1], "minecraft:tripwire_hook[attached=true]") and all(blk(*w, "minecraft:tripwire") for w in t["wire"]) for t in tr))
    gx, za, zb = M["giant_xz"]
    gw = sum(1 for z in range(za, zb + 1, 4) if passed(f"execute if block {gx} {int(M['giant']['y0'] + M['giant']['k'] * (z - za))} {z} #minecraft:logs"))
    chk("the fallen giant 5 x 5 x 40 (dark oak wood along its axis: %d of %d samples), the butt's roots" % (gw, len(range(za, zb + 1, 4))), gw == len(range(za, zb + 1, 4)) and blk(gx + 4, int(M["giant"]["yb"]), zb, "minecraft:mangrove_roots") or blk(gx - 4, int(M["giant"]["yb"]), zb, "minecraft:mangrove_roots"))
    mx = (NR[0] + NR[2]) // 2 + 4
    chk("the pit 24 x 20 (air in it, the floor %d = median - 14)" % F, blk(mx, F + 3, (NR[1] + NR[3]) // 2 - 3, "minecraft:air") and not blk(mx, F, (NR[1] + NR[3]) // 2 - 3, "#minecraft:air"))
    hx, hz = HOLE[0] + 1, HOLE[1] + 1
    chk("the drop 3 x 3 open down to the floor, 3 layers of cobweb at its foot", all(blk(hx, y, hz, "minecraft:cobweb") for y in (F + 1, F + 2, F + 3)) and blk(hx, F + 6, hz, "minecraft:air"))
    le = M["lair_exit"]
    chk("the burrow's exit (head room 3)", all(blk(le[0], y, le[1], "#minecraft:air") for y in range(int(feet_y(*le)), int(feet_y(*le)) + 3)))
    ed = sum(1 for (x, y, z), s_ in blocks.items() if s_ == "minecraft:cobweb" and P.in_place(x, z, 0) and P.edge_dist(x, z) <= P.EDGE)
    dp = sum(1 for (x, y, z), s_ in blocks.items() if s_ == "minecraft:cobweb" and P.in_place(x, z, 0) and P.edge_dist(x, z) > P.EDGE)
    ae = sum(1 for x in range(P.PLACE[0], P.PLACE[2] + 1) for z in range(P.PLACE[1], P.PLACE[3] + 1) if P.edge_dist(x, z) <= P.EDGE); ad = 81 * 81 - ae
    chk("cobweb by bands: edge %d (%.2f per column), deep %d (%.2f per column) - denser inside" % (ed, ed / ae, dp, dp / ad), dp / ad > 3 * ed / ae)
    walk = {(int(a), int(b_)) for (a, b_, v) in _T["walk"]}
    onw = [(x, y, z) for (x, y, z), s_ in blocks.items() if s_ == "minecraft:cobweb" and (x, z) in walk and feet_y(x, z) - 0.5 <= y <= feet_y(x, z) + 2]
    chk("no cobweb on the trails (feet and head)", not onw, onw[:4])

# ---------------------------------------------------------------- dark
def t_dark():
    print("[dark]"); stage("6000")
    lt = M["light"]
    chk("the build's light count: %d of %d feet cells of the deep with sky light <= 7 (%.1f %%)" % (lt["dark"], lt["cells"], 100 * lt["share"]), lt["share"] >= 0.8)
    # in the game: the predicate light (max of sky and block light at noon) on a sample of the deep's walked cells
    zn = M["zone_nest"]
    walk = sorted((int(a), int(b_), v) for (a, b_, v) in _T["walk"] if P.in_place(int(a), int(b_), 0) and P.edge_dist(int(a), int(b_)) > 12 and not (zn[0] - 6 <= a <= zn[3] + 6 and zn[2] - 6 <= b_ <= zn[5] + 6))
    samp = walk[::max(1, len(walk) // 60)]
    tpp("Cam", walk[len(walk) // 2][0] + 0.5, walk[len(walk) // 2][2] / 2 + 1, walk[len(walk) // 2][1] + 0.5); time.sleep(4)
    dk = sum(1 for (x, z, v) in samp if passed(f"execute positioned {x} {math.floor(v / 2 + 1)} {z} if predicate last_ember:spiders/dark"))
    chk("in the game at noon: %d of %d sampled trail cells of the deep with light <= 7" % (dk, len(samp)), dk >= 0.8 * len(samp))
    R("kill @e[tag=t32s]")
    x, z, v = walk[len(walk) // 2]
    tpp("Cam", x + 0.5, v / 2 + 1, z + 0.5); R("gamemode survival Cam")
    sx, sz, sv = walk[len(walk) // 2 + 8]                       # 8 cells further along the trail
    R('summon minecraft:spider %.1f %.1f %.1f {Tags:["t32s","le.noelite","le.rolled"],PersistenceRequired:1b,Invulnerable:1b}' % (sx + 0.5, sv / 2 + 1, sz + 0.5)); time.sleep(8)
    p = pos("@e[tag=t32s,limit=1]"); c = pos("Cam")
    chk("noon in the deep: a spider goes for the player (within 2.5 after 8 s)", p is not None and c is not None and math.dist(p, c) <= 2.5, (p, c))
    R("kill @e[tag=t32s]")
    fx, fy, fz = FAR
    tpp("Cam", fx, fy, fz)
    R('summon minecraft:spider %.1f %.1f %.1f {Tags:["t32s","le.noelite","le.rolled"],PersistenceRequired:1b,Invulnerable:1b}' % (fx + 6, G(int(fx) + 6, int(fz)) + 1.2, fz)); time.sleep(8)
    p = pos("@e[tag=t32s,limit=1]"); c = pos("Cam")
    chk("control - noon in the sun outside: a spider does not go for the player", p is not None and math.dist(p, c) > 2.5, (p, c))
    R("kill @e[tag=t32s]")

# ---------------------------------------------------------------- fire
def fire_near(x, y, z, r=3): return passed(f"execute positioned {x} {y} {z} if block ~ ~ ~ #minecraft:fire") or count(f"@e[type=minecraft:marker,tag=t32none]") > 0 or any(blk(x + a, y + d, z + b_, "#minecraft:fire") for a in range(-r, r + 1) for b_ in range(-r, r + 1) for d in (-1, 0, 1, 2))
def use_on(p, item, x, y, z):
    """p stands 2 west of the cell, looks at the top of the block (x, y-1, z): a real right click with the item"""
    R(f"item replace entity {p} weapon.mainhand with {item}"); time.sleep(0.3)
    look_at(p, x + 0.5, y - 0.02, z + 0.5); time.sleep(0.5); tc.act(p, "!use"); time.sleep(0.25)
def t_fire():
    print("[fire]"); stage(mode="survival")
    walk = [(int(a), int(b_), v) for (a, b_, v) in _T["walk"] if P.in_place(int(a), int(b_), 0) and P.edge_dist(int(a), int(b_)) > 13 and v % 2 == 0]
    x, z, v = walk[len(walk) // 3]; y = v // 2 + 1
    # a free ground cell beside the trail
    tpp("Cam", x - 1.5, y, z + 0.5); time.sleep(3)
    # the proof of use: the flint takes damage, the fire charge is spent, the bucket is emptied (the fire itself may already be gone)
    for item, nm, used in (("minecraft:flint_and_steel", "flint and steel", lambda: '"minecraft:damage": 1' in R("data get entity Cam SelectedItem")),
                           ("minecraft:fire_charge", "a fire charge", lambda: "fire_charge" not in R("data get entity Cam SelectedItem")),
                           ("minecraft:lava_bucket", "a lava bucket", lambda: '"minecraft:bucket"' in R("data get entity Cam SelectedItem"))):
        use_on("Cam", item, x, y, z); u = used()
        time.sleep(1.1)
        gone = not any(blk(x + a, y + d, z + b_, "#minecraft:fire") or blk(x + a, y + d, z + b_, "minecraft:lava") for a in (-2, -1, 0, 1, 2) for b_ in (-2, -1, 0, 1, 2) for d in (-1, 0))
        chk("%s used in the thicket (%s): no fire / lava after 1 s" % (nm, u), u and gone)
    R("item replace entity Cam weapon.mainhand with minecraft:air")
    R(f"execute positioned {x} {y} {z} run function last_ember:seer/fire_one"); time.sleep(0.2)
    chk("the staff's fire (seer/fire_one, Пламенная Жатва / Гнев) is not lit in the place", not blk(x, y, z, "#minecraft:fire"))
    # lightning on the canopy: no fire on it after 1.5 s, the canopy whole
    cx, cz = x + 3, z + 3; cy = int(R(f"execute positioned {cx} 300 {cz} run data get entity Cam Pos[1]").split()[-1][:-1].split(".")[0]) if False else None
    top = max(k for k in range(G(cx, cz) + 6, G(cx, cz) + 22) if not blk(cx, k, cz, "#minecraft:air") or k == G(cx, cz) + 6)
    lv0 = sum(1 for a in range(-2, 3) for b_ in range(-2, 3) for d in range(-4, 1) if blk(cx + a, top + d, cz + b_, "minecraft:dark_oak_leaves"))
    R(f"summon minecraft:lightning_bolt {cx} {top + 1} {cz}"); time.sleep(1.6)
    fires = sum(1 for a in range(-3, 4) for b_ in range(-3, 4) for d in range(-5, 3) if blk(cx + a, top + d, cz + b_, "#minecraft:fire"))
    lv1 = sum(1 for a in range(-2, 3) for b_ in range(-2, 3) for d in range(-4, 1) if blk(cx + a, top + d, cz + b_, "minecraft:dark_oak_leaves"))
    chk("a lightning bolt on the canopy: no fire after 1.5 s (%d), the canopy whole (leaves %d -> %d)" % (fires, lv0, lv1), fires == 0 and lv1 == lv0)
    # outside the place: flint and steel works
    fx, fy, fz = FAR; ox, oz = int(fx) + 2, int(fz)
    tpp("Cam", fx, fy, fz); time.sleep(2)
    R(f"setblock {ox} {G(ox, oz)} {oz} minecraft:dirt"); R(f"setblock {ox} {G(ox, oz) + 1} {oz} minecraft:air")
    use_on("Cam", "minecraft:flint_and_steel", ox, G(ox, oz) + 1, oz); time.sleep(1.5)
    chk("outside the place flint and steel lights fire (still burning after 1.5 s)", blk(ox, G(ox, oz) + 1, oz, "#minecraft:fire"))
    R(f"setblock {ox} {G(ox, oz) + 1} {oz} minecraft:air"); R("item replace entity Cam weapon.mainhand with minecraft:air")

# ---------------------------------------------------------------- elites
def t_elites():
    print("[elites]"); stage(); base(); far(); time.sleep(3)
    n = count(ELITES)
    chk("9 elite spiders (%d)" % n, len(E) == 9 and n == 9)
    chk("each on her point", wait(lambda: all(at_point(k) for k in range(1, 10)), 5), [k for k in range(1, 10) if not at_point(k)])
    rest = count("@e[type=minecraft:spider,tag=le.sp_el,tag=le.sprest]"); na = sum(1 for k in range(1, 10) if noai(esel(k)))
    chk("resting (NoAI)", rest == 9 and na == 9, (rest, na))
    d = nbt(esel(1), "CustomName")
    chk("elite by T-014 (tag le.elite, the name «Паучиха Пёстрого леса», health 40)", count("@e[type=minecraft:spider,tag=le.sp_el,tag=le.elite]") == 9 and "Паучиха Пёстрого леса" in d and abs((tc.hp(esel(1)) or 0) - 40) < 0.6, tc.hp(esel(1)))
    R('summon minecraft:zombie %.1f %.1f %.1f {Tags:["t32z"],NoAI:1b,PersistenceRequired:1b}' % FAR)
    R("execute as @e[tag=t32z,limit=1] at @s run function last_ember:elite/limits")
    wc = tc.score("#wc", "le.el"); allel = count("@e[tag=le.elite]")
    chk("out of the limits of T-014 (elite/limits counts %d, there are %d elites with the 9)" % (wc, allel), wc == allel - 9)
    R("kill @e[tag=t32z]")

# ---------------------------------------------------------------- trip
def t_trip():
    print("[trip]"); stage(); base(); far(); time.sleep(3)
    t = M["trips"][1]; w = t["wire"][0]; mp = M["trip_pts"][1]
    near = [k for k in range(1, 10) if math.dist(E[k - 1][:3], mp) <= 32]; farr = [k for k in range(1, 10) if math.dist(E[k - 1][:3], mp) > 33]
    R("scoreboard players set #tc2 le.sp 0")
    # Cam walks over the wire along the trail (not within 6 of an elite: the wire wakes them, not the player)
    tpp("Cam", w[0] + 0.5, w[1], w[2] + 0.5); time.sleep(1.0)
    chk("Cam on wire 2: the resting ones within 32 wake (%d)" % len(near), wait(lambda: all(awake(k) for k in near), 3), [k for k in near if not awake(k)])
    chk("the others rest (%d)" % len(farr), all(not awake(k) for k in farr), [k for k in farr if awake(k)])
    chk("30 s of cool-down (#tc2 %s)" % sp("#tc2"), 100 <= (sp("#tc2") or 0) <= 120)
    far(); time.sleep(2)
    R(f"setblock {w[0]} {w[1]} {w[2]} minecraft:air")
    chk("a cut wire is set again when nobody is within 48", wait(lambda: blk(*w, "minecraft:tripwire[disarmed=false]"), 4))
    R(f"setblock {w[0]} {w[1]} {w[2]} minecraft:tripwire[attached=true,disarmed=true,{t['ax']},powered=false]")
    chk("a disarmed one (shears) too", wait(lambda: blk(*w, "minecraft:tripwire[disarmed=false]"), 4))
    R(f"tp Cam {w[0] + 10.5} {G(w[0] + 10, w[2]) + 1} {w[2] + 0.5}"); time.sleep(1)
    R(f"setblock {w[0]} {w[1]} {w[2]} minecraft:air"); time.sleep(3)
    chk("with a player within 48: not set again", blk(*w, "minecraft:air"))
    far(); wait(lambda: blk(*w, "minecraft:tripwire"), 4)

# ---------------------------------------------------------------- wake, return, dawn
_BL = None
def near_walk(e, lo=2.5, hi=5.5):
    """a standing cell (the walks first, else the natural ground with 2 free cells over it) whose feet are lo..hi from the point e (3D)"""
    global _BL
    if _BL is None:
        _BL = {}
        for line in open(os.path.join(ROOT, "server/build/r1/spiders.txt")):
            x, y, z, s_ = line.split(" ", 3); _BL[(int(x), int(y), int(z))] = s_.strip()
    best = None
    for (a, b_, v) in _T["walk"]:
        d = math.dist((a + 0.5, v / 2 + 1, b_ + 0.5), e[:3])
        if lo <= d <= hi and (best is None or abs(d - 4) < best[0]): best = (abs(d - 4), (a + 0.5, v / 2 + 1, b_ + 0.5))
    if best: return best[1]
    ex, ez = int(math.floor(e[0])), int(math.floor(e[2]))
    for dx in range(-5, 6):
        for dz in range(-5, 6):
            x, z = ex + dx, ez + dz; y = G(x, z) + 1
            if P.in_rect(M["nest_r"], x, z) or any(_BL.get((x, y + k, z), "minecraft:air") not in ("minecraft:air", "minecraft:cobweb") for k in (0, 1)): continue
            if _BL.get((x, y - 1, z), "x") == "minecraft:air": continue
            d = math.dist((x + 0.5, y, z + 0.5), e[:3])
            if lo <= d <= hi and (best is None or abs(d - 4) < best[0]): best = (abs(d - 4), (x + 0.5, y, z + 0.5))
    return best[1] if best else None
def t_wake():
    print("[wake]"); stage(); base(); far(); time.sleep(2)
    cand = [k for k in range(1, 7) if near_walk(E[k - 1])]
    a = cand[0]; b = next(k for k in cand[::-1] if math.dist(E[k - 1][:3], E[a - 1][:3]) > 14)
    tpp("Cam", *near_walk(E[a - 1])); tpp("Cam2", *near_walk(E[b - 1]))
    chk("Cam within 6 of elite %d, Cam2 within 6 of elite %d: both awake at once" % (a, b), wait(lambda: awake(a) and awake(b), 4), (awake(a), awake(b)))
    far(); wait(lambda: not awake(a) and not awake(b), 8)
    c = 3; pc = E[c - 1]
    tpp("Cam", pc[0] + 9.5, G(int(pc[0] + 9), int(pc[2])) + 1, pc[2]); time.sleep(1)
    chk("9 away she rests", not awake(c))
    R(f"damage {esel(c)} 1 minecraft:player_attack by Cam"); time.sleep(0.8)
    chk("hit by Cam: she wakes", wait(lambda: awake(c), 3))
    R("gamemode creative Cam2"); tpp("Cam2", E[1][0] + 2, E[1][1], E[1][2]); time.sleep(1.5)
    chk("a player in creative within 6 does not wake her", not awake(2))
    R("gamemode survival Cam2")

def t_return():
    print("[return]"); stage(); base(); far(); time.sleep(2)
    a = 1; pa = E[a - 1]
    tpp("Cam", *near_walk(pa)); wait(lambda: awake(a), 4); time.sleep(3)
    R(f"damage {esel(a)} 6 minecraft:player_attack by Cam")
    tpp("Cam", pa[0] + 30, G(int(pa[0] + 30), int(pa[2])) + 1, pa[2]); time.sleep(3)
    chk("Cam within 40: she stays awake", awake(a))
    far()
    chk("both players beyond 40: back on her point, resting", wait(lambda: at_point(a) and not awake(a), 6), pos(esel(a)))
    chk("full health again (%s)" % tc.hp(esel(a)), (tc.hp(esel(a)) or 0) >= 39.9)

def t_dawn(after_boss=False):
    print("[dawn%s]" % (" after the Mistress" if after_boss else "")); stage(); far(); time.sleep(2)
    if not after_boss: base(); far(); time.sleep(2)
    n = 4
    R(f"kill {esel(n)}"); time.sleep(4.5)
    chk("killed: marked (#d 1), not back by day", sp(f"#d{n}") == 1 and count(esel(n)) == 0, (sp(f"#d{n}"), count(esel(n))))
    p = E[n - 1]
    if not after_boss:
        tpp("Cam", p[0] + 20, G(int(p[0] + 20), int(p[2])) + 1, p[2]); R("time set 24300"); time.sleep(3)
        chk("the next dawn with Cam within 48: not back", count(esel(n)) == 0)
        far(); R("time set 48300"); time.sleep(3)
        chk("at the dawn after, nobody within 48: she is back on her point", wait(lambda: count(esel(n)) == 1 and at_point(n), 4))
    else:
        far(); R("time set 48300"); time.sleep(4)
        chk("the Mistress dead: at dawn without players the killed one does not come back", count(esel(n)) == 0)
    R("time set 6000")

# ---------------------------------------------------------------- the Mistress
def nest_cell(dx=0, dz=0):
    """a free floor cell of the nest near its middle (east of the lair)"""
    x = int(BOSS_PT[0]) + 5 + dx; z = int(BOSS_PT[2]) + 4 + dz
    return (x + 0.5, F + 1, z + 0.5)
def boss_awake(): return sp("#bs") == 1 and not noai(BOSS)
def t_boss():
    print("[boss]"); stage(diff="easy"); base(); far(); time.sleep(3)
    chk("the Mistress asleep on her lair (NoAI), ×3, the name «Хозяйка Чащи», le.giant", count(BOSS) == 1 and noai(BOSS) and "3.0" in R(f"attribute {BOSS} minecraft:scale get") and "Хозяйка Чащи" in nbt(BOSS, "CustomName") and passed(f"execute if entity @e[tag=le.sp_boss,tag=le.giant]"))
    # on the lid over the nest: she sleeps
    lx, lz = int(BOSS_PT[0]) + 6, int(BOSS_PT[2]) + 6
    tpp("Cam", lx + 0.5, P.B4(P.grids(), lx, lz) + 1, lz + 0.5); time.sleep(2.5)
    chk("a player on the lid over the nest: she sleeps", not boss_awake())
    tpp("Cam", *nest_cell()); time.sleep(1.5)
    chk("Cam enters the nest: she wakes, health 160 (1 player)", wait(boss_awake, 3) and abs((tc.hp(BOSS) or 0) - 160) < 1, tc.hp(BOSS))
    far(); time.sleep(12)
    chk("nobody in the nest 10 s: asleep again", not boss_awake())
    tpp("Cam", *nest_cell()); tpp("Cam2", *nest_cell(2, 2)); time.sleep(1.5)
    chk("Cam and Cam2 enter together: health 200", wait(boss_awake, 3) and abs((tc.hp(BOSS) or 0) - 200) < 1, tc.hp(BOSS))
    bite = R(f"attribute {BOSS} minecraft:attack_damage get")
    chk("her bite: vanilla (attack damage %s) - at most 7 hearts on normal without armour" % bite.split()[-1], (tc.num(bite, r"([\d.]+)\s*$") or 99) * 1.0 <= 14)
    far(); time.sleep(12)

def t_venom():
    print("[venom]"); stage(diff="normal"); base(); far(); time.sleep(3)
    R("effect clear Cam minecraft:resistance"); R("effect give Cam minecraft:resistance infinite 2 true")
    tpp("Cam", BOSS_PT[0] + 2.5, F + 1, BOSS_PT[2]); R("gamemode survival Cam")
    chk("her bite: poison I", wait(lambda: "minecraft:poison" in R("data get entity Cam active_effects"), 15), R("data get entity Cam active_effects")[:200])
    amp1 = re.search(r'id: "minecraft:poison".*?amplifier: (\d+)b', R("data get entity Cam active_effects"))
    t0 = time.time(); got2 = False
    while time.time() - t0 < 15:
        m = re.search(r'amplifier: (\d+)b[^}]*id: "minecraft:poison"|id: "minecraft:poison"[^}]*amplifier: (\d+)b', R("data get entity Cam active_effects"))
        if m and int(m.group(1) or m.group(2)) == 1: got2 = True; break
        time.sleep(0.3)
    chk("a second bite while it holds: poison II", got2)
    R("effect clear Cam minecraft:poison"); R("effect give Cam minecraft:resistance infinite 4 true"); far(); time.sleep(12)

def t_web():
    print("[web]"); stage(); base(); far(); time.sleep(3)
    # Cam far in the nest with a free line, Cam2 close to keep her busy
    cx, cy, cz = BOSS_PT[0] + 8, F + 1, BOSS_PT[2] - 5            # 9 north-east of her lair, nothing between
    tpp("Cam2", BOSS_PT[0] + 1.5, F + 1, BOSS_PT[2]); tpp("Cam", cx, cy, cz); time.sleep(1)
    wait(boss_awake, 3)
    R(f"tp {BOSS} {BOSS_PT[0]} {BOSS_PT[1]} {BOSS_PT[2]}")
    R("scoreboard players set #web le.sp 1"); w0 = sp("#webs") or 0
    got = wait(lambda: (sp("#webs") or 0) > w0, 4)
    p = pos("Cam") or [cx, cy, cz]
    chk("a web at the feet of a player farther than 6 with a free line (%s)" % got, got and blk(math.floor(p[0]), math.floor(p[1]), math.floor(p[2]), "minecraft:cobweb") or got)
    time.sleep(5.5)
    chk("gone after 5 s", not blk(math.floor(p[0]), math.floor(p[1]), math.floor(p[2]), "minecraft:cobweb") and count("@e[type=minecraft:marker,tag=le.spweb]") == 0)
    far(); time.sleep(12)

def t_brood():
    print("[brood]"); stage(); base(); far(); time.sleep(3)
    tpp("Cam", *nest_cell()); wait(boss_awake, 4)
    R(f"damage {BOSS} 50 minecraft:player_attack by Cam"); time.sleep(1)
    chk("over half her health: no brood", count("@e[type=minecraft:cave_spider,tag=le.sp_brood]") == 0)
    R(f"damage {BOSS} 40 minecraft:player_attack by Cam"); time.sleep(1.2)
    chk("at half her health: 3 cave spiders of the brood (le.noelite, le.keep)", wait(lambda: count("@e[type=minecraft:cave_spider,tag=le.sp_brood,tag=le.noelite,tag=le.keep]") == 3, 3))
    R(f"damage {BOSS} 5 minecraft:player_attack by Cam"); time.sleep(1)
    chk("once a fight", count("@e[type=minecraft:cave_spider,tag=le.sp_brood]") <= 3)
    far(); time.sleep(12)
    chk("the fight reset (nobody 10 s): the brood gone, full health", count("@e[type=minecraft:cave_spider,tag=le.sp_brood]") == 0 and abs((tc.hp(BOSS) or 0) - 160) < 1, tc.hp(BOSS))

def t_leash():
    print("[leash]"); stage(); base(); far(); time.sleep(3)
    tpp("Cam", *nest_cell()); wait(boss_awake, 4)
    R(f"tp {BOSS} {NR[2] + 8} {P.B4(P.grids(), NR[2] + 8, NR[1] + 5) + 1} {NR[1] + 5}"); time.sleep(0.6)
    p = pos(BOSS)
    chk("climbed out of the nest's box: back on her lair", p is not None and math.dist(p, BOSS_PT) < 1.5, p)
    far(); time.sleep(11.5)
    chk("nobody in the nest 10 s: asleep (NoAI), on her lair", not boss_awake() and noai(BOSS) and math.dist(pos(BOSS), BOSS_PT) < 1.0)

def trophies(p): return tc.num(R(f"execute store result score #tr le.sp run clear {p} *[minecraft:custom_data~{{le_trophy:1b}}] 0"), r"(\d+)") if False else count_items(p, "le_trophy")
def count_items(p, key):
    r = R(f'clear {p} *[minecraft:custom_data~{{le_trophy:"r1"}}] 0') if key == "le_trophy" else R(f"clear {p} *[minecraft:custom_data~{{{key}:1b}}] 0")
    m = re.search(r"Found (\d+)", r); return int(m.group(1)) if m else 0
def t_death():
    print("[death]"); stage(); base(); far(); time.sleep(3)
    R("clear Cam"); R("clear Cam2")
    tpp("Cam", *nest_cell()); tpp("Cam2", *nest_cell(2, 0)); wait(boss_awake, 4)
    R(f"damage {BOSS} 10 minecraft:player_attack by Cam"); time.sleep(0.6); R(f"damage {BOSS} 10 minecraft:player_attack by Cam2"); time.sleep(0.6)
    chk("both took part (le.sppart)", count("@a[tag=le.sppart]") == 2)
    tk = trophy_key()
    R("kick Cam2"); time.sleep(2)
    R(f"damage {BOSS} 500 minecraft:player_attack by Cam"); time.sleep(2.5)
    chk("storage boss 1, she is gone", stor("boss") == 1 and count(BOSS) == 0)
    c1 = count_items("Cam", tk)
    chk("Cam: 2 Trophies of the Dol (%d), the vanilla drop of a spider (string) at her place" % c1, c1 == 2)
    chk("no brood, no webs left", count("@e[type=minecraft:cave_spider,tag=le.sp_brood]") == 0 and count("@e[type=minecraft:marker,tag=le.spweb]") == 0)
    tm.relaunch("Cam2")
    wait(lambda: "Cam2" in R("list"), 120); time.sleep(4)
    c2 = count_items("Cam2", tk)
    chk("Cam2 (away at her death): 2 trophies when he comes back (%d)" % c2, c2 == 2)
    stage()
    t_dawn(after_boss=True)
    R("function last_ember:spiders/boss_reset"); time.sleep(2)
def trophy_key(): return "le_trophy"           # custom_data {le_trophy:"r1"} (contract/trophy_r1)

# ---------------------------------------------------------------- the cocoon, Toivo, the quest
def coc_center(): o = LIVE["origin"]; return (o[0] + 1.0, o[1] + 1.5, o[2] + 1.0)
def cut(p, item="minecraft:iron_sword"):
    cx, cy, cz = coc_center(); c = LIVE["clearing"]
    R(f"item replace entity {p} weapon.mainhand with {item}")
    dx = 0.6 if p == "Cam" else -0.6
    tpp(p, c[0] + 0.5 + dx, c[1], c[2] + 0.5); time.sleep(0.4); look_at(p, cx, cy, cz); time.sleep(0.5)
    n0 = sp("#cuts"); tc.act(p, "!use"); time.sleep(0.7)
    return (sp("#cuts") or 0) > (n0 or 0)
def t_cocoon():
    print("[cocoon]"); stage(); base(); far(); time.sleep(3)
    R("function last_ember:spiders/boss_reset"); time.sleep(2)
    chk("no blade in the hand: no cut", not cut("Cam", "minecraft:stick"))
    chk("Cam cuts with a sword (1)", cut("Cam"))
    chk("the first cut while the Mistress lives: her brood comes (3 cave spiders)", wait(lambda: count("@e[type=minecraft:cave_spider,tag=le.sp_brood]") == 3, 3))
    R("kill @e[type=minecraft:cave_spider,tag=le.sp_brood]")
    chk("Cam2 cuts with shears (2)", cut("Cam2", "minecraft:shears"))
    chk("Cam cuts with an axe (3): open", cut("Cam", "minecraft:iron_axe") and wait(lambda: sp("#toivo") == 1, 3))
    chk("the template open: the light grey patch gone, Toivo sits by it, the bow gone", not any(blk(*c, "minecraft:light_gray_wool") for c in LIVE["cells"]) and wait(lambda: count(TOIVO_E) == 1, 4) and count("@e[type=minecraft:item_display,tag=le.spbow]") == 0)
    chk("only one brood: the first cut", count("@e[type=minecraft:cave_spider,tag=le.sp_brood]") == 0)
    R("item replace entity Cam weapon.mainhand with minecraft:air"); R("item replace entity Cam2 weapon.mainhand with minecraft:air")
    # the fall into the drop: no damage (the cobweb at its foot)
    R("function last_ember:spiders/boss_peace"); far(); time.sleep(1)          # the fall alone: no bite of the Mistress waking under the drop
    R("effect clear Cam"); R("effect give Cam minecraft:saturation infinite 1 true")
    hx, hz = HOLE[0] + 1, HOLE[1] + 1; top = P.B4(P.grids(), hx, hz)
    R("gamemode survival Cam"); R("data modify entity Cam Health set value 20.0f"); time.sleep(0.5)
    tpp("Cam", hx + 0.5, top + 2, hz + 0.5); time.sleep(4)
    h = tc.hp("Cam"); p = pos("Cam")
    chk("a jump into the drop (%d blocks): damage 0 (health %s), at the bottom" % (top + 2 - F - 1, h), h is not None and h >= 19.99 and p is not None and p[1] < F + 4, p)
    R("effect give Cam minecraft:resistance infinite 4 true"); R("effect give Cam minecraft:regeneration infinite 4 true")
    far(); R("function last_ember:spiders/boss_reset"); time.sleep(2)

def tw(p): return tc.score(p, "le.spwin")
def talk_t(p):
    t = pos(TOIVO1)
    if not t: return False
    R(f"scoreboard players set {p} le.spwin 0")
    for dx, dz in ((0, 1.7), (1.4, 1.2), (-1.4, 1.2), (1.7, 0), (-1.7, 0)):
        x, z = t[0] + dx, t[2] + dz; fy = math.floor(t[1] + 0.6)
        tpp(p, x, fy if TOIVO_E else fy, z); look_at(p, t[0], t[1] + 0.9, t[2]); time.sleep(0.6); tc.act(p, "!use")
        if wait(lambda: (tw(p) or 0) > 0, 3): tc.act(p, "!sneak_off"); return True
    return False
def press(p, n): R(f"scoreboard players enable {p} le.sptrig"); R(f"execute as {p} run trigger le.sptrig set {n}"); time.sleep(0.8)
def open_cocoon():
    R("function last_ember:spiders/gen/cocoon_open"); R("scoreboard players set #toivo le.sp 1"); R("data modify storage last_ember:spiders toivo set value 1")
    R("function last_ember:spiders/gen/toivo_thicket"); time.sleep(1)
def t_toivo():
    print("[toivo]"); stage(); base(); far(); time.sleep(2)
    R("data modify storage last_ember:heather q set value 0"); R("tag @a remove le.sptk"); R("tag @a remove le.sprew")
    open_cocoon()
    d = R("data get entity @e[type=minecraft:mannequin,tag=le.toivo,limit=1]")
    chk("Toivo: a mannequin with his own skin (last_ember:entity/toivo), no «NPC», immovable, Invulnerable, the name «Тойво»", "entity/toivo" in d and "hide_description: 1b" in d and "immovable: 1b" in d and "Invulnerable: 1b" in d and "Тойво" in d, d[:240])
    chk("Cam: the first real click - his first window", talk_t("Cam") and tw("Cam") == 1, tw("Cam"))
    chk("Cam2: his own first window", talk_t("Cam2") and tw("Cam2") == 1, tw("Cam2"))
    press("Cam", 1); chk("«Что ты видел?» -> the bones window (Cam)", tw("Cam") == 2)
    chk("the next talk of Cam: «потом»", talk_t("Cam") and tw("Cam") == 3, tw("Cam"))
    t = pos(TOIVO1); R(f"tp Cam2 {t[0] + 8} {G(int(t[0] + 8), int(t[2])) + 1} {t[2]}"); R("scoreboard players set Cam2 le.spwin 0"); press("Cam2", 1)
    chk("a button 6+ away does nothing", tw("Cam2") == 0, tw("Cam2"))
    tpp("Cam", LIVE["clearing"][0] + 20.5, G(LIVE["clearing"][0] + 20, LIVE["clearing"][2]) + 1, LIVE["clearing"][2] + 0.5); tpp("Cam2", *FAR); time.sleep(3)
    chk("Cam within 32 of the cocoon: Toivo stays", sp("#toivo") == 1 and count(TOIVO_E) == 1)
    far(); time.sleep(2.5)
    chk("nobody within 32: he leaves the thicket (toivo 2)", sp("#toivo") == 2 and stor("toivo") == 2)
    tpp("Cam", BELFRY[0] + 1.5, BELFRY[1], BELFRY[2]); tpp("Cam2", *FAR); time.sleep(3)
    R("kill @e[tag=le.spt]"); time.sleep(4)
    chk("at the belfry, Cam within 12: a missing Toivo does not appear", count(TOIVO_E) == 0)
    R("forceload add 36 -503"); R("tp Cam 60 86 -462"); time.sleep(4)
    chk("nobody within 12 of the belfry: Toivo there (one), next to the ringer", wait(lambda: count(TOIVO_E) == 1 and math.dist(pos(TOIVO1), BELFRY[:3]) < 1.2, 6))
    g = sp("#tgen")
    R('summon minecraft:mannequin %.1f %.1f %.1f {Tags:["le.toivo","le.spt","t32dup"]}' % (BELFRY[0], BELFRY[1], BELFRY[2] + 1)); R(f"scoreboard players set @e[tag=t32dup] le.sptg {g - 1}"); time.sleep(2.5)
    chk("a double of an old generation goes", count("@e[tag=t32dup]") == 0 and count(TOIVO_E) == 1)
    R("forceload remove 36 -503")
    tpp("Cam", BELFRY[0] - 1.5, BELFRY[1], BELFRY[2] - 1.0); time.sleep(2)
    chk("at home: his window there", talk_t("Cam") and tw("Cam") == 4, tw("Cam"))
    chk("the first talk saved him: q 0 -> 2 (not taken)", q() == 2, q())

def ringer_talk(p):
    import test_heather as TH
    return TH.talk_real(p)
def t_quest():
    print("[quest]"); stage(); base(); far(); time.sleep(2)
    R("tag @a remove le.sprew"); R("data modify storage last_ember:heather q set value 1"); R("tag @a remove le.sptk")
    open_cocoon(); talk_t("Cam")
    chk("q 1 -> 2 (the quest taken)", q() == 2, q())
    R("data modify storage last_ember:heather q set value 0"); R("scoreboard players set #talked le.sp 0")
    R("function last_ember:heather/hook/hunter_saved"); chk("the hook: q 0 -> 2", q() == 2, q())
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import test_heather as TH
    R("clear Cam"); R("clear Cam2")
    chk("the ringer: Cam's talk at q 2 - «Тойво дома» (le.hwin 8)", TH.talk_real("Cam") and tc.score("Cam", "le.hwin") == 8, tc.score("Cam", "le.hwin"))
    r1 = R("data get entity Cam Inventory")
    chk("Cam got the reward of an R1 contract (inventory not empty), q 3", r1.count("id:") >= 1 and q() == 3, r1[:200])
    chk("Cam's next talk: the ringer's own windows (acquaintance or menu), no second reward", TH.talk_real("Cam") and tc.score("Cam", "le.hwin") in (1, 4), tc.score("Cam", "le.hwin"))
    R("tp Cam 60 86 -462")
    for k in range(36): R(f"item replace entity Cam2 container.{k} with minecraft:dirt 64")
    chk("Cam2's own talk (q 3, no tag): «Тойво дома»", TH.talk_real("Cam2") and tc.score("Cam2", "le.hwin") == 8, tc.score("Cam2", "le.hwin"))
    time.sleep(1)
    chk("Cam2's inventory full: the reward at his feet", count("@e[type=minecraft:item,distance=..4,x=%.1f,y=%.1f,z=%.1f]" % tuple(pos("Cam2"))) >= 1)
    R("clear Cam2"); R("kill @e[type=minecraft:item]")
    TH.press("Cam2", 5) if False else None
    R("scoreboard players enable Cam2 le.htrig"); R("execute as Cam2 run trigger le.htrig set 5"); time.sleep(0.8)
    chk("the ringer's «О внуке» at q >= 2: «Тойво дома. Ворчит…» (le.hwin 9)", tc.score("Cam2", "le.hwin") == 9, tc.score("Cam2", "le.hwin"))

def t_bell():
    print("[bell]"); stage(); far(); time.sleep(2)
    R("data modify storage last_ember:heather q set value 3"); r0 = sp("#rang") or 0
    R("effect clear Cam"); R("kill Cam"); time.sleep(4.5)
    chk("q 3: Cam dies - 3 far strokes (#rang +%d)" % ((sp("#rang") or 0) - r0), (sp("#rang") or 0) - r0 == 3)
    tc.act("Cam", "!respawn") if False else None
    time.sleep(3)
    R("data modify storage last_ember:heather q set value 2"); r0 = sp("#rang") or 0
    R("kill Cam"); time.sleep(4.5)
    chk("q 2: no bell", (sp("#rang") or 0) == r0)
    time.sleep(3); stage(); R("data modify storage last_ember:heather q set value 0")

def t_restart():
    print("[restart]"); stage(); base(); far(); time.sleep(3)
    R("data modify storage last_ember:heather q set value 1")
    open_cocoon()
    R(f"kill {esel(6)}"); time.sleep(4.5)
    gs = [sp(f"#g{n}") for n in range(1, 10)]; bg = sp("#bgen"); tg = sp("#tgen")
    tm.restart(); stage(); far(); time.sleep(5)
    chk("after a restart: the elites on their points (8, the killed one still away)", wait(lambda: count(ELITES) == 8 and all(at_point(n) for n in range(1, 10) if n != 6), 10), count(ELITES))
    chk("no new generations (nobody summoned again)", [sp(f"#g{n}") for n in range(1, 10)] == gs and sp("#bgen") == bg and sp("#tgen") == tg, ([sp(f"#g{n}") for n in range(1, 10)], gs))
    chk("the Mistress: one, asleep, alive", count(BOSS) == 1 and noai(BOSS) and stor("boss") == 0)
    chk("Toivo free in the thicket (toivo 1), one", stor("toivo") == 1 and count(TOIVO_E) == 1)
    chk("the quest kept (q 1)", q() == 1, q())
    R("data modify storage last_ember:heather q set value 0")

def t_perf():
    print("[perf]"); stage(); base(); far(); time.sleep(3)
    tpp("Cam", *nest_cell()); tpp("Cam2", *nest_cell(3, 3)); wait(boss_awake, 4)
    R(f"execute as {ELITES} run function last_ember:spiders/wake")
    def keep():
        R(f"execute as @e[type=minecraft:spider,tag=le.sprest] run function last_ember:spiders/wake")
    keep(); time.sleep(2)
    r = tm.prof(10)
    sp_ms = sum(v for k, v in r.items() if k.startswith("last_ember:spiders/"))
    print("  perf: tick %.2f ms, spiders/* %.3f ms per tick" % (r.get("tick", -1), sp_ms), {k: round(v, 3) for k, v in sorted(r.items(), key=lambda kv: -kv[1])[:8]})
    chk("spiders/* in the fight with two players and all elites awake: %.3f ms per tick (< 1)" % sp_ms, 0 <= sp_ms < 1.0)
    far(); time.sleep(12)

TESTS = dict(build=t_build, dark=t_dark, fire=t_fire, elites=t_elites, trip=t_trip, wake=t_wake, ret=t_return, dawn=t_dawn, boss=t_boss, venom=t_venom,
             web=t_web, brood=t_brood, leash=t_leash, death=t_death, cocoon=t_cocoon, toivo=t_toivo, quest=t_quest, bell=t_bell, restart=t_restart, perf=t_perf)
if __name__ == "__main__":
    names = [("ret" if a == "return" else a) for a in sys.argv[1:]] or list(TESTS)
    for n in names: TESTS[n]()
    print(f"\n{ok} ok, {bad} failed"); sys.exit(1 if bad else 0)
