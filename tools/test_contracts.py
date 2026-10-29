#!/usr/bin/env python3
"""T-020 checks (server + dev clients Cam, Cam2): contracts on the test playground (contracts/test_contracts.txt around (1300, 200, 1290), floor y=200).
Before: python3 tools/gen_contracts.py contracts/test_contracts.txt, tools/server.sh sync, RESTART the server (dialogs load only at start).
Usage: python3 tools/test_contracts.py [build board clues branch spawn leash back twin womb drag ritual reward offline choice perf] [--shots]
Frames go to docs/reports/T-020/ (only with --shots)."""
import importlib.util, os, re, shutil, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
OUT = os.path.join(ROOT, "docs/reports/T-020"); SHOTS = "--shots" in sys.argv
ok = bad = 0
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n)
    else: bad += 1; print("  FAIL", n, e)
score, num = tc.score, tc.num
def R(c): return rc.run(c)
def S(cid, k): return score(f"#{cid}_{k}", "le.ct")
def pos(sel):
    v = re.findall(r"(-?\d+\.?\d*)d", R(f"data get entity {sel} Pos")); return [float(x) for x in v] if len(v) == 3 else None
def dist(a, b): return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5
def has(sel): return "passed" in R(f"execute if entity {sel}")
def count(sel): m = re.search(r"Count: (\d+)", R(f"execute if entity {sel}")); return int(m.group(1)) if m else 0
def ME(cid): return f"@e[tag=le.ct_{cid},tag=le.cmain,limit=1]"
def shot(name, p="Cam"):
    if not SHOTS: return
    tc.act(p, f"{name} 0")
    src = os.path.join(ROOT, tc.DIR[p], "screenshots", f"{name}.png")
    for _ in range(60):
        if os.path.exists(src): break
        time.sleep(0.1)
    if os.path.exists(src): os.makedirs(OUT, exist_ok=True); shutil.move(src, os.path.join(OUT, name + ("" if p == "Cam" else "_cam2") + ".png"))
def wait(cond, t=10.0, step=0.25):
    end = time.time() + t
    while time.time() < end:
        if cond(): return True
        time.sleep(step)
    return cond()
def safe(p):
    R(f"gamemode survival {p}"); R(f"effect clear {p}")
    R(f"effect give {p} minecraft:resistance infinite 4 true"); R(f"effect give {p} minecraft:regeneration infinite 3 true"); R(f"effect give {p} minecraft:saturation infinite 0 true")
def item(p, key): R(f"loot give {p} loot last_ember:contract/item_{key}")
def hold(p, key):
    R(f"clear {p}"); R(f"item replace entity {p} weapon.mainhand from entity @s weapon.mainhand") if False else None
    R(f"loot replace entity {p} weapon.mainhand loot last_ember:contract/item_{key}")
def crouch(p, x, y, z, t=0.8):
    R(f"tp {p} {x + .5} {y} {z + .5}"); tc.act(p, "!sneak_on"); time.sleep(t); tc.act(p, "!sneak_off")
def home(): R("tp Cam 1298.5 201 1286.5 0 0"); R("tp Cam2 1296.5 201 1286.5 0 0")

X1, Z1, X2, Z2 = 1248, 1240, 1360, 1330
def build():
    R(f"forceload add {X1} {Z1} {X2} {Z2}")
    wait(lambda: "passed" in R(f"execute if loaded {X1} 200 {Z1}") and "passed" in R(f"execute if loaded {X2} 200 {Z2}"), 40, 0.5)
    home(); R("gamemode spectator Cam"); R("gamemode spectator Cam2")
    R("gamerule advance_time false"); R("time set noon"); R("weather clear"); R("difficulty hard"); R("gamerule spawn_monsters false"); R("gamerule send_command_feedback false")
    R("function last_ember:contract/gen/reset_all"); R("kill @e[type=#last_ember:monsters,x=1300,y=200,z=1290,distance=..120]")
    R("kill @e[tag=le.chead]"); R("kill @e[tag=le.cured]"); R("kill @e[type=minecraft:item,x=1300,y=200,z=1290,distance=..120]")
    for x in range(X1, X2, 28):
        for z in range(Z1, Z2, 45):
            a, b = min(x + 27, X2), min(z + 44, Z2)
            R(f"fill {x} 196 {z} {a} 199 {b} minecraft:dirt"); R(f"fill {x} 200 {z} {a} 200 {b} minecraft:grass_block")
            R(f"fill {x} 201 {z} {a} 212 {b} minecraft:air")
    # the board: a wall with three signs and the trophy shelf above them
    R("fill 1296 200 1290 1304 206 1290 minecraft:dark_oak_planks"); R("fill 1297 204 1289 1303 204 1289 minecraft:dark_oak_slab[type=top]")
    # the pool of the womb (water to the surface) and its far bank
    R("fill 1258 197 1254 1266 200 1262 minecraft:water"); R("fill 1257 196 1253 1267 196 1263 minecraft:mud")
    # the grove of the leshy: a few trees, the two braziers
    for (x, z) in ((1314, 1262), (1326, 1262), (1316, 1252), (1324, 1252), (1311, 1258), (1329, 1258)):
        R(f"fill {x} 201 {z} {x} 205 {z} minecraft:oak_log"); R(f"fill {x - 2} 205 {z - 2} {x + 2} 207 {z + 2} minecraft:oak_leaves[persistent=true] keep")
    R("setblock 1312 201 1254 minecraft:campfire[lit=false,facing=south]"); R("setblock 1328 201 1254 minecraft:campfire[lit=false,facing=south]")
    # the mill (a few blocks) and the ritual circle
    R("fill 1338 201 1292 1342 204 1296 minecraft:spruce_planks"); R("fill 1339 201 1293 1341 203 1295 minecraft:air")
    for dx, dz in ((3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (-2, 2), (2, -2), (-2, -2)): R(f"setblock {1328 + dx} 201 {1306 + dz} minecraft:candle[lit=true,candles=3]")
    R("function last_ember:contract/gen/reset_all"); R("scoreboard players set #b_tb_bl le.ct 0"); R("scoreboard players set #b_tb_hd le.ct 0")
    if (score("#chapters", "le.alt") or 0) < 0: R("scoreboard players set #chapters le.alt 0")
    time.sleep(2.5); safe("Cam"); safe("Cam2"); home()
    tc.setc(1, 1, 0, "Cam"); tc.setc(1, 2, 0, "Cam2"); safe("Cam"); safe("Cam2"); home(); R("kill @e[type=minecraft:cave_spider,tag=le.brood]")

def sign(x, y, z): return R(f"data get block {x} {y} {z} front_text.messages")
def click_slot(p, k):
    o = "Cam2" if p == "Cam" else "Cam"; R(f"tp {o} 1300.5 201 1280.5")   # the other one must not stand in the ray
    x = 1298 + 2 * (k - 1)
    for _ in range(4):   # the click must reach the board (the client may not have the new look yet)
        R(f"dialog clear {p}"); n0 = score("#clicks", "le.ct") or 0; tc.face(p, x + .5, 201, 1287.5, x + .5, 202.4, 1289.8); time.sleep(0.8); tc.act(p, "!use"); time.sleep(0.8)
        if (score("#clicks", "le.ct") or 0) > n0: time.sleep(0.3); R(f"dialog clear {p}"); return
def take(p, cid, n):
    for _ in range(3):
        click_slot(p, n); R(f"execute as {p} run trigger le.ctake set {n}"); time.sleep(0.8)
        if S(cid, "s") != 1 or (score("#online", "le.ct") or 0) < 2: return

def t_build():
    print("[build]"); build()
    chk("the board is built: 3 signs, 3 click boxes, all contracts visible (state 1)", count("@e[type=minecraft:interaction,tag=le.cb_tb]") == 3 and all(S(c, "s") == 1 for c in ("t_leshy", "t_womb", "t_wolf")),
        [S(c, "s") for c in ("t_leshy", "t_womb", "t_wolf")])
def t_board():
    print("[board]"); home(); time.sleep(0.3)
    s = sign(1298, 202, 1289); chk("the sign shows the region, the title and «на двоих»", "Сумеречный Дол" in s and "Дерево" in s and "на двоих" in s, s)
    R("execute as Cam run trigger le.ctake set 1"); time.sleep(0.6)
    chk("the take button does nothing before the window was opened (trigger not enabled)", S("t_leshy", "s") == 1)
    R("tp Cam2 1400 201 1400"); R("gamemode spectator Cam2"); time.sleep(1.3)
    take("Cam", "t_leshy", 1)
    chk("alone in the game: a contract for two is not taken", S("t_leshy", "s") == 1)
    safe("Cam2"); home(); time.sleep(1.3)
    take("Cam", "t_leshy", 1)
    chk("two players: the click opens the window, its button takes the contract (state 2)", S("t_leshy", "s") == 2, S("t_leshy", "s"))
    chk("the storage mirrors the state", "s: 2" in R("data get storage last_ember:contracts c.t_leshy"))
    time.sleep(0.4); s = sign(1298, 202, 1289); chk("the sign now says «взят»", "взят" in s, s)
    R("execute as Cam2 run trigger le.ctake set 1"); time.sleep(0.6); chk("a second press changes nothing", S("t_leshy", "s") == 2)
    R("tp Cam 1310 201 1310"); time.sleep(0.3); R("execute as Cam run scoreboard players enable @s le.ctake"); R("execute as Cam run trigger le.ctake set 2"); time.sleep(0.6)
    chk("the button works only at the board (within 10 blocks)", S("t_womb", "s") == 1)
    home(); take("Cam2", "t_womb", 2); take("Cam", "t_wolf", 3)
    chk("all three contracts taken", S("t_womb", "s") == 2 and S("t_wolf", "s") == 2, (S("t_womb", "s"), S("t_wolf", "s")))

CLUES_L = [(1303, 201, 1284), (1308, 201, 1276), (1313, 201, 1268), (1317, 201, 1262)]
def t_clues():
    print("[clues: crouch to read, in order, the ranger standing]"); home(); R("kill @e[tag=le.brood]")
    R("tp Cam 1303.5 201 1284.5"); time.sleep(1.0); chk("standing (not a ranger): the clue is not read", S("t_leshy", "cl") == 1, S("t_leshy", "cl"))
    crouch("Cam", 1308, 201, 1276); chk("crouching on the second clue first: nothing (order)", S("t_leshy", "cl") == 1)
    R("kill @e[tag=le.brood]"); R("scoreboard players set #t_leshy_g le.ct 0")
    crouch("Cam", 1303, 201, 1284); chk("crouching on the first: read (next = 2)", S("t_leshy", "cl") == 2, S("t_leshy", "cl"))
    nb = count("@e[tag=le.brood_t_leshy]"); chk(f"the brood came for the reader ({nb} cave spiders)", nb >= 1, nb); R("kill @e[tag=le.brood]")
    if SHOTS:
        R("tp Cam 1304.5 201 1281.5 160 30"); tc.act("Cam", "!sneak_on"); time.sleep(1.2); shot("clue_glow"); tc.act("Cam", "!sneak_off")
    R("tp Cam 1300.5 201 1285.5"); R("tp Cam2 1308.5 201 1276.5"); time.sleep(1.0)
    chk("the ranger reads standing", S("t_leshy", "cl") == 3, S("t_leshy", "cl"))
    R("kill @e[tag=le.brood]")
    R("tp Cam2 1313.5 201 1268.5"); time.sleep(0.8); R("tp Cam2 1313.5 201 1275.5")
    R("tp Cam 1317.5 201 1262.5"); tc.act("Cam", "!sneak_on"); time.sleep(0.8); tc.act("Cam", "!sneak_off"); R("tp Cam 1300.5 201 1285.5")
    chk("the whole trail read: state 3", S("t_leshy", "cl") == 5 and S("t_leshy", "s") == 3, (S("t_leshy", "cl"), S("t_leshy", "s")))
    R("kill @e[tag=le.brood]"); home()
def t_branch():
    print("[branch: the fork, owners, the take-over]"); home(); tc.setc(1, 1, 0, "Cam2"); safe("Cam2"); home()
    crouch("Cam", 1292, 201, 1284); crouch("Cam", 1284, 201, 1276)
    chk("the main trail of the womb read up to the fork", S("t_womb", "cl") == 3, S("t_womb", "cl"))
    crouch("Cam", 1284, 201, 1276); oa, cpn = S("t_womb", "oa"), score("Cam", "le.cpn")
    chk("crouching at the fork: Cam follows branch a", oa == cpn and oa > 0, (oa, cpn))
    crouch("Cam2", 1284, 201, 1276); ob, cpn2 = S("t_womb", "ob"), score("Cam2", "le.cpn")
    chk("Cam2 at the fork: the other branch (b)", ob == cpn2 and ob > 0 and ob != oa, (ob, cpn2))
    crouch("Cam2", 1276, 201, 1270); chk("Cam2 cannot read branch a while Cam owns it ... unless he crouches ON its next clue: he takes it over", S("t_womb", "oa") == cpn2, S("t_womb", "oa"))
    chk("the take-over read nothing yet (branch a still at 1)", S("t_womb", "ca") in (1, 2), S("t_womb", "ca"))
    crouch("Cam2", 1276, 201, 1270); crouch("Cam2", 1268, 201, 1262)
    chk("Cam2 finishes branch a", S("t_womb", "da") == 1, (S("t_womb", "ca"), S("t_womb", "da")))
    crouch("Cam", 1284, 201, 1276)   # Cam lost a; b is owned by Cam2 -> Cam takes it over at its next clue
    crouch("Cam", 1284, 201, 1266); crouch("Cam", 1284, 201, 1266); crouch("Cam", 1286, 201, 1258)
    inv = R("data get entity Cam Inventory")
    chk("branch b done: Cam got the remains; both halves read: state 3", S("t_womb", "db") == 1 and "le_citem" in inv and S("t_womb", "s") == 3, (S("t_womb", "cb"), S("t_womb", "db"), S("t_womb", "s")))
    # the wolf trail (main only, the ring at its end)
    for (x, z) in ((1306, 1294), (1316, 1294), (1328, 1294)): crouch("Cam2", x, 201, z)
    chk("the wolf trail read, the ring given at its end", S("t_wolf", "s") == 3 and "t_ring" in R("data get entity Cam2 Inventory"), S("t_wolf", "s"))
    R("kill @e[tag=le.brood]"); home()

def t_spawn():
    print("[spawn: lair (dormant tree), bait (warning, >=16, out of sight), night]"); home()
    wait(lambda: S("t_leshy", "m") == 1, 4)
    L = (1320.5, 201, 1258.5); p = pos(ME("t_leshy"))
    chk("the leshy waits in its lair (dormant tree, le.ls 0)", p and dist(p, L) < 2 and score(ME("t_leshy"), "le.ls") == 0, (p, score(ME("t_leshy"), "le.ls")))
    chk("it has the tags le.noelite, le.contract, le.ct_t_leshy and 500 + 120 health", has("@e[tag=le.ct_t_leshy,tag=le.noelite,tag=le.contract]") and abs((num(R(f"data get entity {ME('t_leshy')} Health")) or 0) - 620) < 1)
    if SHOTS: R("gamemode spectator Cam"); R("tp Cam 1320.5 204 1270.5 180 12"); time.sleep(2.5); shot("leshy_tree"); safe("Cam"); home()
    R("tp Cam 1320.5 201 1262.5 180 0"); time.sleep(0.6)
    chk("a player within 4: the tree tears itself out", score(ME("t_leshy"), "le.ls") == 1, score(ME("t_leshy"), "le.ls"))
    wait(lambda: score(ME("t_leshy"), "le.ls") == 2, 4); time.sleep(1.2)
    chk("awake: the fight begins (state 4)", S("t_leshy", "s") == 4, S("t_leshy", "s"))
    chk("Cam is a participant", "le.cp_t_leshy" in R("data get entity Cam Tags"))
    home(); time.sleep(0.5)
    # the wolf: bait at the mill at night, a non-weapon in hand
    R("tp Cam2 1336.5 201 1290.5 0 0"); time.sleep(1.2); chk("by day nothing comes to the bait", S("t_wolf", "w") == 0)
    R("item replace entity Cam2 weapon.mainhand with minecraft:iron_sword"); time.sleep(1.2); R("time set midnight"); time.sleep(1.2)
    chk("at night with a sword in hand: nothing comes", S("t_wolf", "w") == 0)
    R("item replace entity Cam2 weapon.mainhand with minecraft:bread"); R("tp Cam2 1336.5 201 1290.5 180 0"); time.sleep(1.4)
    w = S("t_wolf", "w"); chk(f"at night, bread in hand: the warning starts ({w} s)", w and w > 5, w)
    R("tp Cam2 1336.5 201 1290.5 180 0"); R("tp Cam 1334.5 201 1290.5 180 0")   # both look north-west, away from (1348, 1318)... and toward (1348, 1268)?
    wait(lambda: S("t_wolf", "m") == 1, 22, 0.5); p = pos(ME("t_wolf"))
    ps = [pos("Cam"), pos("Cam2")]
    chk("the wolf arrives at a point >= 16 from both players", p is not None and min(dist(p, q) for q in ps) >= 15.5, (p, ps))
    chk("its arrival starts the fight (state 4)", S("t_wolf", "s") == 4, S("t_wolf", "s"))
    home(); R("time set noon")

def t_leash():
    print("[leash and return]"); home()
    if S("t_leshy", "m") != 1: R("function last_ember:contract/gen/spawn {id:\"t_leshy\"}") if False else None
    R(f"execute as {ME('t_leshy')} run data merge entity @s {{NoAI:1b}}"); R(f"tp {ME('t_leshy')} 1320.5 201 1300.5"); wait(lambda: dist(pos(ME("t_leshy")) or (0, 0, 0), (1320.5, 201, 1258.5)) <= 34, 8)
    p = pos(ME("t_leshy")); chk("pulled 42 blocks out: the leash brings it back toward the lair (within 32)", p and dist(p, (1320.5, 201, 1258.5)) <= 34, (p, score(ME("t_leshy"), "le.ls"), R(f"data get entity {ME('t_leshy')} NoAI")))
    R(f"execute as {ME('t_leshy')} run data merge entity @s {{NoAI:0b}}")
    R(f"execute as {ME('t_leshy')} run damage @s 30 minecraft:generic"); time.sleep(0.4); h0 = num(R(f"data get entity {ME('t_leshy')} Health"))
    R("tp Cam 1400.5 201 1300.5"); R("tp Cam2 1400.5 201 1302.5"); time.sleep(2.5)
    p = pos(ME("t_leshy")); h1 = num(R(f"data get entity {ME('t_leshy')} Health"))
    chk(f"nobody within 48: back in the lair with full health ({h0} -> {h1}), a tree again", p and dist(p, (1320.5, 201, 1258.5)) < 1.5 and h1 >= 619 and score(ME("t_leshy"), "le.ls") == 0, (p, h1, score(ME("t_leshy"), "le.ls")))
    chk("nothing of the contract is reset (trail read, Cam a participant)", S("t_leshy", "cl") == 5 and "le.cp_t_leshy" in R("data get entity Cam Tags"))
    home()

def hp_of(cid): return num(R(f"data get entity {ME(cid)} Health"))
def t_back():
    print("[the back: a blow from the front glances off, from behind it goes in]"); home()
    R("tp Cam 1320.5 201 1262.5 180 0"); wait(lambda: score(ME("t_leshy"), "le.ls") == 2, 6); time.sleep(0.3)
    R(f"execute as {ME('t_leshy')} run data merge entity @s {{NoAI:1b}}"); R(f"tp {ME('t_leshy')} 1320.5 201 1258.5 0 0"); time.sleep(0.3)
    R("tp Cam 1320.5 201 1261.5 180 0"); h0 = hp_of("t_leshy"); R(f"damage {ME('t_leshy')} 8 minecraft:player_attack by Cam"); time.sleep(0.4); h1 = hp_of("t_leshy")
    R("tp Cam 1320.5 201 1255.5 0 0"); time.sleep(0.6); h2 = hp_of("t_leshy"); R(f"damage {ME('t_leshy')} 8 minecraft:player_attack by Cam"); time.sleep(0.4); h3 = hp_of("t_leshy")
    print(f"   front {h0}->{h1}, back {h2}->{h3}")
    chk("from the front: at most a third of the loss counts", h0 - h1 < (h2 - h3) * 0.5 and h0 - h1 > 0, (h0, h1, h2, h3))
    chk("from behind: the blow goes in", h2 - h3 >= 3, (h2, h3))
    chk("the last hitter is recorded", "last" in R("data get storage last_ember:contracts c.t_leshy"))
    R(f"execute as {ME('t_leshy')} run data merge entity @s {{NoAI:0b}}"); home()
def t_twin():
    print("[twins: two braziers within a second]"); home(); R("tp Cam 1312.5 201 1256.5"); R("tp Cam2 1328.5 201 1256.5")
    R("setblock 1312 201 1254 minecraft:campfire[lit=true,facing=south]"); time.sleep(2.0)
    chk("one brazier alone goes out again", "passed" in R("execute if block 1312 201 1254 minecraft:campfire[lit=false]"))
    R("setblock 1312 201 1254 minecraft:campfire[lit=true,facing=south]"); R("setblock 1328 201 1254 minecraft:campfire[lit=true,facing=south]"); time.sleep(0.8)
    chk("both within a second: the leshy is weakened (le.cweak, armour 0)", has("@e[tag=le.ct_t_leshy,tag=le.cweak]") and num(R(f"attribute {ME('t_leshy')} minecraft:armor get")) == 0,
        R(f"attribute {ME('t_leshy')} minecraft:armor get"))
    R(f"execute as {ME('t_leshy')} run data merge entity @s {{NoAI:1b}}"); R(f"tp {ME('t_leshy')} 1320.5 201 1258.5 0 0"); R("tp Cam 1320.5 201 1261.5 180 0"); time.sleep(0.3)
    h0 = hp_of("t_leshy"); R(f"damage {ME('t_leshy')} 8 minecraft:player_attack by Cam"); time.sleep(0.4); h1 = hp_of("t_leshy")
    chk(f"weakened: a blow from the front goes in fully ({h0} -> {h1})", h0 - h1 >= 7, (h0, h1))
    R(f"scoreboard players set {ME('t_leshy')} le.cwk 5"); time.sleep(1.0)
    chk("the weakness runs out", not has("@e[tag=le.ct_t_leshy,tag=le.cweak]"))
    chk("the braziers stay lit until they are rearmed, no second weakening", "passed" in R("execute if block 1328 201 1254 minecraft:campfire[lit=true]"))
    R("function last_ember:contract/gen/twin_rearm_t_leshy_braziers"); time.sleep(0.3)
    chk("rearmed: both out again", "passed" in R("execute if block 1328 201 1254 minecraft:campfire[lit=false]") and S("t_leshy_braziers", "ta") == 0)
    R(f"execute as {ME('t_leshy')} run data merge entity @s {{NoAI:0b}}"); home()

def t_womb():
    print("[the womb: the bait, the water, the split]"); home(); tc.setc(1, 1, 0, "Cam"); safe("Cam")
    R("tp Cam 1282.5 201 1258.5 -90 0"); time.sleep(1.4); chk("no remains in hand: it does not come", S("t_womb", "w") == 0)
    hold("Cam", "t_remains"); R("tp Cam 1282.5 201 1258.5 -90 0"); time.sleep(1.4)
    chk("the remains in hand at the bait: the warning (bubbles, breath)", (S("t_womb", "w") or 0) > 0, S("t_womb", "w"))
    wait(lambda: S("t_womb", "m") == 1, 16, 0.5); p = pos(ME("t_womb"))
    chk("the womb rises in its pool", p and dist(p, (1262.5, 198, 1258.5)) < 3, p)
    time.sleep(2.0); wait(lambda: score(ME("t_womb"), "le.ls") == 2, 6)
    R(f"execute as {ME('t_womb')} run data merge entity @s {{NoAI:1b}}"); R(f"tp {ME('t_womb')} 1262.5 198 1258.5"); time.sleep(1.2)
    chk("in the water: no dry tag (full armour)", not has("@e[tag=le.ct_t_womb,tag=le.cdry]"))
    R(f"tp {ME('t_womb')} 1276.5 201 1258.5"); time.sleep(1.2)
    chk("on dry land: weak (le.cdry, half the blow)", has("@e[tag=le.ct_t_womb,tag=le.cdry]"))
    R(f"damage {ME('t_womb')} 64 minecraft:player_attack by Cam"); time.sleep(0.8)
    n = count("@e[tag=le.ct_t_womb_sm]")
    chk(f"at half health it bursts: two small wombs ({n})", n == 2 and S("t_womb", "hf") == 1, (n, S("t_womb", "hf"), hp_of("t_womb")))
    if SHOTS: R("gamemode spectator Cam"); R("tp Cam 1283.5 204 1262.5 110 20"); time.sleep(2.5); shot("womb_split"); safe("Cam")
    R(f"execute as {ME('t_womb')} run data merge entity @s {{NoAI:0b}}"); R("tp Cam 1290.5 201 1258.5"); home()
def t_drag():
    print("[the drag: one player is taken to the far bank, the other follows the blood]"); home()
    R("tp Cam2 1276.5 201 1258.5"); got = False
    for _ in range(20):
        R(f"execute as Cam2 at @s run scoreboard players set #cid le.ct 2"); R("execute as Cam2 at @s run function last_ember:contract/gen/hurt_p")
        if "le.dragged" in R("data get entity Cam2 Tags"): got = True; break
    p = pos("Cam2"); nt = count("@e[type=minecraft:marker,tag=le.ctrail_t_womb]")
    chk(f"a blow drags Cam2 to the far bank ({p}), a trail of blood ({nt} marks)", got and p and dist(p, (1262, 201, 1250)) < 2 and nt >= 3, (got, p, nt))
    R("tp Cam 1276.5 201 1258.5"); tc.act("Cam", "!sneak_on"); time.sleep(1.5); shot("drag_trail"); tc.act("Cam", "!sneak_off")
    R("tp Cam 1263.5 201 1251.5"); time.sleep(1.4)
    chk("Cam comes within 4: Cam2 is free, the trail is gone", "le.dragged" not in R("data get entity Cam2 Tags") and count("@e[type=minecraft:marker,tag=le.ctrail_t_womb]") == 0)
    home()

import threading
class Pin:
    """keeps a monster at a place (the lab rigs move by tp, NoAI does not hold them): a thread re-places it every 0.2 s"""
    def __init__(self, cid, x, y, z): self.a = (cid, x, y, z); self.on = True; threading.Thread(target=self.run, daemon=True).start()
    def run(self):
        r = load("rcon")
        while self.on: r.run("tp %s %s %s %s" % (ME(self.a[0]), *self.a[1:])); time.sleep(0.2)
    def stop(self): self.on = False; time.sleep(0.3)
def t_ritual():
    print("[the ritual: the ring in the circle at midnight, the wolf held near, the pauses, the floor]"); home()
    if S("t_wolf", "m") != 1:
        R("time set midnight"); R("execute positioned 1348 201 1268 run function last_ember:contract/gen/spawn_t_wolf"); time.sleep(1.0)
    R("time set noon"); R("execute as Cam2 run clear @s"); hold("Cam2", "t_ring")
    pin = Pin("t_wolf", 1328.5, 201, 1312.5)
    R("tp Cam2 1328.5 201 1306.5 180 0"); R("tp Cam 1330.5 201 1310.5"); time.sleep(1.4)
    chk("by day the ritual does not start", S("t_wolf", "rs") == 0, S("t_wolf", "rs"))
    R("time set 18000"); wait(lambda: S("t_wolf", "rs") == 1, 4)
    chk("midnight, the ring in the circle, the wolf within 12: the ritual starts", S("t_wolf", "rs") == 1 and (S("t_wolf", "rt") or 0) > 30, (S("t_wolf", "rs"), S("t_wolf", "rt")))
    if SHOTS: R("gamemode spectator Cam"); R("tp Cam 1336.5 205 1300.5 45 25"); time.sleep(2.0); shot("ritual"); safe("Cam")
    t0 = S("t_wolf", "rt"); R("tp Cam2 1336.5 201 1306.5"); time.sleep(2.2); t1 = S("t_wolf", "rt")
    chk(f"the ring-bearer leaves the circle: the countdown pauses ({t0} -> {t1})", t1 is not None and t0 - t1 <= 1, (t0, t1))
    R("tp Cam2 1328.5 201 1306.5 180 0"); time.sleep(2.2); t2 = S("t_wolf", "rt"); chk(f"back in the circle: it goes on ({t1} -> {t2})", t2 is not None and t2 < t1, (t1, t2))
    R(f"damage {ME('t_wolf')} 300 minecraft:player_attack by Cam"); time.sleep(0.5); h = hp_of("t_wolf")
    chk(f"during the ritual it cannot be killed (health floor 10%: {h})", h is not None and h >= 511, h)
    R("scoreboard players set #t_wolf_rt le.ct 2"); wait(lambda: S("t_wolf", "s") == 5, 8)
    chk("the countdown ends: the curse is lifted, a man (villager) stands there, the contract is done (5)", has("@e[tag=le.cured_t_wolf]") and S("t_wolf", "s") == 5 and S("t_wolf", "cu") == 1, (S("t_wolf", "s"), S("t_wolf", "cu"), S("t_wolf", "rs"), S("t_wolf", "rt"), pos(ME("t_wolf")), score(ME("t_wolf"), "le.ls"), score("#incircle_t_wolf", "le.ct")))
    pin.stop(); chk("the wolf is gone", not has(ME("t_wolf")))
    if SHOTS: R("gamemode spectator Cam"); R("tp Cam 1332.5 203 1312.5 140 15"); time.sleep(2.0); shot("ritual_cured"); safe("Cam")
    R("time set noon"); home()

def inv(p): return R(f"data get entity {p} Inventory")
def t_reward():
    print("[reward: at the board, each participant, the trophy to the last hitter]"); home()
    if S("t_leshy", "s") != 5:
        R(f"execute as {ME('t_leshy')} run data merge entity @s {{NoAI:1b}}"); R(f"tp {ME('t_leshy')} 1320.5 201 1258.5 0 0"); R("tp Cam2 1320.5 201 1255.5 0 0"); R("tp Cam 1320.5 201 1254.5 0 0"); time.sleep(0.5)
        R(f"execute as {ME('t_leshy')} run function last_ember:contract/m/weaken {{t:200}}")
        R(f"damage {ME('t_leshy')} 200 minecraft:player_attack by Cam2"); wait(lambda: S("t_leshy", "s") == 5, 8)
    chk("the leshy is killed: state 5", S("t_leshy", "s") == 5, S("t_leshy", "s"))
    chk("its head stands on the trophy shelf", count("@e[tag=le.chead]") >= 1, count("@e[tag=le.chead]"))
    R("clear Cam"); R("clear Cam2"); R("xp set Cam 0 levels"); R("xp set Cam2 0 levels"); home(); time.sleep(0.3)
    click_slot("Cam", 1); time.sleep(0.5)
    i1 = inv("Cam"); chk(f"Cam (a participant) gets his reward and 5 levels at the board ({score('Cam', 'le.x') if False else ''})", "le_trophy" not in i1 and len(i1) > 20 and "le.cr_t_leshy" in R("data get entity Cam Tags"), i1[:200])
    chk("XP +5 levels", "has 5 experience" in R("xp query Cam levels"), R("xp query Cam levels"))
    click_slot("Cam", 1); time.sleep(0.5); chk("a second click gives nothing more", inv("Cam") == i1)
    click_slot("Cam2", 1); time.sleep(0.5); i2 = inv("Cam2")
    chk("Cam2 (the last hitter) gets his reward and the trophy of the Dol", "le_trophy" in i2 and "r1" in i2, i2[:300])
    chk("everyone has taken it: state 6", S("t_leshy", "s") == 6, S("t_leshy", "s"))
    if SHOTS: R("gamemode spectator Cam"); R("tp Cam 1300.5 204 1283.5 0 15"); time.sleep(2.0); shot("trophy_shelf"); safe("Cam")
    home()
def t_offline():
    print("[offline: a participant who left gets his reward at the next click]")
    cur = S("t_wolf", "s")
    if cur != 5: print("   (needs the ritual first)"); return
    R("clear Cam"); R("xp set Cam 0 levels"); R("clear Cam2"); R("kick Cam2"); time.sleep(2.0)
    for d in os.listdir("/proc"):   # the kicked client stays on its menu: close it
        try:
            if d.isdigit() and "--username\0Cam2\0" in open(f"/proc/{d}/cmdline").read(): os.kill(int(d), 15)
        except OSError: pass
    home(); click_slot("Cam", 3); time.sleep(0.5)
    chk("Cam takes his share (cured: no trophy, 5 levels); the wolf contract waits for Cam2 (state stays 5)", S("t_wolf", "s") == 5 and "has 5 experience" in R("xp query Cam levels") and "le_trophy" not in inv("Cam"), (S("t_wolf", "s"), R("xp query Cam levels")))
    subprocess.Popen([sys.executable, os.path.join(ROOT, "tools/client_launch.py"), "--name", "Cam2", "--dir", "server/client2", "--mem", "1500M", "--size", "640x360"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    wait(lambda: "Cam2" in R("list"), 150, 2); time.sleep(4); safe("Cam2"); home(); time.sleep(0.5); click_slot("Cam2", 3); time.sleep(0.6)
    chk("Cam2 is back: his reward at the board (cured: no trophy), state 6", S("t_wolf", "s") == 6 and "le_trophy" not in inv("Cam2") and len(inv("Cam2")) > 20, (S("t_wolf", "s"), inv("Cam2")[:200]))

def t_choice():
    print("[choice: clickable lines, the first who clicks decides]")
    R("data remove storage last_ember:choices t_choice"); R("scoreboard players set #ch_t_choice le.ct 0")
    R("execute as Cam2 run trigger le.choice set 11"); chk("not offered yet: a trigger does nothing", "t_choice" not in R("data get storage last_ember:choices"))
    R("function last_ember:contract/gen/offer {id:\"t_choice\"}"); time.sleep(0.2)
    if SHOTS: tc.act("Cam", "!chat_open") if False else None
    R("execute as Cam2 run trigger le.choice set 12"); time.sleep(0.4); R("execute as Cam run trigger le.choice set 11"); time.sleep(0.4)
    chk("Cam2 clicked first: option b stands, Cam's later click changes nothing", R("data get storage last_ember:choices t_choice").strip().endswith('"b"'), R("data get storage last_ember:choices t_choice"))

def t_cent():
    print("[the centipede segments: a blow counts like a vanilla one (weapon, enchantments, cooldown, fire, oil)]"); home()
    R("function last_ember:lab/clear"); R("execute positioned 1300.5 201 1318.5 run function last_ember:lab/st_fish"); time.sleep(1.0)
    R("tp Cam2 1300.5 201 1314.5 0 0"); wait(lambda: score("@e[tag=le.lab_fish,limit=1]", "le.ls") == 2, 8); time.sleep(3.0)
    R("execute as @e[tag=le.lab_fish] run data merge entity @s {NoAI:1b}"); R("effect give @e[tag=le.lab_fish] minecraft:resistance infinite 0 true") if False else None
    F = "@e[tag=le.lab_fish,limit=1]"
    def hit(item, charge=True):
        R(f"item replace entity Cam2 weapon.mainhand with {item}"); time.sleep(1.0)
        if not charge: R("execute store result score Cam2 le.lcbt run time query gametime")
        h0 = num(R(f"data get entity {F} Health"))
        R("execute as @e[tag=le.cb6] run data merge entity @s {attack:{player:[I;0,0,0,0],timestamp:0L}}"); R("data modify entity @e[tag=le.cb6,limit=1] attack.player set from entity Cam2 UUID")
        time.sleep(0.25); h1 = num(R(f"data get entity {F} Health")); d = round((h0 or 0) - (h1 or 0), 2)
        if d == 0 and charge: R("scoreboard players set @e[tag=le.lab_fish] le.ls 2"); time.sleep(0.6); return hit(item, charge)   # the box was not there (it moved): once more
        return d
    R("execute as @e[tag=le.lab_fish] run attribute @s minecraft:armor base set 0")
    plain = hit("minecraft:iron_sword"); sharp = hit("minecraft:iron_sword[minecraft:enchantments={\"minecraft:sharpness\":5}]"); bane = hit("minecraft:iron_sword[minecraft:enchantments={\"minecraft:bane_of_arthropods\":2}]")
    weak = hit("minecraft:iron_sword", False)
    print(f"   iron sword {plain}, sharpness V {sharp}, bane II {bane}, no charge {weak}")
    chk(f"a full blow with an iron sword: 6 ({plain})", abs(plain - 6) < 0.3, plain)
    chk(f"Sharpness V adds 3 ({sharp})", abs(sharp - 9) < 0.3, sharp)
    chk(f"Bane of Arthropods II adds 5 (the carrier is an arthropod: {bane})", abs(bane - 11) < 0.3, bane)
    chk(f"a blow right after the last one: a fifth ({weak})", 0.8 < weak < 2.0, weak)
    hit("minecraft:iron_sword[minecraft:enchantments={\"minecraft:fire_aspect\":1}]")
    chk("Fire Aspect sets the carrier on fire", (num(R(f"data get entity {F} Fire")) or 0) > 20, R(f"data get entity {F} Fire"))
    R(f"execute as {F} run data merge entity @s {{Fire:0s}}")
    hit("minecraft:iron_sword[minecraft:custom_data={le_oil:{type:\"poison\",n:3}}]")
    chk("an oiled blade poisons the carrier (wherever it is)", "poison" in R(f"data get entity {F} active_effects"), R(f"data get entity {F} active_effects"))
    R("function last_ember:lab/clear"); R("item replace entity Cam2 weapon.mainhand with minecraft:air"); home()
def t_wounds():
    print("[wounds: Frost and Burn]"); home(); safe("Cam2"); R("effect clear Cam2 minecraft:resistance"); R("effect clear Cam2 minecraft:regeneration")
    R("execute as Cam2 at @s run function last_ember:wound/frost"); time.sleep(0.3); e = R("data get entity Cam2 active_effects")
    chk("Frost: slowness I and mining fatigue I", "slowness" in e and "mining_fatigue" in e, e)
    R("tag Cam2 add le.warm"); time.sleep(0.3); e = R("data get entity Cam2 active_effects")
    chk("the Warmth of the Ember lifts it at once", "mining_fatigue" not in e and score("Cam2", "le.wfr") == 0, (e, score("Cam2", "le.wfr")))
    R("tag Cam2 remove le.warm")
    R("effect give Cam2 minecraft:instant_health 1 5"); time.sleep(0.3); h0 = num(R("data get entity Cam2 Health"))
    R("execute as Cam2 at @s run function last_ember:wound/burn"); time.sleep(3.4); h1 = num(R("data get entity Cam2 Health"))
    chk(f"Burn: fire damage once a second for 3 s, then out ({h0} -> {h1}; the knight's armour and Resistance soften it)", h0 and h1 is not None and 0.5 <= h0 - h1 <= 4.5 and score("Cam2", "le.wbu") == 0, (h0, h1))
    R("execute as Cam2 at @s run function last_ember:wound/burn"); R("tp Cam2 1262.5 198 1258.5"); time.sleep(0.4)
    chk("water puts it out", score("Cam2", "le.wbu") == 0, score("Cam2", "le.wbu"))
    R("effect give Cam2 minecraft:fire_resistance 10 0 true"); R("tp Cam2 1296.5 201 1286.5"); R("execute as Cam2 at @s run function last_ember:wound/burn"); time.sleep(0.2)
    chk("fire resistance: no burn", score("Cam2", "le.wbu") in (0, None)); safe("Cam2"); home()
def t_gallery():
    """frames only: the three monsters side by side (day and night), the board"""
    if not SHOTS: return
    print("[gallery]"); home(); R("function last_ember:contract/gen/reset_all"); R("kill @e[tag=le.lab]"); R("scoreboard players set #noleash le.ct 1"); time.sleep(1.0)
    R("gamemode spectator Cam"); R("tp Cam 1300.5 203.3 1286.6 0 10"); time.sleep(8); shot("board")
    R("time set midnight")
    for cid, x in (("t_wolf", 1294.5), ("t_leshy", 1300.5), ("t_womb", 1307.5)): R(f"execute positioned {x} 201 1306.5 run function last_ember:contract/gen/spawn_{cid}")
    R("gamemode spectator Cam2"); R("tp Cam2 1300.5 201 1290.5")   # wakes them
    time.sleep(5.0); pins = [Pin(c, x, 201, 1306.5) for c, x in (("t_wolf", 1294.5), ("t_leshy", 1300.5), ("t_womb", 1307.5))]
    for c in ("t_wolf", "t_leshy", "t_womb"): R(f"execute as {ME(c)} at @s run rotate @s 180 0")
    R("tp Cam 1300.5 204 1295.5 0 12"); R("effect give Cam minecraft:night_vision infinite 0 true"); time.sleep(3.0); shot("three_night")
    R("effect clear Cam minecraft:night_vision"); time.sleep(1.0); shot("three_night_dark")
    R("time set noon"); time.sleep(1.5); shot("three_day"); R("tp Cam 1300.5 202.5 1299.5 0 5"); time.sleep(1.5); shot("three_day_near")
    for c, a in (("t_wolf", -35), ("t_leshy", 20), ("t_womb", 40)):
        R(f"execute as {ME(c)} at @s rotated ~{a} 10 positioned ^ ^2.5 ^6 run tp Cam ~ ~ ~ facing entity {ME(c)} eyes"); time.sleep(2.0); shot("close_" + c[2:])
    for p_ in pins: p_.stop()
    R("scoreboard players set #noleash le.ct 0"); R("function last_ember:contract/gen/reset_all"); safe("Cam"); safe("Cam2"); home()
def prof(sec=10):
    """the profiler for sec seconds: ms per tick of every last_ember function run from the schedule or the tick tag"""
    import glob, zipfile
    before = set(glob.glob(os.path.join(ROOT, "server/debug/profiling/*.zip"))); R("perf start"); time.sleep(sec + 1)
    if "Stopped" not in R("perf stop"): pass
    new = []
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
    print("[load: the profiler, ms per tick of the contract loop and of the monsters]"); home()
    def show(tag, p): c = p.get("last_ember:contract/loop", 0); l = p.get("last_ember:lab/tick", 0); print(f"   {tag}: tick {p.get('tick', 0):.1f} ms, contract/loop {c:.3f} ms, lab/tick {l:.3f} ms, char/loop {p.get('last_ember:char/loop', 0):.3f} ms"); return c, l
    R("function last_ember:contract/gen/reset_all"); time.sleep(1.5); c0, _ = show("no contract taken", prof())
    for c in ("t_leshy", "t_womb", "t_wolf"): R(f"function last_ember:contract/gen/state {{id:\"{c}\",s:2}}")
    R("tp Cam 1303.5 201 1284.5"); R("tp Cam2 1292.5 201 1284.5"); tc.act("Cam", "!sneak_on"); tc.act("Cam2", "!sneak_on"); c1, _ = show("3 taken, both crouch on trails", prof())
    tc.act("Cam", "!sneak_off"); tc.act("Cam2", "!sneak_off"); R("time set midnight")
    R("execute positioned 1336 201 1300 run function last_ember:contract/gen/spawn_t_wolf"); R("execute positioned 1276 201 1258 run function last_ember:contract/gen/spawn_t_womb")
    R("tp Cam 1320.5 201 1262.5"); R("tp Cam2 1310.5 201 1270.5"); time.sleep(4); c2, l2 = show("3 monsters awake and fighting", prof())
    chk(f"contracts taken, 2 players on trails: the contract loop {c1:.3f} ms per tick (< 0.6)", c1 < 0.6)
    chk(f"three monsters fighting: contract loop {c2:.3f} ms + the three rigs {l2:.3f} ms per tick (loop < 0.5, rigs < 1 ms each; this machine also renders two clients)", c2 < 0.5 and l2 < 3.0)
    R("function last_ember:contract/gen/reset_all"); R("time set noon"); home()

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")] or ["build", "board", "clues", "branch", "spawn", "leash", "back", "twin", "womb", "drag", "ritual", "offline", "reward", "choice", "cent", "wounds", "gallery", "perf"]
    try:
        for w in want: globals()["t_" + w]()
    finally: R("gamerule spawn_monsters true"); R("gamerule send_command_feedback true")
    print(f"\n{ok} ok, {bad} failed"); sys.exit(1 if bad else 0)
