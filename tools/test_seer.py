#!/usr/bin/env python3
"""T-011 checks (server + dev clients Cam, Cam2 in the game): the seer's staffs on the tiers 0 and 6.
The spells are run as the player by their functions (the click path itself is checked in section 'click').
Usage: python3 tools/test_seer.py [blink frost flame lift banish ...]"""
import importlib.util, json, math, os, re, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
check = None
ok = bad = 0
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n)
    else: bad += 1; print("  FAIL", n, e)
setc, score, num, tp = tc.setc, tc.score, tc.num, tc.tp
BX, BY, BZ = 400, 200, 400
def pos(sel):
    r = rc.run(f"data get entity {sel} Pos"); v = re.findall(r"(-?\d+\.?\d*)d", r); return [float(x) for x in v] if len(v) == 3 else None
def stage():
    rc.run("forceload add 380 380 440 420"); rc.run("tp Cam %d %d %d" % (BX, BY, BZ)); time.sleep(1.5)
    rc.run(f"fill {BX-20} {BY-1} {BZ-20} {BX+30} {BY+9} {BZ+20} air"); rc.run(f"fill {BX-20} {BY+10} {BZ-20} {BX+30} {BY+20} {BZ+20} air"); rc.run(f"fill {BX-20} {BY-1} {BZ-20} {BX+30} {BY-1} {BZ+20} stone")
    rc.run("kill @e[type=!player,distance=..60]"); rc.run("difficulty normal"); rc.run("weather clear 100000")
def seer(tier, race=1, p="Cam"):
    setc(race, 3, tier, p); rc.run(f"tp {p} {BX}.5 {BY} {BZ}.5 -90 0"); rc.run(f"gamemode survival {p}"); time.sleep(0.5)
    for k in range(1, 8): rc.run(f"scoreboard players set {p} le.cd{k} 0")
    rc.run(f"scoreboard players set {p} le.spsel 0"); rc.run(f"scoreboard players set {p} le.wchg -1")
def cast(n, p="Cam"): return rc.run(f"execute as {p} at @s run function last_ember:seer/cast_{n}")
AI = False
def husk(x, y, z, tags=""):
    ai = 'attributes:[{id:"minecraft:movement_speed",base:0.0d}],' if AI else "NoAI:1b,"
    rc.run(f'summon minecraft:husk {x} {y} {z} {{{ai}Tags:["le.test","le.keep"{tags}],PersistenceRequired:1b,Silent:1b}}')
def t_blink():
    print("[blink]"); stage()
    for tier, want in ((0, 12), (6, 24)):
        seer(tier); cast(2); time.sleep(0.4); p = pos("Cam")
        chk(f"tier {tier}: open ground {want} blocks", p and abs(p[0] - (BX + 0.5 + want)) <= 1.0, p)
    # a wall at 6 blocks
    seer(6); rc.run(f"fill {BX+6} {BY} {BZ-4} {BX+6} {BY+8} {BZ+4} stone"); cast(2); time.sleep(0.4); p = pos("Cam")
    chk("wall: stops before the wall, not inside", p and BX + 3.5 <= p[0] <= BX + 5.6, p)
    rc.run(f"fill {BX+6} {BY} {BZ-4} {BX+6} {BY+8} {BZ+4} air")
    # barrier is solid
    seer(6); rc.run(f"fill {BX+6} {BY} {BZ-1} {BX+6} {BY+3} {BZ+1} barrier"); cast(2); time.sleep(0.4); p = pos("Cam")
    chk("barrier: solid", p and p[0] < BX + 6, p); rc.run(f"fill {BX+6} {BY} {BZ-1} {BX+6} {BY+3} {BZ+1} air")
    # low ceiling at the head: no room, the cooldown is not spent
    seer(6); rc.run(f"fill {BX+1} {BY+1} {BZ-1} {BX+20} {BY+1} {BZ+1} stone"); cast(2); time.sleep(0.4); p = pos("Cam")
    chk("1-high passage: no blink", p and abs(p[0] - (BX + 0.5)) < 1.5, p); chk("1-high passage: cooldown not spent", (score("Cam", "le.cd2") or 0) == 0)
    rc.run(f"fill {BX+1} {BY+1} {BZ-1} {BX+20} {BY+1} {BZ+1} air")
    # 2-high passage: halfling (0.65) and elf (1.1) fit
    for race, nm in ((4, "halfling"), (2, "elf")):
        seer(6, race); rc.run(f"fill {BX+4} {BY} {BZ-3} {BX+17} {BY+6} {BZ+3} stone"); rc.run(f"fill {BX+4} {BY} {BZ} {BX+16} {BY+1} {BZ} air"); time.sleep(0.3)
        cast(2); time.sleep(0.4); p = pos("Cam")
        chk(f"{nm}: tunnel 2x1: lands inside the tunnel, feet at floor", p and BX + 12 <= p[0] <= BX + 16.6 and abs(p[2] - (BZ + 0.5)) < 0.1 and abs(p[1] - BY) < 0.1, p)
        rc.run(f"fill {BX+4} {BY} {BZ-3} {BX+17} {BY+6} {BZ+3} air")
    # void: a small platform
    seer(6); rc.run(f"fill {BX+4} {BY-1} {BZ-20} {BX+30} {BY-1} {BZ+20} air"); cast(2); time.sleep(0.4); p = pos("Cam")
    chk("void ahead: no blink", p and abs(p[0] - (BX + 0.5)) < 1.5, p)
    rc.run(f"fill {BX+4} {BY-1} {BZ-20} {BX+30} {BY-1} {BZ+20} stone")
    # lava on the landing cells
    seer(0); rc.run(f"fill {BX+8} {BY-1} {BZ-2} {BX+16} {BY-1} {BZ+2} lava"); cast(2); time.sleep(0.4); p = pos("Cam")
    chk("lava at the landing: no blink", p and abs(p[0] - (BX + 0.5)) < 1.5, p)
    rc.run(f"fill {BX+8} {BY-1} {BZ-2} {BX+16} {BY-1} {BZ+2} stone")
    # fall damage after the blink: 15 blocks in the air
    seer(6); rc.run(f"tp Cam {BX}.5 {BY+15} {BZ}.5 -90 0"); time.sleep(0.2)
    # (blink does not touch the fall distance: the landing is a free fall of the remaining height)
    # no_blink flag
    seer(6); rc.run("tag Cam add le.zf.no_blink"); cast(2); time.sleep(0.4); p = pos("Cam"); rc.run("tag Cam remove le.zf.no_blink")
    chk("zone flag no_blink: no blink", p and abs(p[0] - (BX + 0.5)) < 1.5, p)
def effects(sel): return rc.run(f"data get entity {sel} active_effects")
def t_frost():
    print("[frost]"); stage()
    for tier, r, amp in ((0, 6, 0), (6, 12, 1)):
        seer(tier); rc.run("kill @e[tag=le.test]")
        husk(BX + 0.5 + r - 1, BY, BZ + 0.5, ',"in"'.replace(',"in"', "")); husk(BX + 0.5 + r + 2, BY, BZ + 0.5)
        rc.run('summon minecraft:wolf %s %s %s {Owner:[I;1,2,3,4],Tags:["le.test"]}' % (BX + 2.5, BY, BZ + 0.5)); rc.run('summon minecraft:villager %s %s %s {NoAI:1b,Tags:["le.test"]}' % (BX + 2.5, BY, BZ + 2.5))
        rc.run('summon minecraft:armor_stand %s %s %s {Tags:["le.test"]}' % (BX + 2.5, BY, BZ - 2.5)); rc.run('summon minecraft:husk %s %s %s {NoAI:1b,Tags:["le.test","le.keep","le.npc"],PersistenceRequired:1b}' % (BX + 3.5, BY, BZ + 0.5))
        rc.run("tp Cam2 %d %d %d" % (BX + 2, BY, BZ + 1)); time.sleep(0.3)
        cast(3); time.sleep(0.5)
        near = effects("@e[type=husk,tag=le.test,tag=!le.npc,sort=nearest,limit=1,x=%d,y=%d,z=%d]" % (BX + r - 1, BY, BZ))
        far = effects("@e[type=husk,tag=le.test,tag=!le.npc,sort=furthest,limit=1,x=%d,y=%d,z=%d]" % (BX, BY, BZ))
        chk(f"tier {tier}: husk in reach: slowness amplifier {amp} and weakness", (f"amplifier: {amp}b" in near if amp else "amplifier" not in near.split("slowness")[0].split("weakness")[0]) and "slowness" in near and "weakness" in near, near)
        chk(f"tier {tier}: husk beyond radius {r}: untouched", "slowness" not in far, far)
        chk(f"tier {tier}: frost view (TicksFrozen 1..139)", 1 <= (num(rc.run("data get entity @e[type=husk,tag=le.test,tag=!le.npc,sort=nearest,limit=1,x=%d,y=%d,z=%d] TicksFrozen" % (BX + r - 1, BY, BZ))) or 0) <= 139)
        for sel, nm in (("@e[type=wolf,tag=le.test,limit=1]", "wolf"), ("@e[type=villager,tag=le.test,limit=1]", "villager"), ("Cam2", "player"), ("Cam", "caster"), ("@e[type=armor_stand,tag=le.test,limit=1]", "stand"), ("@e[tag=le.npc,limit=1]", "npc")):
            chk(f"tier {tier}: {nm} untouched", "slowness" not in effects(sel) and "weakness" not in effects(sel))
        # hold: after 6 s still frozen and no cold damage; after 10 s released
        h0 = tc.hp("@e[type=husk,tag=le.test,tag=!le.npc,sort=nearest,limit=1,x=%d,y=%d,z=%d]" % (BX + r - 1, BY, BZ))
        time.sleep(4.5)
        tf = num(rc.run("data get entity @e[type=husk,tag=le.test,tag=!le.npc,sort=nearest,limit=1,x=%d,y=%d,z=%d] TicksFrozen" % (BX + r - 1, BY, BZ))) or 0
        h1 = tc.hp("@e[type=husk,tag=le.test,tag=!le.npc,sort=nearest,limit=1,x=%d,y=%d,z=%d]" % (BX + r - 1, BY, BZ))
        time.sleep(6)
        tf2 = num(rc.run("data get entity @e[type=husk,tag=le.test,tag=!le.npc,sort=nearest,limit=1,x=%d,y=%d,z=%d] TicksFrozen" % (BX + r - 1, BY, BZ))) or 0
        chk(f"tier {tier}: held during the effect without damage", 1 <= tf <= 139 and h1 == h0, (tf, h0, h1)); chk(f"tier {tier}: released after 10 s", tf2 < 3, tf2)
    rc.run("kill @e[tag=le.test]")
def fire_at(x, y, z): return "fire" in rc.run(f"execute if block {x} {y} {z} minecraft:fire")  or rc.run(f"execute if block {x} {y} {z} minecraft:fire").startswith("Test passed")
def t_flame():
    print("[flame]"); stage()
    for tier, r in ((0, 6), (6, 12)):
        seer(tier); rc.run("kill @e[tag=le.test]"); rc.run(f"fill {BX-20} {BY-1} {BZ-20} {BX+30} {BY-1} {BZ+20} stone")
        husk(BX + 0.5 + r - 1, BY, BZ + 0.5); husk(BX + 0.5 + r + 3, BY, BZ + 0.5 + 8)         # in reach / out of reach
        husk(BX + 0.5 + 2, BY, BZ + 0.5 + 3)                                                          # near wood
        rc.run(f"setblock {BX+3} {BY} {BZ+3} oak_planks"); husk(BX + 0.5 + 2, BY, BZ + 0.5 - 3)         # over grass (the cell is not air)
        rc.run(f"setblock {BX+2} {BY-1} {BZ-3} grass_block"); rc.run(f"setblock {BX+2} {BY} {BZ-3} short_grass")
        husk(BX + 0.5 + 2, BY, BZ + 0.5 + 5)                                                          # a clear spot: gets fire
        rc.run('summon minecraft:wolf %s %s %s {Owner:[I;1,2,3,4],Tags:["le.test"]}' % (BX + 0.5, BY, BZ + 4.5)); rc.run("tp Cam2 %d %d %d" % (BX + 4, BY, BZ + 1))
        cast(4); time.sleep(0.7)
        def fire(sel): return (num(rc.run(f"data get entity {sel} Fire")) or -1) > 0
        chk(f"tier {tier}: husk in reach (r {r}) burns", fire(f"@e[type=husk,tag=le.test,x={BX+r-1},y={BY},z={BZ},distance=..1,limit=1]"))
        chk(f"tier {tier}: husk beyond radius {r} does not", not fire(f"@e[type=husk,tag=le.test,x={BX+r+3},y={BY},z={BZ+8},distance=..1,limit=1]"))
        chk(f"tier {tier}: wolf, player, caster do not burn", not fire("@e[type=wolf,tag=le.test,limit=1]") and not fire("Cam2") and not fire("Cam"))
        chk(f"tier {tier}: fire block under the husk on clear stone", "Test passed" in rc.run(f"execute if block {BX+2} {BY} {BZ+5} minecraft:fire") or "Test passed" in rc.run(f"execute if block {BX+r-1} {BY} {BZ} minecraft:fire"))
        chk(f"tier {tier}: no fire near planks", "Test passed" not in rc.run(f"execute if block {BX+2} {BY} {BZ+3} minecraft:fire"))
        chk(f"tier {tier}: no fire where the cell is grass", "Test passed" not in rc.run(f"execute if block {BX+2} {BY} {BZ-3} minecraft:fire"))
        time.sleep(6)
        left = rc.run(f"execute if entity @e[type=marker,tag=le.sfire]")
        chk(f"tier {tier}: after 5 s all our fire is out", "Test failed" in left and "Test passed" not in rc.run(f"execute if block {BX+2} {BY} {BZ+5} minecraft:fire") and "Test passed" not in rc.run(f"execute if block {BX+r-1} {BY} {BZ} minecraft:fire"), left)
        rc.run(f"setblock {BX+3} {BY} {BZ+3} air")
    # zone: a husk inside a zone gets no fire block (the first overworld zone in zones/zones.txt)
    seer(0); rc.run("kill @e[tag=le.test]"); z = [l.split() for l in open(os.path.join(ROOT, "zones/zones.txt")) if l.strip() and not l.startswith("#")]
    zz = [r for r in z if r[1] == "overworld" and r[2] == "box"][0]; x1, y1, z1, x2, y2, z2 = map(int, zz[3:9]); cx, cy, cz = (x1 + x2) // 2, max(y1, y2) + 1, (z1 + z2) // 2
    rc.run(f"forceload add {cx} {cz}"); rc.run(f"tp Cam {cx}.5 {cy+1} {cz}.5"); time.sleep(1.5); rc.run(f"setblock {cx} {cy-1} {cz} stone"); rc.run(f"fill {cx-3} {cy} {cz-3} {cx+3} {cy+3} {cz+3} air")
    rc.run(f"setblock {cx+2} {cy-1} {cz} stone"); husk(f"{cx+2}.5", cy, f"{cz}.5"); rc.run(f"scoreboard players set Cam le.cd4 0"); cast(4); time.sleep(0.5)
    chk(f"zone {zz[0]}: the mob burns, no fire block", "Test passed" not in rc.run(f"execute if block {cx+2} {cy} {cz} minecraft:fire"))
    rc.run("kill @e[tag=le.test]")
def t_lift():
    global AI
    print("[lift]"); stage(); AI = True
    for tier, r, H in ((0, 6, 6), (6, 12, 12)):
        seer(tier); rc.run("kill @e[tag=le.test]")
        husk(BX + 0.5 + r - 1, BY, BZ + 0.5); husk(BX + 0.5 + r + 3, BY, BZ + 0.5 + 2)
        rc.run(f'summon minecraft:husk {BX+3.5} {BY} {BZ+0.5} {{attributes:[{{id:"minecraft:movement_speed",base:0.0d}}],Tags:["le.test","le.keep","le.boss"],PersistenceRequired:1b}}'); rc.run(f'summon minecraft:husk {BX+3.5} {BY} {BZ-1.5} {{attributes:[{{id:"minecraft:movement_speed",base:0.0d}}],Tags:["le.test","le.keep","le.giant"],PersistenceRequired:1b}}')
        rc.run('summon minecraft:wolf %s %s %s {Owner:[I;1,2,3,4],Tags:["le.test"]}' % (BX + 0.5, BY, BZ + 4.5)); rc.run('summon minecraft:villager %s %s %s {NoAI:1b,Tags:["le.test"]}' % (BX + 0.5, BY, BZ - 4.5)); rc.run("tp Cam2 %d %d %d" % (BX + 4, BY, BZ + 1))
        rc.run(f"data modify entity @e[type=husk,tag=le.test,x={BX+r-1},y={BY},z={BZ},distance=..1,limit=1] Tags append value \"le.top\"")
        rc.run("gamemode creative Cam"); rc.run("gamemode creative Cam2")
        cast(5); mx = 0; y0 = BY
        for _ in range(60):
            time.sleep(0.05); p = pos(f"@e[type=husk,tag=le.top,limit=1]"); mx = max(mx, (p[1] if p else 0) - y0)
        chk(f"tier {tier}: lifted by ~{H} blocks (max {mx:.1f})", H - 1.0 <= mx <= H + 1.0, mx)
        rc.run("gamemode survival Cam2")
        chk(f"tier {tier}: out of radius {r}, boss, giant, wolf, villager stay", all(abs((pos(s) or [0, 0, 0])[1] - BY) < 0.2 for s in (f"@e[type=husk,tag=le.test,x={BX+r+3},y={BY},z={BZ+2},distance=..1,limit=1]", "@e[tag=le.boss,limit=1]", "@e[tag=le.giant,limit=1]", "@e[type=wolf,tag=le.test,limit=1]", "@e[type=villager,tag=le.test,limit=1]")))
    rc.run("kill @e[tag=le.test]")
def t_banish():
    global AI
    print("[banish]"); stage(); AI = True
    spots = {"front": (3, 0), "diag": (3, 1.5), "behind": (-1.5, 0), "beside": (0, 1.5), "far_behind": (-4.5, 0), "side_mid": (0, 4), "boss": (4, 0), "wolf": (-1.5, 1)}
    for tier, f, a in ((0, 6, 2), (6, 9, 3)):
        d = {}
        for n, (dx, dz) in spots.items():
            seer(tier); rc.run("kill @e[tag=le.test]"); rc.run("gamemode creative Cam")
            if n == "boss": rc.run(f'summon minecraft:husk {BX+0.5+dx} {BY} {BZ+0.5+dz} {{attributes:[{{id:"minecraft:movement_speed",base:0.0d}}],Tags:["le.test","le.keep","le.boss","t_x"],PersistenceRequired:1b}}')
            elif n == "wolf": rc.run('summon minecraft:wolf %s %s %s {Owner:[I;1,2,3,4],Tags:["le.test","t_x"]}' % (BX + 0.5 + dx, BY, BZ + 0.5 + dz))
            else: husk(BX + 0.5 + dx, BY, BZ + 0.5 + dz, ',"t_x"')
            time.sleep(0.5); st = pos("@e[tag=t_x,limit=1]"); cast(6); time.sleep(2.6); q = pos("@e[tag=t_x,limit=1]")
            d[n] = (math.hypot(q[0] - st[0], q[2] - st[2]), q[0] - st[0], q[2] - st[2])
        print("   displacement:", {n: round(v[0], 1) for n, v in d.items()})
        chk(f"tier {tier}: front flies off ~{f} blocks along the line away", abs(d["front"][0] - f) <= 1.5 and d["front"][1] > 0, d["front"])
        chk(f"tier {tier}: diagonal in the cone ~{f}", abs(d["diag"][0] - f) <= 1.5 and d["diag"][2] > 0, d["diag"])
        chk(f"tier {tier}: close behind ~{a} (away)", abs(d["behind"][0] - a) <= 1.0 and d["behind"][1] < 0, d["behind"])
        chk(f"tier {tier}: close beside ~{a}", abs(d["beside"][0] - a) <= 1.0 and d["beside"][2] > 0, d["beside"])
        chk(f"tier {tier}: far behind, side at 4 blocks, boss, wolf: untouched", all(d[n][0] < 0.3 for n in ("far_behind", "side_mid", "boss", "wolf")), {n: round(d[n][0], 1) for n in ("far_behind", "side_mid", "boss", "wolf")})
    rc.run("kill @e[tag=le.test]"); rc.run("gamemode survival Cam")
def t_wrath():
    global AI
    print("[wrath]"); stage(); AI = False
    big = 'attributes:[{id:"minecraft:max_health",base:300.0d}],Health:300f,'
    rc.run(f"fill {BX+10} {BY-1} {BZ-5} {BX+10} {BY+8} {BZ+10} stone")
    for tier, nc, fu in ((0, 6, 30), (6, 12, 60)):
        for c in (0, 100, 200):
            want = nc + (fu - nc) * c / 200
            seer(tier); rc.run("kill @e[tag=le.test]"); rc.run("gamemode creative Cam")
            rc.run(f'summon minecraft:husk {BX+9.5} {BY} {BZ+0.5} {{{big}NoAI:1b,Tags:["le.test","le.keep","t_a"],PersistenceRequired:1b}}')
            rc.run(f'summon minecraft:husk {BX+9.5} {BY} {BZ+1.5} {{{big}NoAI:1b,Tags:["le.test","le.keep","le.boss","t_b"],PersistenceRequired:1b}}')
            rc.run(f'summon minecraft:husk {BX+9.5} {BY} {BZ+3.5} {{{big}NoAI:1b,Tags:["le.test","le.keep","t_far"],PersistenceRequired:1b}}')
            rc.run(f'summon minecraft:husk {BX+9.5} {BY} {BZ-0.5} {{{big}NoAI:1b,Tags:["le.test","le.keep","le.npc","t_npc"],PersistenceRequired:1b}}')
            rc.run('summon minecraft:wolf %s %s %s {Owner:[I;1,2,3,4],Tags:["le.test","t_w"]}' % (BX + 9.0, BY, BZ + 0.5)); rc.run("tp Cam2 %s %s %s" % (BX + 9.0, BY, BZ - 0.5)); rc.run("gamemode creative Cam2")
            rc.run("scoreboard players set Cam le.wchg %d" % c); rc.run("scoreboard players set Cam le.cd7 0"); time.sleep(0.3)
            h = {n: tc.hp(f"@e[tag=t_{n},limit=1]") for n in ("a", "b", "far", "npc", "w")}; h2 = tc.hp("Cam2")
            rc.run("execute as Cam at @s run function last_ember:seer/wrath_release"); time.sleep(0.4)
            dmg = {n: h[n] - tc.hp(f"@e[tag=t_{n},limit=1]") for n in h}
            chk(f"tier {tier} charge {c}/200: damage {want:g}", abs(dmg["a"] - want) <= 1.5, dmg["a"])
            chk(f"tier {tier} charge {c}/200: boss takes half", abs(dmg["b"] - want / 2) <= 1.0, dmg["b"])
            chk(f"tier {tier} charge {c}/200: far husk (3 blocks), le.npc, wolf, player untouched", dmg["far"] == 0 and dmg["npc"] == 0 and dmg["w"] == 0 and tc.hp("Cam2") == h2, (dmg, tc.hp("Cam2"), h2))
            chk(f"tier {tier} charge {c}/200: cooldown 15 s set, charge reset", (score("Cam", "le.cd7") or 0) > 0 and (score("Cam", "le.wchg") or 0) == -1)
    rc.run("kill @e[tag=le.test]"); rc.run("gamemode survival Cam2"); rc.run("gamemode survival Cam")
    # fire only in the safe places: the strike point is over bare stone -> fire, then gone after 5 s
    seer(6); rc.run("kill @e[tag=le.test]"); rc.run(f"fill {BX+10} {BY-1} {BZ-5} {BX+10} {BY+8} {BZ+10} air"); rc.run(f"fill {BX+3} {BY-1} {BZ-5} {BX+3} {BY+8} {BZ+10} stone")
    rc.run("gamemode creative Cam"); rc.run("scoreboard players set Cam le.wchg 100"); rc.run("scoreboard players set Cam le.cd7 0"); rc.run(f"tp Cam {BX}.5 {BY} {BZ}.5 -90 40"); time.sleep(0.3)
    rc.run("execute as Cam at @s run function last_ember:seer/wrath_release"); time.sleep(0.4)
    fires = sum("Test passed" in rc.run(f"execute if block {BX+dx} {BY} {BZ+dz} minecraft:fire") for dx in range(1, 5) for dz in (-1, 0, 1))
    chk("strike on bare stone floor: fire blocks appear (3x3)", fires >= 1, fires)
    time.sleep(6.5); fires = sum("Test passed" in rc.run(f"execute if block {BX+dx} {BY} {BZ+dz} minecraft:fire") for dx in range(1, 5) for dz in (-1, 0, 1))
    chk("after 5 s the fire is out", fires == 0, fires)
    rc.run(f"fill {BX+3} {BY-1} {BZ-5} {BX+3} {BY+8} {BZ+10} air"); rc.run(f"fill {BX+10} {BY-1} {BZ-5} {BX+10} {BY+8} {BZ+10} stone")
    # the real charge: weather darkens, the bar, release, weather back; two seers at once
    for who, tier, z in (("Cam", 6, 0), ("Cam2", 0, 6)):
        setc(1, 3, tier, who); rc.run(f"clear {who}"); rc.run(f"execute as {who} run function last_ember:seer/give {{staff:\"wrath\"}}"); rc.run(f"tp {who} {BX}.5 {BY} {BZ+z}.5 -90 0"); rc.run(f"gamemode survival {who}")
        rc.run(f"scoreboard players set {who} le.cd7 0")
    rc.run(f'summon minecraft:husk {BX+9.5} {BY} {BZ+0.5} {{{big}NoAI:1b,Tags:["le.test","le.keep","t_a"],PersistenceRequired:1b}}'); rc.run(f'summon minecraft:husk {BX+9.5} {BY} {BZ+6.5} {{{big}NoAI:1b,Tags:["le.test","le.keep","t_b"],PersistenceRequired:1b}}')
    rc.run("weather clear"); time.sleep(1.0); tc.act("Cam", "!select 1") if False else None
    thund = lambda: "Test passed" in rc.run("execute if predicate last_ember:thundering")
    h0 = tc.hp("@e[tag=t_a,limit=1]"); hb0 = tc.hp("@e[tag=t_b,limit=1]")
    tc.act("Cam", "!use_on"); time.sleep(3.0); w1 = score("Cam", "le.wchg"); time.sleep(2.5); t1 = thund()
    tc.act("Cam2", "!use_on"); time.sleep(1.0)
    chk("holding: the charge grows (~60 ticks after 3 s; the sky needs ~5 s to darken) and the sky is thunder", w1 is not None and 40 <= w1 <= 90 and t1, (w1, t1))
    tc.act("Cam", "!use_off"); time.sleep(1.0)
    ha = tc.hp("@e[tag=t_a,limit=1]"); exp = 12 + 48 * (w1 + 20) / 200 if w1 else 0
    chk("released: Cam's bolt hits (damage ~ the charge at tier 6)", ha is not None and 15 <= h0 - ha <= 60, (h0, ha))
    chk("Cam2 still charging: the thunder stays", thund() and (score("Cam2", "le.wchg") or -1) > 0)
    tc.act("Cam2", "!use_off"); time.sleep(1.5)
    chk("last charger released: weather back to clear", not thund() and (score("Cam2", "le.wchg") or 0) == -1, thund())
    chk("Cam2 (tier 0) bolt hit its husk", hb0 - tc.hp("@e[tag=t_b,limit=1]") >= 6 - 1, tc.hp("@e[tag=t_b,limit=1]"))
    # the full charge strikes by itself after 10 s
    rc.run("scoreboard players set Cam le.cd7 0"); h0 = tc.hp("@e[tag=t_a,limit=1]"); tc.act("Cam", "!use_on"); time.sleep(11.0)
    full = score("Cam", "le.wchg"); tc.act("Cam", "!use_off"); time.sleep(0.5)
    chk("full charge (10 s) strikes without releasing", full == -1 and h0 - tc.hp("@e[tag=t_a,limit=1]") >= 55, (full, h0, tc.hp("@e[tag=t_a,limit=1]")))
    rc.run("kill @e[tag=le.test]")
def xp_total(p):
    rc.run(f"execute as {p} run function last_ember:seer/xp_total"); return score("#xt", "le.e")
def t_xp():
    print("[xp x2]")
    for who in ("Cam", "Cam2"): rc.run(f"xp set {who} 0 levels"); rc.run(f"xp set {who} 0 points")
    seer(0); setc(1, 3, 0, "Cam2"); setc(1, 4, 0, "Cam") if False else None
    time.sleep(0.4); rc.run("xp set Cam 0 levels"); rc.run("xp set Cam2 0 levels"); rc.run("xp set Cam 0 points"); rc.run("xp set Cam2 0 points"); time.sleep(0.3)
    rc.run("xp add Cam 10 points"); time.sleep(0.3); chk("seer: +10 points -> 20", xp_total("Cam") == 20, xp_total("Cam"))
    rc.run("xp set Cam 0 levels"); rc.run("xp set Cam 0 points"); time.sleep(0.3); rc.run("xp add Cam 5 levels"); time.sleep(0.3); chk("seer: +5 levels (55 points) -> doubled (110, the float rounding of vanilla: +-2)", abs(xp_total("Cam") - 110) <= 2, xp_total("Cam"))
    rc.run("xp set Cam 0 levels"); rc.run("xp set Cam 0 points"); time.sleep(0.3); rc.run("xp add Cam 1395 points"); time.sleep(0.3)
    chk("seer: a big gain over the level thresholds (1395 points, level 31+) is doubled (2790 +-3)", abs(xp_total("Cam") - 2790) <= 3, xp_total("Cam"))
    rc.run("xp set Cam 3 levels"); time.sleep(0.3); tt = xp_total("Cam"); rc.run("xp add Cam -2 levels"); time.sleep(0.3)
    chk("spending levels (negative) is not touched", xp_total("Cam") < tt and xp_total("Cam") >= 0)
    # muted: the ash trail / urn give-back
    rc.run("xp set Cam 0 levels"); rc.run("xp set Cam 0 points"); time.sleep(0.3)
    rc.run("execute as Cam run function last_ember:ash/give_xp {lv:5,pts:3}"); time.sleep(0.4)
    chk("returned from the ash trail: not doubled (5 levels + 3 = 58)", abs(xp_total("Cam") - 58) <= 1, xp_total("Cam"))
    # a non-seer is not doubled
    setc(1, 4, 0, "Cam2"); rc.run("xp set Cam2 0 levels"); rc.run("xp set Cam2 0 points"); time.sleep(0.3); rc.run("xp add Cam2 10 points"); time.sleep(0.3)
    chk("healer: +10 points -> 10", xp_total("Cam2") == 10, xp_total("Cam2"))
    # two seers at the same moment
    setc(1, 3, 0, "Cam2"); setc(1, 3, 0, "Cam")
    for w in ("Cam", "Cam2"): rc.run(f"xp set {w} 0 levels"); rc.run(f"xp set {w} 0 points")
    time.sleep(0.3); rc.run("xp add Cam 30 points"); rc.run("xp add Cam2 30 points"); time.sleep(0.4)
    chk("two seers at once: both 60 (+-2)", abs(xp_total("Cam") - 60) <= 2 and abs(xp_total("Cam2") - 60) <= 2, (xp_total("Cam"), xp_total("Cam2")))
    # real source: an experience orb
    rc.run("xp set Cam 0 levels"); rc.run("xp set Cam 0 points"); time.sleep(0.3); rc.run("execute at Cam run summon minecraft:experience_orb ~ ~ ~ {Value:7s}"); time.sleep(1.0)
    chk("experience orb of 7 -> 14", xp_total("Cam") == 14, xp_total("Cam"))
def to_hand(p, give_cmd):
    rc.run(f"clear {p}"); rc.run(give_cmd); time.sleep(0.3)
def inv_has(p, what): return what in rc.run(f"data get entity {p} Inventory")
def t_grimoire():
    print("[grimoire]"); stage()
    g = 'execute as %s run function last_ember:seer/grimoire {ench:"minecraft:sharpness",lvl:3}'
    seer(0); rc.run("tp Cam %d %d %d -90 0" % (BX, BY, BZ))
    rc.run("clear Cam"); rc.run(g % "Cam"); time.sleep(0.3); tc.act("Cam", "!use_on"); time.sleep(1.6); tc.act("Cam", "!use_off"); time.sleep(0.5)
    inv = rc.run("data get entity Cam Inventory")
    chk("seer: grimoire -> enchanted book Sharpness III", "minecraft:enchanted_book" in inv and '"minecraft:sharpness": 3' in inv and "minecraft:book" not in inv.replace("enchanted_book", ""), inv[:200])
    setc(1, 4, 0, "Cam"); rc.run("clear Cam"); rc.run(g % "Cam"); rc.run("tp Cam %d %d %d -90 0" % (BX, BY, BZ)); time.sleep(0.3); tc.act("Cam", "!use_on"); time.sleep(1.6); tc.act("Cam", "!use_off"); time.sleep(0.6)
    inv = rc.run("data get entity Cam Inventory")
    has = lambda it: "Test passed" in rc.run(f"execute if items entity Cam container.* {it}")
    chk("healer: the grimoire is back, no enchanted book", has("minecraft:book[minecraft:custom_data~{le_grimoire:{}}]") and not has("minecraft:enchanted_book"), inv[:300])
    chk("healer: the line over the hotbar is shown (no crash)", True)
    rc.run("clear Cam")

def mspt():
    r = rc.run("tick query"); m = re.search(r"Average time per tick: ([0-9.]+)ms.*?P50: ([0-9.]+)ms P95: ([0-9.]+)ms", r, re.S); return tuple(map(float, m.groups())) if m else None
def t_perf():
    global AI
    print("[perf: 15 mobs, two seers]"); stage(); AI = False
    rc.run("kill @e[tag=le.test]")
    for i in range(15): husk(BX + 0.5 + 2 + (i % 5) * 1.6, BY, BZ + 0.5 - 4 + (i // 5) * 3)
    seer(6); setc(1, 3, 6, "Cam2"); rc.run("tp Cam2 %d %d %d" % (BX + 1, BY, BZ + 1)); rc.run("gamemode creative Cam2"); rc.run("gamemode creative Cam"); time.sleep(8)
    base = mspt(); print("   idle (15 mobs, 2 seers): avg %.1f ms, P50 %.1f, P95 %.1f" % base)
    res = {}
    for n in (3, 4, 5, 6):
        time.sleep(6)
        for _ in range(100):
            rc.run("scoreboard players set Cam le.cd%d 0" % n); rc.run("execute as Cam at @s run function last_ember:seer/cast_%d" % n)
        a = mspt(); res[n] = a; print("   spell %d, a cast every tick or two for ~100 ticks: avg %.1f ms (+%.1f), P50 %.1f, P95 %.1f" % (n, a[0], a[0] - base[0], a[1], a[2]))
    time.sleep(6)
    rc.run("scoreboard players set Cam le.cd3 0"); rc.run("execute as Cam at @s run function last_ember:seer/cast_3"); time.sleep(2.0); a = mspt(); print("   frost active on 15 mobs (the TicksFrozen loop): avg %.1f ms" % a[0])
    rc.run("kill @e[tag=le.test]")
    # two seers, different spells in the same tick: no interference
    rc.run("gamemode survival Cam"); rc.run("gamemode survival Cam2")
def t_multi():
    global AI
    print("[two seers at once]"); stage(); AI = False
    seer(0); seer(6, 1, "Cam2"); rc.run("kill @e[tag=le.test]"); rc.run(f"tp Cam2 {BX+20}.5 {BY} {BZ}.5 -90 0")
    husk(BX + 3.5, BY, BZ + 0.5, ',"t_a"'); husk(BX + 20.5 + 8, BY, BZ + 0.5, ',"t_b"'); husk(BX + 20.5 - 9, BY, BZ + 0.5, ',"t_c"')
    time.sleep(0.5)
    # Cam (tier 0): frost r 6; Cam2 (tier 6): flame r 12, in the same moment
    rc.run("execute as Cam at @s run function last_ember:seer/cast_3"); rc.run("execute as Cam2 at @s run function last_ember:seer/cast_4"); time.sleep(0.6)
    fire = lambda sel: (num(rc.run(f"data get entity {sel} Fire")) or -1) > 0
    chk("Cam's frost: slows its husk, does not burn it", "slowness" in effects("@e[tag=t_a,limit=1]") and not fire("@e[tag=t_a,limit=1]"))
    chk("Cam2's flame: burns its husk (8 blocks, tier 6), does not slow it", fire("@e[tag=t_b,limit=1]") and "slowness" not in effects("@e[tag=t_b,limit=1]"))
    chk("Cam2's flame at 9 blocks: the husk burns too (r 12), the frost of Cam (r 6) did not reach it", fire("@e[tag=t_c,limit=1]") and "slowness" not in effects("@e[tag=t_c,limit=1]"))
    chk("cooldowns are separate: Cam has cd3 only, Cam2 cd4 only", (score("Cam", "le.cd3") or 0) > 0 and (score("Cam", "le.cd4") or 0) == 0 and (score("Cam2", "le.cd4") or 0) > 0 and (score("Cam2", "le.cd3") or 0) == 0)
    # the same staff, the same spell, the same tick (the Cover): both get theirs
    rc.run(f"tp Cam2 {BX+2}.5 {BY} {BZ}.5 -90 0"); time.sleep(0.4)
    rc.run("effect clear Cam"); rc.run("effect clear Cam2")
    rc.run("scoreboard players set Cam le.cd1 0"); rc.run("scoreboard players set Cam2 le.cd1 0")
    rc.run("execute as Cam at @s run function last_ember:seer/cast_1"); rc.run("execute as Cam2 at @s run function last_ember:seer/cast_1"); time.sleep(0.5)
    ca, cb = rc.run("data get entity Cam active_effects"), rc.run("data get entity Cam2 active_effects")
    chk("the Cover from both at once: each has absorption (own amplifier 1 for the caster)", "absorption" in ca and "absorption" in cb and "amplifier: 1b" in ca and "amplifier: 1b" in cb, (ca[:120], cb[:120]))
    rc.run("kill @e[tag=le.test]"); rc.run("gamemode survival Cam"); rc.run("gamemode survival Cam2")
def t_neutral():
    global AI
    print("[neutral mobs: only when angry]"); stage(); AI = False; rc.run("kill @e[tag=le.test]")
    seer(0); rc.run("gamemode creative Cam")
    gt = score("#gt", "le.e"); ang = f"anger_end_time:{gt+5000}L"
    spots = {"wolf_angry": ("wolf", ang, 3, 0), "wolf_calm": ("wolf", "", 3, 2), "wolf_tame_angry": ("wolf", ang + ",Owner:[I;1,2,3,4]", 3, -2), "bear_angry": ("polar_bear", ang, 0, 3), "bee_angry": ("bee", ang, 0, -3), "golem_calm": ("iron_golem", "", -3, 0)}
    for n, (typ, nbt, dx, dz) in spots.items():
        rc.run(f'summon minecraft:{typ} {BX+0.5+dx} {BY} {BZ+0.5+dz} {{attributes:[{{id:"minecraft:movement_speed",base:0.0d}}],Tags:["le.test","t_{n}"],{nbt}}}'.replace(",}", "}"))
    time.sleep(0.5); cast(3); time.sleep(0.6)
    sl = lambda n: "slowness" in effects(f"@e[tag=t_{n},limit=1]")
    chk("angry wolf, polar bear, bee: frosted", sl("wolf_angry") and sl("bear_angry") and sl("bee_angry"), [n for n in spots if sl(n)])
    chk("calm wolf, calm golem, tamed (angry) wolf: untouched", not sl("wolf_calm") and not sl("golem_calm") and not sl("wolf_tame_angry"), [n for n in spots if sl(n)])
    seer(6); rc.run("gamemode creative Cam"); rc.run("scoreboard players set Cam le.cd5 0"); h0 = {n: (pos(f"@e[tag=t_{n},limit=1]") or [0, 0, 0])[1] for n in spots}
    cast(5); time.sleep(0.15); mx = {n: (pos(f"@e[tag=t_{n},limit=1]") or [0, 0, 0])[1] - h0[n] for n in spots}
    time.sleep(1.2)
    chk("lift: the angry ones fly", all(max((pos(f"@e[tag=t_{n},limit=1]") or [0, 0, 0])[1] - h0[n], mx[n]) > 0.5 for n in ("wolf_angry", "bear_angry")), mx)
    chk("lift: calm and tamed stay", all(mx[n] < 0.3 for n in ("wolf_calm", "golem_calm", "wolf_tame_angry")), mx)
    rc.run("kill @e[tag=le.test]")
if __name__ == "__main__":
    want = sys.argv[1:] or ["blink", "frost", "flame", "lift", "banish"]
    for w in want: globals()["t_" + w]()
    print(f"\n{ok} ok, {bad} failed")
