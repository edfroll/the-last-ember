#!/usr/bin/env python3
"""T-030 checks on the R1 world (tools/build/rebuild.sh or world_cache.py redo grove): the Mushroom Grove of the Advisor. Clients Cam and
Cam2 in the game (real input through the dev agent: !use on the Advisor; the buttons of the windows run `trigger le.atrig set N` as the
player, the same command the button sends). The last window shown to a player: score le.awin (1 intro, 2 menu day, 3 menu night, 4 after,
5 circle, 12..17 the answers to the buttons 2..7).
  build    the house (door, hearth, chair, lectern with «Счёт звёзд», chiseled shelves, pots, bee nest), 9 giants, the faces closed, no snow
           and no vanilla trees in the circle, the light of the walks (grove.json), the biome, the zone line
  advisor  one Advisor: the skin of the pack, the name, no «NPC», the pipe; a double goes; the missing one comes back; peaceful keeps him
  day      day -> night: he goes to the observatory when nobody is within 12; with Cam by him he stays; night -> day back to the armchair
  talk     Cam: the first real click = the acquaintance, the second = the menu; Cam2 his own acquaintance
  menu     every button opens its window; a button 10 away does nothing; Cam and Cam2 press at once; at night the night menu
  circle   the four keys of chapter I taken -> at the west arch of the Circle, his window there (real click); chapter I done -> back in the
           grove (the window "after"); altar/reset {chapter:1} and the keys again -> at the Circle again
  fade     the fading of chapter I: the biome of the grove stays, bonfire 10 burns, the window "after"
  faces    grove/faces_open / faces_close put the templates (6 eyes of verdant froglight / none)
  zones    adventure in the grove, nothing breaks (a real attack), a zombie in the zone goes
  restart  after a restart: one Advisor on his point, the acquaintance is not repeated
  perf     two players in the grove (night, the move, the smoke): grove/* by the profiler
Usage: python3 tools/test_grove.py [build advisor day talk menu circle fade faces zones restart perf]"""
import importlib.util, json, math, os, re, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
R = rc.run
ok = bad = 0
class tm:   # the restart, the profiler and tick query of tools/test_maze.py (that module runs its suites on import)
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
    def mspt():
        m = re.search(r"([0-9.]+)\s*ms", R("tick query")); return float(m.group(1)) if m else None
    @staticmethod
    def prof(sec=10, during=None):
        import glob, zipfile
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
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n, flush=True)
    else: bad += 1; print("  FAIL", n, e, flush=True)
M = json.load(open(os.path.join(ROOT, "server/build/r1/grove.json")))
PT = M["advisor_points"]; HX, HZ = M["house"]; L = M["L"]
PAD = (-404.5, 137, 75.5)                          # on the pad of bonfire 10, > 12 from the day and the night point
CIRCLE_FL = "forceload add -446 -189 -438 -181"
ADV = "@e[type=minecraft:mannequin,tag=le.advisor]"
ADV1 = "@e[type=minecraft:mannequin,tag=le.advisor,limit=1]"
def passed(cmd): return "passed" in R(cmd)
def pos(sel):
    v = re.findall(r"(-?\d+\.?\d*)d", R(f"data get entity {sel} Pos")); return [float(x) for x in v] if len(v) == 3 else None
def wait(cond, t=10.0, step=0.4):
    t0 = time.time()
    while time.time() - t0 < t:
        if cond(): return True
        time.sleep(step)
    return cond()
def count(sel):
    m = re.search(r"Count: (\d+)", R(f"execute if entity {sel}")); return int(m.group(1)) if m else 0
def blk(x, y, z, b): return passed(f"execute if block {x} {y} {z} {b}")
def gv(k): return tc.score(k, "le.grv")
def win(p): return tc.score(p, "le.awin")
def at(k, d=1.2):
    p = pos(ADV1); q = PT[k]
    return p is not None and math.dist(p, q[:3]) <= d
def where():
    p = pos(ADV1)
    if p is None: return None
    for k, q in PT.items():
        if math.dist(p, q[:3]) <= 1.2: return k
    return p
def look_at(p, x, y, z): R(f"execute as {p} at @s anchored eyes run tp @s ~ ~ ~ facing {x} {y} {z}")
def stage(night=False, mode="adventure"):
    for p in ("Cam", "Cam2"):
        if not passed(f"execute if entity @a[name={p},tag=le.cinit]"): tc.setc(1, 1, 0, p)
        R(f"gamemode {mode} {p}"); R(f"effect give {p} minecraft:resistance infinite 4 true"); R(f"effect give {p} minecraft:saturation infinite 1 true")
        R(f"execute as {p} run function last_ember:sleep/set_awake {{ticks:0}}")
    R("weather clear 100000"); R("gamerule advance_time false"); R("difficulty easy"); R("time set " + ("18000" if night else "6000"))
    R(f"tp Cam {PAD[0]} {PAD[1]} {PAD[2]}"); R(f"tp Cam2 {PAD[0] + 2} {PAD[1]} {PAD[2]}")
    wait(lambda: passed("execute if loaded %d 0 %d" % (HX, HZ)), 30); time.sleep(2)
def base_state():
    """chapter I not done, no key taken, the Advisor free on the day point, everybody's acquaintance again"""
    R("function last_ember:altar/set_chapters {n:0}"); R("clear Cam minecraft:ominous_trial_key"); R("clear Cam2 minecraft:ominous_trial_key"); time.sleep(0.6)
    for k in ("signet_king", "tear_creaker", "crown_witches", "thread_labyrinth"): R(f"data modify storage last_ember:keys k.{k}.got set value 0b")
    R("function last_ember:grove/reset"); time.sleep(2.5)
def talk_real(p, tries=4):
    """a real right click on the Advisor: stand 1.6 in front of him (a free cell), look at his chest, !use (repeated: the cloud client is slow)"""
    other = "Cam2" if p == "Cam" else "Cam"
    R(f"tp {other} {PAD[0]} {PAD[1]} {PAD[2]}")              # not between the clicker and the Advisor
    for _ in range(tries):
        a = pos(ADV1)
        if not a: return False
        R(f"scoreboard players set {p} le.awin 0")
        for dx, dz in ((1.6, 0), (0, 1.6), (-1.6, 0), (0, -1.6), (1.2, 1.2), (-1.2, 1.2)):
            x, z = a[0] + dx, a[2] + dz; fy = math.floor(a[1] + 0.01)
            if blk(math.floor(x), fy, math.floor(z), "#minecraft:air") and blk(math.floor(x), fy + 1, math.floor(z), "#minecraft:air"):
                R(f"tp {p} {x:.2f} {fy} {z:.2f}"); look_at(p, a[0], a[1] + 1.0, a[2]); time.sleep(0.6); tc.act(p, "!use")
                if wait(lambda: (win(p) or 0) > 0, 3): return True
                break
    return False
def press(p, n): R(f"scoreboard players enable {p} le.atrig"); R(f"execute as {p} run trigger le.atrig set {n}"); time.sleep(0.8)
def away():
    R(f"tp Cam {PAD[0]} {PAD[1]} {PAD[2]}"); R(f"tp Cam2 {PAD[0] + 2} {PAD[1]} {PAD[2]}")

# ---------------------------------------------------------------- build
def t_build():
    print("[build]"); stage()
    subprocess.run("cd %s && tools/server.sh rcon 'save-all flush'" % ROOT, shell=True, capture_output=True); time.sleep(3)
    sys.path.insert(0, os.path.join(ROOT, "tools/build")); import grove_plan as P, r1_grove as RG
    snow = RG.world_scan(RG.SNOW, lambda x, z: P.in_circle(x, z) and not P.on_pad(x, z))
    trees = RG.world_scan(RG.VANILLA_TREE, lambda x, z: P.in_circle(x, z) and not P.on_pad(x, z))
    chk("no snow and no vanilla tree blocks in the circle", not snow and not trees, (snow + trees)[:4])
    d = M["door"]; ch = M["chair"]; hh = M["hearth"]; lc = M["lectern"]
    chk("the round door (spruce), the hearth burning, the armchair", wait(lambda: blk(d[0], d[1], d[2], "minecraft:spruce_door") and blk(*hh, "minecraft:campfire[lit=true]") and blk(*ch, "minecraft:spruce_stairs"), 4),
        [blk(d[0], d[1], d[2], "minecraft:spruce_door"), blk(*hh, "minecraft:campfire[lit=true]"), blk(*ch, "minecraft:spruce_stairs")])
    book = R("data get block %d %d %d Book" % tuple(lc))
    chk("the lectern holds «Счёт звёзд» by the Advisor (3 pages)", "Счёт звёзд" in book and "Советчик" in book and book.count("raw:") == 4, book[:160])
    shelves = [blk(HX + dx, L + 2, HZ - 3, "minecraft:chiseled_bookshelf") for dx in (-2, 2)]
    chk("two chiseled bookshelves in the study", all(shelves), shelves)
    pots = sum(1 for p in M["pots"] if not blk(*p, "minecraft:air"))
    chk("8..10 pots (decorated and flower pots)", 8 <= pots <= 10 and pots == len(M["pots"]), pots)
    nest = M["garden"]["nest"]
    def bees(): return R("data get block %d %d %d bees" % tuple(nest)).count("entity_data") + count("@e[type=minecraft:bee,tag=le.gbee]")
    chk("the bee nest of the garden: 2 bees (in the nest + out)", wait(lambda: bees() == 2, 4), bees())
    R("execute as @e[type=minecraft:bee,tag=le.gbee,limit=1] run tp @s %d 140 %d" % (nest[0] - 60, nest[2])); time.sleep(2.5)
    chk("a bee strayed 60 away comes back by the nest; still 2", bees() == 2 and count("@e[type=minecraft:bee,tag=le.gbee,x=%d,y=%d,z=%d,distance=40..]" % tuple(nest)) == 0, bees())
    gi = sum(1 for g in M["giants"] if blk(g["x"], g["lo"] + 1, g["z"], "minecraft:mushroom_stem") and not blk(g["cap"][0] + g["cap"][3] - 1, g["cap"][1], g["cap"][2], "minecraft:air"))
    chk("9 giant mushrooms (stems standing)", len(M["giants"]) == 9 and gi == 9, gi)
    sys.path.insert(0, os.path.join(ROOT, "tools/build")); import grove_dp
    closed = sum(1 for f in M["faces"] if blk(*grove_dp.eye_cell(f), "minecraft:stripped_poplar_log"))
    chk("6 faces, eyes closed", len(M["faces"]) == 6 and closed == 6, closed)
    lt = M["light"]
    chk("light >= 1 on every walked cell (path, terrace, garden, approaches, the study): %d cells, the circle %d of %d" % (lt["must"], lt["rest"] - lt["rest_dark"], lt["rest"]), lt["must_dark"] == 0)
    bio = [passed(f"execute positioned {x} {y} {z} if biome ~ ~ ~ last_ember:mushroom_grove") for (x, y, z) in ((-420, 130, 60), (HX, L + 2, HZ), (-404, 138, 72))]
    chk("the biome mushroom_grove (centre, house, bonfire 10)", all(bio), bio)
    z = open(os.path.join(ROOT, "zones/zones.txt")).read()
    chk("the zone grove (cylinder r 45, no_spawn)", re.search(r"^grove\s+overworld cyl -420 60 45 \d+ \d+\s+no_spawn", z, re.M) is not None)

# ---------------------------------------------------------------- the Advisor himself
def t_advisor():
    print("[advisor]"); stage(); base_state(); away()
    chk("one Advisor, in the armchair by day", wait(lambda: count(ADV) == 1 and at("day"), 6), (count(ADV), where()))
    d = R(f"data get entity {ADV1}")
    chk("the skin of the pack (profile texture last_ember:entity/advisor), the name always shown, no «NPC» line, immovable, invulnerable",
        'texture: "last_ember:entity/advisor"' in d and "Советчик" in d and "CustomNameVisible: 1b" in d and "hide_description: 1b" in d and "immovable: 1b" in d and "Invulnerable: 1b" in d, d[:300])
    chk("the pipe in his hand by day", "last_ember:advisor_pipe" in d)
    chk("he sits (rides the seat of the armchair)", count("@e[type=minecraft:armor_stand,tag=le.aseat]") == 1 and passed(f"execute as {ADV} on vehicle if entity @s[tag=le.aseat]"))
    R("damage %s 40 minecraft:player_attack" % ADV1); R(f"execute as {ADV} at @s run tp @s ~1 ~ ~"); time.sleep(2)
    chk("hurt and pushed: one Advisor, back on his point", count(ADV) == 1 and wait(lambda: at("day"), 4), where())
    g = gv("#agen")
    R("execute positioned %.2f %.2f %.2f run summon minecraft:mannequin ~ ~ ~ {Tags:[\"le.advisor\",\"le.advent\",\"t30dup\"]}" % (HX + 1.5, L + 1, HZ + 1.5))
    R(f"scoreboard players set @e[tag=t30dup] le.agen {g - 1}"); time.sleep(2.2)
    chk("a double (old generation, as from a chunk not loaded) goes", count(ADV) == 1 and count("@e[tag=t30dup]") == 0)
    R("kill @e[tag=le.advent]"); time.sleep(0.5)
    chk("the missing Advisor comes back on his point (2 s)", wait(lambda: count(ADV) == 1 and at("day"), 6), where())
    R("difficulty peaceful"); time.sleep(3)
    chk("peaceful: the Advisor stays", count(ADV) == 1 and at("day"))
    R("difficulty easy")

# ---------------------------------------------------------------- day / night
def t_day():
    print("[day]"); stage(); base_state(); away()
    wait(lambda: at("day"), 5)
    R("time set 13000")
    chk("night, nobody within 12: to the observatory", wait(lambda: at("night"), 6), where())
    chk("at night the pipe lies on the armrest (item display), not in his hand", count("@e[type=minecraft:item_display,tag=le.advpipe]") == 1 and "advisor_pipe" not in R(f"data get entity {ADV1} equipment"))
    n = PT["night"]; R(f"tp Cam {n[0] - 2} {n[1]} {n[2]}"); R("time set 1000"); time.sleep(3)
    chk("day with Cam 2 from him: he stays in the observatory", at("night"), where())
    away(); R(f"tp Cam {PT['day'][0] + 3} {PT['day'][1]} {PT['day'][2] + 2}"); time.sleep(3)
    chk("day, Cam by the armchair (the new point): he still stays", at("night"), where())
    away()
    chk("nobody within 12 of either point: back in the armchair", wait(lambda: at("day"), 5), where())

# ---------------------------------------------------------------- talk / menu
def t_talk():
    print("[talk]"); stage(); base_state(); away(); wait(lambda: at("day"), 5)
    chk("Cam: a real click on the Advisor -> the acquaintance", talk_real("Cam") and win("Cam") == 1 and passed("execute if entity @a[name=Cam,tag=le.amet]"), win("Cam"))
    time.sleep(1); tc.act("Cam", "!sneak_off")
    chk("Cam: the second click -> the day menu", talk_real("Cam") and win("Cam") == 2, win("Cam"))
    chk("Cam2: his own acquaintance", talk_real("Cam2") and win("Cam2") == 1, win("Cam2"))
    chk("Cam2: then the menu", talk_real("Cam2") and win("Cam2") == 2, win("Cam2"))

def t_menu():
    print("[menu]"); stage(); base_state(); away(); wait(lambda: at("day"), 5)
    a = PT["day"]
    R(f"tp Cam {a[0] + 2} {L + 1} {a[2] + 1}"); R(f"tp Cam2 {a[0] + 2} {L + 1} {a[2] + 2}")
    res = {}
    for n in range(2, 8): press("Cam", n); res[n] = win("Cam")
    chk("every button opens its window (2..7 -> 12..17)", res == {n: 10 + n for n in range(2, 8)}, res)
    press("Cam", 1)
    chk("«Ещё»/«Расспросить» -> the menu (day)", win("Cam") == 2, win("Cam"))
    R("scoreboard players enable Cam le.atrig"); R("scoreboard players enable Cam2 le.atrig")
    R("execute as Cam run trigger le.atrig set 3"); R("execute as Cam2 run trigger le.atrig set 5"); time.sleep(0.8)
    chk("Cam and Cam2 press at once: each his own window (maze / fens)", win("Cam") == 13 and win("Cam2") == 15, (win("Cam"), win("Cam2")))
    R(f"tp Cam {M['door'][0] + 5} {L + 1} {M['door'][2]}")
    R("scoreboard players set Cam le.awin 0"); press("Cam", 4)
    chk("a button pressed 7 from the Advisor does nothing", win("Cam") == 0, win("Cam"))
    away(); R("time set 13000"); wait(lambda: at("night"), 6)
    n = PT["night"]; R(f"tp Cam {n[0] - 2} {n[1]} {n[2]}"); press("Cam", 1)
    chk("at night the night menu", win("Cam") == 3, win("Cam"))
    R("time set 6000"); away(); wait(lambda: at("day"), 6)

# ---------------------------------------------------------------- at the Circle
def keys_taken():
    for k in ("signet_king", "tear_creaker", "crown_witches", "thread_labyrinth"):
        R(f"execute as Cam run function last_ember:altar/give_key {{id:\"{k}\"}}")
    time.sleep(0.5)
def t_circle():
    print("[circle]"); stage(); base_state(); away(); R(CIRCLE_FL); wait(lambda: at("day"), 5)
    keys_taken()
    chk("the four keys of chapter I taken (got:1b)", wait(lambda: all('got: 1b' in R(f"data get storage last_ember:keys k.{k}") for k in ("signet_king", "tear_creaker", "crown_witches", "thread_labyrinth")), 4))
    chk("-> the Advisor at the west arch of the Circle (nobody near either point)", wait(lambda: at("circle"), 8), where())
    c = PT["circle"]
    chk("facing the Circle (yaw %.0f)" % c[3], "%.1ff" % c[3] in R(f"data get entity {ADV1} Rotation") or abs(float(re.findall(r"(-?[\d.]+)f", R(f"data get entity {ADV1} Rotation"))[0]) - c[3]) < 1)
    R(f"tp Cam {c[0] + 3} {c[1]} {c[2]}"); time.sleep(3)
    chk("his window there (a real click): «У Круга»", talk_real("Cam") and win("Cam") == 5, win("Cam"))
    chk("one Advisor in the world (the grove's is gone)", count(ADV) == 1)
    away(); R("function last_ember:altar/set_chapters {n:1}"); R("data modify storage last_ember:altars a.weepers.done set value 1b")   # as after the event
    chk("chapter I done -> back in the grove", wait(lambda: at("day"), 8), where())
    a = PT["day"]; R(f"tp Cam {a[0] + 2} {L + 1} {a[2] + 1}"); press("Cam", 1)
    chk("the window «после главы I» instead of the menu", win("Cam") == 4, win("Cam"))
    away(); R("clear Cam minecraft:ominous_trial_key"); time.sleep(0.6); R("function last_ember:altar/reset {chapter:1}"); time.sleep(3)
    chk("altar/reset {chapter:1}: chapter 0, the keys not taken: he stays in the grove", tc.score("#chapters", "le.alt") == 0 and at("day"), where())
    keys_taken()
    chk("the keys again -> at the Circle again", wait(lambda: at("circle"), 8), where())
    base_state(); away(); wait(lambda: at("day"), 8); R("forceload remove -446 -189 -438 -181")

# ---------------------------------------------------------------- the fading of chapter I
def t_fade():
    print("[fade]"); stage(); base_state(); away()
    R("data modify storage last_ember:bonfires by.b10.state set value 1"); time.sleep(1.5)            # lit by the Bearer
    R("function last_ember:altar/set_chapters {n:1}"); R("function last_ember:region/gen/fade_r1"); time.sleep(6)
    bio = [passed(f"execute positioned {x} {y} {z} if biome ~ ~ ~ last_ember:mushroom_grove") for (x, y, z) in ((-420, 130, 60), (HX, L + 2, HZ), (-404, 138, 72), (-400, 145, 40), (-440, 110, 80))]
    chk("after the fading the grove keeps its biome (r <= 29: inside the 16 of transition)", all(bio), bio)
    st = R("data get storage last_ember:bonfires by.b10")
    chk("bonfire 10 still burns (state 1, not faded)", "state: 1" in st and "faded: 1b" not in st, st[:160])
    a = PT["day"]; R(f"tp Cam {a[0] + 2} {L + 1} {a[2] + 1}"); press("Cam", 1)
    chk("the Advisor speaks «после главы I»", win("Cam") == 4, win("Cam"))
    R("function last_ember:region/gen/unfade_r1"); base_state(); away()

# ---------------------------------------------------------------- faces
def t_faces():
    print("[faces]"); stage()
    sys.path.insert(0, os.path.join(ROOT, "tools/build")); import grove_dp
    for f in M["faces"]: R(f"forceload add {f['x']} {f['z']}")
    time.sleep(2)
    R("function last_ember:grove/faces_open"); time.sleep(0.5)
    o = sum(1 for f in M["faces"] if blk(*grove_dp.eye_cell(f), "minecraft:verdant_froglight"))
    chk("faces_open: 6 faces with eyes of verdant froglight", o == 6, o)
    R("function last_ember:grove/faces_close"); time.sleep(0.5)
    c = sum(1 for f in M["faces"] if blk(*grove_dp.eye_cell(f), "minecraft:stripped_poplar_log"))
    chk("faces_close: closed again (as built)", c == 6, c)
    for f in M["faces"]: R(f"forceload remove {f['x']} {f['z']}")

# ---------------------------------------------------------------- zones
def t_zones():
    print("[zones]"); stage(mode="survival")
    R(f"tp Cam {M['path'][4][0] + 0.5} {M['path'][4][2]} {M['path'][4][1] + 1.6} 180 40"); time.sleep(1.5)
    chk("in the grove a player is in adventure", wait(lambda: passed("execute if entity @a[name=Cam,gamemode=adventure]"), 4))
    x, z, y = M["path"][4][0], M["path"][4][1], int(M["path"][4][2] - 1)
    b0 = R(f"execute if block {x} {y} {z} #minecraft:air")
    look_at("Cam", x + 0.5, y + 0.9, z + 0.5); time.sleep(0.4); tc.act("Cam", "!attack_on"); time.sleep(3); tc.act("Cam", "!attack_off")
    chk("a path block does not break (real attack, 3 s)", not blk(x, y, z, "#minecraft:air"))
    R(f"summon minecraft:zombie {HX + 8} {L + 1} {HZ + 8} {{Tags:[\"t30z\"]}}"); time.sleep(2.5)
    chk("a zombie in the grove goes (no_spawn)", count("@e[tag=t30z]") == 0)
    R("difficulty hard"); R("time set 18000"); time.sleep(2)
    chk("night, hard: the Advisor stays", count(ADV) == 1)
    R("difficulty easy"); R("time set 6000"); R("gamemode adventure Cam")

# ---------------------------------------------------------------- restart
def t_restart():
    print("[restart]"); stage(); base_state(); away(); wait(lambda: at("day"), 5)
    talk_real("Cam")
    chk("Cam met him", passed("execute if entity @a[name=Cam,tag=le.amet]"))
    g = gv("#agen")
    tm.restart(); stage(); time.sleep(3)
    chk("after a restart: one Advisor on his point (day)", wait(lambda: count(ADV) == 1 and at("day"), 8), (count(ADV), where()))
    chk("the generation kept (no new Advisor summoned)", gv("#agen") == g, (g, gv("#agen")))
    chk("the acquaintance is not repeated: the menu", talk_real("Cam") and win("Cam") == 2, win("Cam"))

# ---------------------------------------------------------------- perf
def t_perf():
    print("[perf: two players in the grove, night, the move to the observatory and back, the smoke]"); stage(); base_state()
    R(f"tp Cam {PT['day'][0] + 2} {L + 1} {PT['day'][2] + 1}"); R(f"tp Cam2 -410 137 66"); time.sleep(3)
    def during(): R("gamerule advance_time true"); R("time set 12400")
    p0 = tm.prof(10, during); ms = [tm.mspt() for _ in range(3)]
    f = sum(v for k, v in p0.items() if k.startswith("last_ember:grove/"))
    print(f"     profiler: grove/* {f:.4f} ms per tick, server tick {p0.get('tick', 0):.1f} ms, tick query {ms} ms")
    for k, v in sorted(((k, v) for k, v in p0.items() if "grove" in k), key=lambda kv: -kv[1])[:6]: print(f"       {k} {v:.4f}")
    chk("two players: grove/* under 0.1 ms per tick, the tick keeps up", 0 <= f < 0.1 and ms[0] and max(ms) < 50, (f, ms))
    R("gamerule advance_time false"); R("time set 6000")

SUITES = dict(build=t_build, advisor=t_advisor, day=t_day, talk=t_talk, menu=t_menu, circle=t_circle, fade=t_fade, faces=t_faces, zones=t_zones,
              restart=t_restart, perf=t_perf)
if __name__ == "__main__":
    for a in sys.argv[1:] or list(SUITES):
        SUITES[a]()
    print(f"grove: {ok} ok, {bad} failed")
