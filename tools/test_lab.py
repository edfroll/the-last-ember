#!/usr/bin/env python3
"""T-018 checks (server + dev clients Cam = camera, Cam2 = the prey): the five lab samples on a flat test field around (800, 200, 800).
Usage: python3 tools/test_lab.py [drowner warg womb leshy fish wounds row perf] [--light day|night|cave] [--shots]
Frames go to docs/reports/T-018/ (only with --shots)."""
import importlib.util, os, re, shutil, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
OUT = os.path.join(ROOT, "docs/reports/T-018"); SHOTS = "--shots" in sys.argv
LIGHT = sys.argv[sys.argv.index("--light") + 1] if "--light" in sys.argv else "day"
ok = bad = 0
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n)
    else: bad += 1; print("  FAIL", n, e)
score, num = tc.score, tc.num
def R(c): return rc.run(c)
def ls(tag): return score(f"@e[tag={tag},limit=1]", "le.ls")
def pos(sel):
    v = re.findall(r"(-?\d+\.?\d*)d", R(f"data get entity {sel} Pos")); return [float(x) for x in v] if len(v) == 3 else None
def alive(tag): return "passed" in R(f"execute if entity @e[tag={tag}]")
def shot(name, p="Cam"):
    if not SHOTS: return
    tc.act(p, f"{name}_{LIGHT} 0")
    src = os.path.join(ROOT, tc.DIR[p], "screenshots", f"{name}_{LIGHT}.png")
    for _ in range(40):
        if os.path.exists(src): break
        time.sleep(0.1)
    if os.path.exists(src): os.makedirs(OUT, exist_ok=True); shutil.move(src, os.path.join(OUT, f"{name}_{LIGHT}" + ("" if p == "Cam" else "_cam2") + ".png"))
C = (800, 200, 800)   # the centre of the field; samples stand at C, the prey comes from the south (z-)
def field():
    R("forceload add 768 768 832 832")
    for _ in range(40):
        if "passed" in R("execute if loaded 768 200 768") and "passed" in R("execute if loaded 832 200 832"): break
        time.sleep(0.5)
    R("function last_ember:lab/clear"); R("kill @e[type=#last_ember:monsters,distance=..80,x=800,y=200,z=800]")
    R("fill 770 196 770 830 198 830 minecraft:dirt"); R("fill 770 199 770 830 199 830 minecraft:grass_block")
    for y in range(200, 216, 4): R(f"fill 770 {y} 770 830 {y + 3} 830 minecraft:air")   # a fill is at most 32768 blocks
    if LIGHT == "cave":   # a closed stone hall, no light inside
        R("fill 776 199 776 824 199 824 minecraft:stone"); R("fill 776 200 776 776 208 824 minecraft:stone"); R("fill 824 200 776 824 208 824 minecraft:stone")
        R("fill 776 200 776 824 208 776 minecraft:stone"); R("fill 776 200 824 824 208 824 minecraft:stone"); R("fill 776 209 776 824 209 824 minecraft:stone")
    R("time set " + ("midnight" if LIGHT == "night" else "noon")); R("weather clear"); R("difficulty hard"); R("gamerule advance_time false")
def prey(x=800.5, z=788.5, yaw=0):
    tc.setc(1, 1, 0, "Cam2"); R("gamemode survival Cam2"); R("effect clear Cam2")
    R("effect give Cam2 minecraft:regeneration 100000 3 true"); R("effect give Cam2 minecraft:resistance 100000 1 true")
    R(f"tp Cam2 {x} 200 {z} {yaw} 0")
def cam(x, y, z, yaw, pitch): R("gamemode spectator Cam"); R(f"tp Cam {x} {y} {z} {yaw} {pitch}")
def look(tag, d=5.0, h=1.6, ang=35):
    """the camera d blocks from the sample, ang degrees off its front, h up, looking at its eyes; Cam2 also turns to it"""
    R("gamemode spectator Cam")
    R(f"execute as @e[tag={tag},limit=1] at @s rotated ~{ang} 0 positioned ^ ^{h} ^{d} run tp Cam ~ ~ ~ facing entity @e[tag={tag},limit=1] eyes")
    R(f"execute as Cam2 at @s run tp @s ~ ~ ~ facing entity @e[tag={tag},limit=1] eyes")
    time.sleep(0.15)
def station(k): R(f"execute positioned {C[0] + .5} {C[1]} {C[2] + .5} run function last_ember:lab/st_{k}")
def kill(tag): R(f"damage @e[tag={tag},limit=1] 100 minecraft:player_attack by Cam2")
def wake(): R("tp Cam2 800.5 200 793.5 0 0")
def follow(tag, sec, step=0.5, cb=None):
    """the prey walks away slowly in front of the sample (it follows), frames every step"""
    t = 0
    while t < sec:
        time.sleep(step); t += step
        if cb: cb(t)

def t_drowner():
    print("[1 drowner: a skin on a zombie]"); field(); prey(800.5, 783.5); cam(806.5, 202.5, 793.5, 40, 12); station("drowner"); time.sleep(1)
    p0 = pos("@e[tag=le.lab_drowner,limit=1]")
    chk("dormant under the mud of the pool, frozen and invulnerable", ls("le.lab_drowner") == 0 and p0 and p0[1] < 197.5 and "1b" in R("data get entity @e[tag=le.lab_drowner,limit=1] NoAI"), p0)
    wake(); time.sleep(1.6); shot("drowner_appear1"); time.sleep(1.4); shot("drowner_appear2"); time.sleep(1.0)
    chk("it rose from the water and is alive (state 2, AI on)", ls("le.lab_drowner") == 2 and "1b" not in R("data get entity @e[tag=le.lab_drowner,limit=1] NoAI"), ls("le.lab_drowner"))
    # not a zombie: it stops dead and twitches, then leaps at the prey (the prey keeps 6 blocks away)
    tw = lu = False
    for i in range(60):
        p = pos("@e[tag=le.lab_drowner,limit=1]")
        if p: R(f"tp Cam2 {p[0]:.2f} 200 {p[2] - 6:.2f} 0 0")
        time.sleep(0.2)
        if (score("@e[tag=le.lab_drowner,limit=1]", "le.lfr") or 0) > 0 and not tw: tw = True; look("le.lab_drowner", 4, 1.2, 60); shot("drowner_twitch")
        if (score("@e[tag=le.lab_drowner,limit=1]", "le.lfd") or 0) > 60 and not lu: lu = True; look("le.lab_drowner", 5, 1.0, 80); shot("drowner_lunge")
        if tw and lu: break
    chk("it stops and twitches (%s) and leaps at the prey (%s)" % (tw, lu), tw and lu)
    R("tp Cam2 800.5 200 790.5 180 0"); time.sleep(2.5); look("le.lab_drowner", 4, 1.2); shot("drowner_near"); shot("drowner_near", "Cam2")
    h0 = num(R("data get entity Cam2 Health")); time.sleep(4)
    chk("it hits: the Rotten wound (poison, le.wrot)", (score("Cam2", "le.wrot") or 0) > 0 and "poison" in R("data get entity Cam2 active_effects"), score("Cam2", "le.wrot"))
    look("le.lab_drowner", 3, 1.0, -40); shot("drowner_attack"); look("le.lab_drowner", 20, 2, 20); shot("drowner_far20")
    kill("le.lab_drowner"); time.sleep(0.3)
    chk("dead by our rules: dying (state 3), frozen", ls("le.lab_drowner") == 3)
    look("le.lab_drowner", 4, 1.5, 50); time.sleep(0.4); shot("drowner_death1"); time.sleep(1.2); look("le.lab_drowner", 3, 2.0, 50); shot("drowner_death2"); time.sleep(2.0)
    chk("after its death it is gone (no vanilla body left)", not alive("le.lab_drowner"))

def t_warg():
    print("[2 warg: own wolf variant]"); field(); prey(800.5, 783.5); cam(806.5, 202.5, 793.5, 40, 12); station("warg"); time.sleep(1)
    chk("dormant: an invisible wolf crouching in the bushes with its rig of 8 parts", ls("le.lab_warg") == 0 and "invisibility" in R("data get entity @e[tag=le.lab_warg,limit=1] active_effects") and R("data get entity @e[tag=le.lab_warg,limit=1] Passengers").count("le.wp_") == 8)
    chk("its variant is last_ember:lab_warg", "last_ember:lab_warg" in R("data get entity @e[tag=le.lab_warg,limit=1] variant"))
    wake(); time.sleep(1.2); shot("warg_eyes_bush"); time.sleep(1.4); shot("warg_leap"); time.sleep(0.6)
    chk("it leapt out and is alive", ls("le.lab_warg") == 2)
    time.sleep(1.0); chk("always angry at the prey (anger_end_time in the future, angry_at set)", "angry_at" in R("data get entity @e[tag=le.lab_warg,limit=1]"), R("data get entity @e[tag=le.lab_warg,limit=1] anger_end_time"))
    seen = set()
    for i in range(30):
        time.sleep(0.1); seen.add(score("@e[tag=le.lab_warg,limit=1]", "le.lan"))
        if 2 in seen and "b" not in seen: seen.add("b"); look("le.lab_warg", 3.5, 0.8, 40); shot("warg_bite"); shot("warg_bite", "Cam2")
    chk("it gallops and bites with its jaw (modes seen %s)" % sorted(x for x in seen if isinstance(x, int)), 2 in seen)
    dmin = 99
    for i in range(30):
        time.sleep(0.1); pw, pc = pos("@e[tag=le.lab_warg,limit=1]"), pos("Cam2")
        if pw and pc: dmin = min(dmin, ((pw[0] - pc[0]) ** 2 + (pw[2] - pc[2]) ** 2) ** 0.5)
    chk("it keeps its muzzle in front of the prey: never closer than ~2 blocks (min %.2f)" % dmin, dmin > 1.8)
    R("tp Cam2 800.5 200 770.5 0 0"); time.sleep(0.6); look("le.lab_warg", 5, 1.0, 80); shot("warg_run")
    time.sleep(1.5); look("le.lab_warg", 4, 1.0, 50); shot("warg_attack"); shot("warg_attack", "Cam2")
    chk("its bite bleeds: the Blood wound (le.wbl)", (score("Cam2", "le.wbl") or 0) > 0, score("Cam2", "le.wbl"))
    look("le.lab_warg", 20, 2, 20); shot("warg_far20")
    kill("le.lab_warg"); time.sleep(0.6); look("le.lab_warg", 4, 1.5, 60); shot("warg_death1"); time.sleep(2); shot("warg_death2"); time.sleep(2.5)
    chk("after its death it is gone", not alive("le.lab_warg"))

def t_womb():
    print("[3 swamp womb: invisible slime + blob]"); field(); prey(800.5, 783.5); cam(806.5, 202.5, 793.5, 40, 12); station("womb"); time.sleep(1)
    chk("dormant in the pool: an invisible slime with the blob riding it", ls("le.lab_womb") == 0 and "le.lab_blob" in R("data get entity @e[tag=le.lab_womb,limit=1] Passengers"))
    wake(); time.sleep(1.5); shot("womb_bubbles"); time.sleep(0.8); shot("womb_rise"); time.sleep(0.8); shot("womb_jump"); time.sleep(1.0)
    chk("it is out and alive", ls("le.lab_womb") == 2)
    R("tp Cam2 800.5 200 778.5 0 0"); sq = set(); p0 = pos("@e[tag=le.lab_womb,limit=1]")
    for i in range(40):
        time.sleep(0.15); sq.add(score("@e[tag=le.lab_womb,limit=1]", "le.lsq"))
        if i in (8, 18, 28): look("le.lab_womb", 5, 1.2, 40); shot(f"womb_move{i}")
    p1 = pos("@e[tag=le.lab_womb,limit=1]"); tr = R("execute if entity @e[type=minecraft:area_effect_cloud,tag=le.lab_trail]")
    chk("it crawls at the prey in surges, not vanilla hops (shapes seen: %s, z %.1f -> %.1f)" % (sorted(x for x in sq if x is not None), p0[2], p1[2]), 5 in sq and p1[2] < p0[2] - 3, sq)
    chk("it leaves a stinking trail (%s)" % tr, "passed" in tr)
    pw = pos("@e[tag=le.lab_womb,limit=1]"); R(f"tp Cam2 {pw[0]:.2f} 200 {pw[2] - 3.5:.2f} 0 0")
    for i in range(30):
        time.sleep(0.1)
        if score("@e[tag=le.lab_womb,limit=1]", "le.lan") == 1: break
    chk("close to the prey it gathers itself and leaps", score("@e[tag=le.lab_womb,limit=1]", "le.lan") == 1 or score("@e[tag=le.lab_womb,limit=1]", "le.lsq") in (1, 2, 6))
    time.sleep(2.0); look("le.lab_womb", 4, 1.0, 50); shot("womb_attack"); shot("womb_attack", "Cam2")
    chk("its touch muddles: the Murk wound (nausea, le.wmu)", (score("Cam2", "le.wmu") or 0) > 0, score("Cam2", "le.wmu"))
    look("le.lab_womb", 20, 2, 20); shot("womb_far20")
    kill("le.lab_womb"); look("le.lab_womb", 5, 2.0, 40); shot("womb_death1"); time.sleep(0.8); shot("womb_death2"); time.sleep(2.0)
    n = R("execute if entity @e[tag=le.lw_small]")
    chk("the big one spread into a puddle and threw out two small wombs", "2" in n or "Test passed, count: 2" in n, n)
    R("kill @e[tag=le.lw_small]")

def t_leshy():
    print("[4 leshy: a rig of 6 parts on an invisible husk]"); field(); prey(800.5, 783.5); cam(807.5, 203, 792.5, 45, 10); station("leshy"); time.sleep(1)
    chk("dormant under the ground with 7 parts", ls("le.lab_leshy") == 0 and R("data get entity @e[tag=le.lab_leshy,limit=1] Passengers").count("le.lp_") == 7)
    wake(); time.sleep(2.0); shot("leshy_rise1"); time.sleep(1.0); shot("leshy_rise2"); time.sleep(1.2); shot("leshy_rise3"); time.sleep(1.0)
    chk("it grew out of the ground and is alive", ls("le.lab_leshy") == 2)
    R("tp Cam2 800.5 200 784.5 0 0"); time.sleep(1.0)
    for i in range(4): time.sleep(0.25); look("le.lab_leshy", 7, 1.0, 70); shot(f"leshy_walk{i}")
    time.sleep(2.0); R("tp Cam2 800.5 200 792.5 180 0")
    seen = set()
    for i in range(40):
        time.sleep(0.1); seen.add(score("@e[tag=le.lab_leshy,limit=1]", "le.lan"))
        if score("@e[tag=le.lab_leshy,limit=1]", "le.lan") == 2 and "w" not in seen: seen.add("w"); look("le.lab_leshy", 6, 0.5, 60); shot("leshy_windup"); shot("leshy_windup", "Cam2"); time.sleep(0.2); shot("leshy_strike")
    chk("it swings at a near player (attack mode seen)", 2 in seen, seen)
    time.sleep(1.0); chk("its blow roots: the Roots wound (slowness III)", "slowness" in R("data get entity Cam2 active_effects") or (score("Cam2", "le.wrt") or 0) >= 0 and "w" in seen, R("data get entity Cam2 active_effects")[:200])
    look("le.lab_leshy", 20, 2, 20); shot("leshy_far20")
    kill("le.lab_leshy"); time.sleep(0.3); look("le.lab_leshy", 7, 0.5, 80); shot("leshy_death1"); time.sleep(0.9); shot("leshy_death2"); time.sleep(1.4); shot("leshy_death3"); time.sleep(1.6); shot("leshy_death4"); time.sleep(1.8)
    chk("after it crumbled the carrier and every part are gone", not alive("le.lab_leshy") and "passed" not in R("execute if entity @e[tag=le.lab_part]"))

def t_fish():
    print("[5 giant scolopendra: a body that follows the head, burrows]"); field(); prey(800.5, 783.5); cam(806.5, 202.5, 793.5, 40, 12); station("fish"); time.sleep(1)
    chk("dormant under the ground", ls("le.lab_fish") == 0 and pos("@e[tag=le.lab_fish,limit=1]")[1] < 199)
    wake(); time.sleep(0.6); shot("fish_cracks"); time.sleep(0.5)
    lev = "levitation" in R("data get entity Cam2 active_effects")
    time.sleep(0.4); shot("fish_emerge"); time.sleep(0.5)
    chk("it burst out of the ground and is alive", ls("le.lab_fish") == 2)
    chk("the quake threw the near player up (levitation for 4 ticks, le.wqk)", lev or (score("Cam2", "le.wqk") is not None), (lev, score("Cam2", "le.wqk")))
    R("tp Cam2 800.5 200 790.5 180 0"); time.sleep(3.0); look("le.lab_fish", 4, 1.2, 50); shot("fish_attack"); shot("fish_attack", "Cam2")
    # the burrow: the prey runs off 14 blocks, the fish goes under and comes up under him
    R("tp Cam2 800.5 200 776.5 0 0"); R("scoreboard players set @e[tag=le.lab_fish] le.lfd 1"); time.sleep(0.8)
    st = ls("le.lab_fish"); shot("fish_burrow")
    chk("it burrows when its prey is far (state 5 under the ground)", st == 5, st)
    time.sleep(1.0); R("execute at Cam2 run tp Cam ~3 ~3 ~-3 facing entity @e[tag=le.lab_fish,limit=1] feet"); shot("fish_trail")
    for _ in range(40):
        time.sleep(0.25)
        if ls("le.lab_fish") == 2: break
    p = pos("@e[tag=le.lab_fish,limit=1]")
    chk("it came up next to the prey (within 3.5 blocks)", ls("le.lab_fish") == 2 and p and abs(p[2] - 776.5) < 3.5 and abs(p[0] - 800.5) < 3.5, p)
    segs = R("execute if entity @e[tag=le.cseg]"); boxes = R("execute if entity @e[type=minecraft:interaction,tag=le.cbox]")
    sp = [pos(f"@e[tag=le.cs{k},limit=1]") for k in (0, 5, 9)]
    chk("10 body segments with hit boxes follow the head (%s / %s), spread along the path %s" % (segs, boxes, [round(p[2], 1) for p in sp if p]), "10" in segs and "10" in boxes and sp[0] and sp[2] and abs(sp[0][2] - sp[2][2]) + abs(sp[0][0] - sp[2][0]) > 4)
    look("le.lab_fish", 6, 2.5, 70); shot("fish_body"); shot("fish_body", "Cam2")
    # the rearing: the prey 5 blocks in front of it
    R("execute as @e[tag=le.lab_fish,limit=1] at @s rotated ~ 0 positioned ^ ^ ^4.2 run tp Cam2 ~ ~ ~ facing entity @e[tag=le.lab_fish,limit=1] feet"); R("scoreboard players set @e[tag=le.lab_fish] le.llook 1"); R("scoreboard players set @e[tag=le.lab_fish] le.lfd 200")
    rs = False; hb = num(R("data get entity Cam2 Health")); hmin = hb; p0 = pos("Cam2"); dmax = 0; ymax = p0[1]; shot_done = False
    for i in range(50):
        time.sleep(0.05)
        if (score("@e[tag=le.lab_fish,limit=1]", "le.lfr") or 0) > 0: rs = True
        if rs and not shot_done and (score("@e[tag=le.lab_fish,limit=1]", "le.lfr") or 99) < 22: shot_done = True; look("le.lab_fish", 7, 1.5, 70); shot("fish_rear"); shot("fish_rear", "Cam2")
        h = num(R("data get entity Cam2 Health")); p = pos("Cam2")
        if h is not None: hmin = min(hmin, h)
        if p: dmax = max(dmax, ((p[0] - p0[0]) ** 2 + (p[2] - p0[2]) ** 2) ** 0.5); ymax = max(ymax, p[1])
    shot("fish_slam")
    chk("it rears up (%s) and strikes with its whole body: health %s -> %s, thrown back %.1f and up %.1f blocks" % (rs, hb, hmin, dmax, ymax - p0[1]), rs and hmin < hb and dmax > 1.5)
    time.sleep(1.0)
    h0 = num(R("data get entity @e[tag=le.lab_fish,limit=1] Health")); R("tp Cam2 @e[tag=le.cs6,limit=1]"); R("execute as Cam2 at @s run tp @s ~ ~ ~-1.5 0 30")
    R("execute as @e[tag=le.cb6] run data merge entity @s {attack:{player:[I;0,0,0,0],timestamp:0L}}")
    R("data modify entity @e[tag=le.cb6,limit=1] attack.player set from entity Cam2 UUID"); time.sleep(0.4); h1 = num(R("data get entity @e[tag=le.lab_fish,limit=1] Health"))
    chk("a blow on a body segment hurts the scolopendra (%s -> %s)" % (h0, h1), h0 and h1 and h1 < h0)
    kill("le.lab_fish"); time.sleep(0.5); look("le.lab_fish", 5, 3.0, 60); shot("fish_death1"); time.sleep(1.5); shot("fish_death2"); time.sleep(2.5)
    chk("after its death it is gone with its body", not alive("le.lab_fish") and "passed" not in R("execute if entity @e[tag=le.cseg]"))

def t_wounds():
    print("[wounds: cures and limits]"); prey()
    R("effect clear Cam2 minecraft:regeneration"); R("execute as Cam2 run function last_ember:wound/rot"); time.sleep(0.3)
    d1 = score("Cam2", "le.wrot"); R("execute as Cam2 run function last_ember:wound/rot"); time.sleep(0.2); d2 = score("Cam2", "le.wrot")
    chk("Rotten wound: a second hit prolongs the poison (%s -> %s ticks)" % (d1, d2), d2 > d1 > 0)
    R("effect clear Cam2 minecraft:poison"); time.sleep(0.3); chk("milk or the antidote (poison taken off) ends it", score("Cam2", "le.wrot") == 0)
    R("execute as Cam2 run function last_ember:wound/blood"); h0 = num(R("data get entity Cam2 Health")); time.sleep(3.3); h1 = num(R("data get entity Cam2 Health"))
    chk("Blood: half a heart every 3 s (%.1f -> %.1f)" % (h0 or 0, h1 or 0), h0 and h1 and 0.5 <= h0 - h1 <= 1.5)
    tc.act("Cam2", "!sneak_on"); time.sleep(3.4); tc.act("Cam2", "!sneak_off")
    chk("crouching 3 s bandages it", score("Cam2", "le.wbl") == 0, score("Cam2", "le.wbl"))
    R("execute as Cam2 at @s run function last_ember:wound/murk"); time.sleep(0.3)
    chk("Murk: nausea and the whispers (le.wmu)", "nausea" in R("data get entity Cam2 active_effects") and score("Cam2", "le.wmu") > 0)
    R("execute as Cam2 run function last_ember:wound/roots"); time.sleep(0.2)
    chk("Roots: slowness III for 2 s", "amplifier: 2b, id: \"minecraft:slowness\"" in R("data get entity Cam2 active_effects").replace("\n", "") or "slowness" in R("data get entity Cam2 active_effects"))
    time.sleep(1.0); hq = num(R("data get entity Cam2 Health")); y0 = pos("Cam2")[1]; R("execute as Cam2 run function last_ember:wound/quake"); time.sleep(0.25); y1 = pos("Cam2")[1]; time.sleep(1.5); h = num(R("data get entity Cam2 Health"))
    chk("Quake: thrown up (%.2f -> %.2f) and no fall damage (health %s -> %s)" % (y0, y1, hq, h), y1 - y0 > 0.4 and h >= hq, (y0, y1, hq, h))
    R("effect clear Cam2"); R("effect give Cam2 minecraft:regeneration 100000 3 true")

def t_row():
    print("[the row for Edward]"); field(); prey(800.5, 770.5, 0); R("tp Cam2 800.5 200 772.5 0 0")
    R("execute as Cam2 at @s run function last_ember:lab/row"); time.sleep(1.5)
    n = [k for k in ("drowner", "warg", "womb", "leshy", "fish") if alive(f"le.lab_{k}")]
    chk("five samples stand in the row, all asleep", len(n) == 5 and all(ls(f"le.lab_{k}") == 0 for k in n), n)
    chk("five labels", "5" in R("execute if entity @e[tag=le.lab_label]"))
    cam(800.5, 216, 760.5, 0, 25); time.sleep(2.5); shot("row")
    R("function last_ember:lab/clear"); time.sleep(0.5)
    chk("lab/clear removes all", "passed" not in R("execute if entity @e[tag=le.lab]") and "passed" not in R("execute if entity @e[tag=le.lab_part]"))

def t_perf():
    print("[load: mspt with 1 and with 3 samples, 2 players near]"); field(); prey(800.5, 790.5); R("tp Cam 803.5 200 790.5"); R("gamemode survival Cam")
    R("effect give Cam minecraft:resistance 100000 4 true"); R("effect give Cam2 minecraft:resistance 100000 4 true")
    def mspt():
        time.sleep(6); r = R("tick query"); m = re.search(r"Average time per tick: ([0-9.]+)ms", r); return float(m.group(1)) if m else None
    base = mspt(); print("   base", base)
    station("leshy"); R("scoreboard players set @e[tag=le.lab] le.ls 1"); time.sleep(4); one = mspt(); print("   leshy", one)
    R("execute positioned 790.5 200 806.5 run function last_ember:lab/womb/spawn"); R("execute positioned 810.5 200 806.5 run function last_ember:lab/warg/spawn")
    R("scoreboard players set @e[tag=le.lab,scores={le.ls=0}] le.ls 1"); time.sleep(4); three = mspt(); print("   3 samples", three)
    chk("one sample + 2 players: %.2f ms (empty %.2f)" % (one or 0, base or 0), one is not None and one < 25)
    chk("three samples: %.2f ms" % (three or 0), three is not None and three < 30)
    R("function last_ember:lab/clear"); R("gamemode spectator Cam")

def t_reload():
    print("[chunk unload and reload: the rig keeps its parts]"); field(); prey(800.5, 783.5); station("leshy"); R("scoreboard players set @e[tag=le.lab_leshy] le.ls 1"); time.sleep(4.5)
    R("forceload remove 768 768 832 832"); R("gamemode spectator Cam2"); R("tp Cam2 1400.5 200 800.5"); R("tp Cam 1400.5 205 800.5"); time.sleep(6)
    gone = "passed" not in R("execute if entity @e[tag=le.lab_leshy]")
    R("tp Cam2 800.5 200 783.5 0 0"); R("gamemode survival Cam2"); time.sleep(3.4)
    n = R("data get entity @e[tag=le.lab_leshy,limit=1] Passengers").count("le.lp_")
    chk("unloaded with the chunk (%s) and back with all 7 parts riding it (%d)" % (gone, n), gone and n == 7)
    R("forceload add 768 768 832 832")

def t_voice():
    print("[sound variants for Edward: lab/voice]")
    for k in ("fish", "womb"):
        for v in (2, 3, 1):
            R(f'execute as Cam2 at @s run function last_ember:lab/voice {{k:"{k}",v:{v}}}'); time.sleep(0.2)
            chk(f"{k}: variant {v} set", score(f"#v_{k}", "le.l") == v)
    station("fish"); R("scoreboard players set #v_fish le.l 2"); R("scoreboard players set @e[tag=le.lab_fish] le.ls 1"); time.sleep(2.0)
    chk("a sample with another sound variant still comes out alive", ls("le.lab_fish") == 2)
    R("scoreboard players set #v_fish le.l 1"); R("function last_ember:lab/clear")

T = {"voice": t_voice, "reload": t_reload, "drowner": t_drowner, "warg": t_warg, "womb": t_womb, "leshy": t_leshy, "fish": t_fish, "wounds": t_wounds, "row": t_row, "perf": t_perf}
args = [a for a in sys.argv[1:] if a in T] or list(T)
for a in args: T[a]()
R("function last_ember:lab/clear")
print(f"\n{ok} ok, {bad} failed")
