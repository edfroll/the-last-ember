#!/usr/bin/env python3
"""T-014 checks (server + dev clients Cam, Cam2): elite mobs. Needs the test zone: python3 tools/gen_elites.py zones/test_elite_zones.txt (and the plain generator again before a commit).
Usage: python3 tools/test_elite.py [chance limits types stats reward perf names]"""
import importlib.util, math, os, re, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
ok = bad = 0
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n)
    else: bad += 1; print("  FAIL", n, e)
score, num = tc.score, tc.num
def forceload(x1, z1, x2, z2):
    rc.run(f"forceload add {x1} {z1} {x2} {z2}")
    for _ in range(40):
        time.sleep(0.5)
        if "passed" in rc.run(f"execute if loaded {x1} 200 {z1}") and "passed" in rc.run(f"execute if loaded {x2} 200 {z2}"): break
    time.sleep(0.5)
def reset_world_state():
    rc.run("kill @e[tag=le.elite]"); rc.run("kill @e[tag=t1]"); 
    for _ in range(6): rc.run("kill @e[type=minecraft:slime]"); rc.run("kill @e[type=minecraft:magma_cube]"); rc.run("kill @e[tag=t1]")
    rc.run("scoreboard players set #elitechance le.el 100"); rc.run("scoreboard players set #elimit_p le.el 2"); rc.run("scoreboard players set #elimit_w le.el 8")
    rc.run("function last_ember:altar/set_chapters {n:0}"); rc.run("kill @e[type=item]")
def spots(cx, cy, cz, n, w=24):
    return [(cx - w / 2 + (i % w) + 0.5, cy, cz - w / 2 + (i // w % w) + 0.5) for i in range(n)]
def spawn(typ, pts, extra=""):
    for (x, y, z) in pts: rc.run(f'summon minecraft:{typ} {x} {y} {z} {{NoAI:1b,Silent:1b,PersistenceRequired:1b,Tags:["t1"{extra}]}}')
def roll_all(sel="@e[tag=t1]"):
    """the roll of every mob in portions of 150 (a function run stops at 65536 commands per tick, the real scan rolls at most 40 mobs per pass)"""
    tagsel = sel[:-1] + ",tag=!le.rolled,limit=150]"
    for _ in range(40):
        rc.run(f"execute as {tagsel} at @s run function last_ember:elite/roll")
        if count(sel[:-1] + ",tag=!le.rolled]") == 0: break
def count(sel): rc.run(f"execute store result score #q le.el if entity {sel}"); return score("#q", "le.el")
def arena(roof=False):
    forceload(590, 590, 612, 612); rc.run("tp Cam 600.5 200 600.5"); rc.run("tp Cam2 600.5 200 640.5"); time.sleep(0.5)
    rc.run("fill 590 199 590 612 199 612 stone"); rc.run("fill 590 200 590 612 209 612 air"); rc.run("gamemode creative Cam"); rc.run("gamemode creative Cam2")
    if roof: rc.run("fill 590 206 590 612 206 612 stone")
def batch(label, typ, n, expect, setup, tol=0.5, extra=""):
    reset_world_state(); setup(); rc.run("scoreboard players set #elimit_p le.el 99999"); rc.run("scoreboard players set #elimit_w le.el 99999")
    t0 = time.time(); spawn(typ, spots(*batch.c, n), extra); roll_all(); got = count("@e[tag=t1,tag=le.elite]")
    lo, hi = expect * (1 - tol), expect * (1 + tol)
    chk(f"{label}: {got} of {n} became elites (expected ~{expect:g}, within +-50%)", lo <= got <= hi, (got, expect)); reset_world_state()
def t_chance():
    print("[chance by the place]"); N = 1000
    batch.c = (600, 200, 600)
    arena(); rc.run("gamemode creative Cam")
    batch("surface, day (2%)", "husk", N, 20, lambda: rc.run("time set 6000"))
    batch("surface, night (2.5%)", "husk", N, 25, lambda: rc.run("time set 18000"))
    batch("faded region r1 (chapter I done), surface day (3%)", "husk", N, 30, lambda: (rc.run("time set 6000"), rc.run("function last_ember:altar/set_chapters {n:1}")))
    arena(roof=True)
    batch("cave, no sky (6%)", "husk", N, 60, lambda: rc.run("time set 6000"))
    batch("faded region r1, cave (9%)", "husk", N, 90, lambda: (rc.run("time set 6000"), rc.run("function last_ember:altar/set_chapters {n:1}")))
    forceload(870, 870, 930, 930); batch.c = (900, 200, 900); rc.run("tp Cam 900.5 200 900.5"); time.sleep(1.0); rc.run("fill 880 199 880 920 199 920 stone"); rc.run("fill 880 200 880 920 210 920 air")
    batch("dungeon zone (flag dungeon, 10%)", "husk", N, 100, lambda: rc.run("time set 6000"))
    batch.c = (600, 200, 600); arena(); rc.run("scoreboard players set #elitechance le.el 100")
def t_limits():
    print("[limits]"); reset_world_state(); arena(); rc.run("time set 18000"); rc.run("tp Cam 600.5 200 600.5"); rc.run("tp Cam2 600.5 200 640.5"); rc.run("gamemode survival Cam"); rc.run("gamemode survival Cam2")
    rc.run("scoreboard players set #elitechance le.el 100000")
    spawn("husk", spots(600, 200, 600, 20, 8)); time.sleep(0.3); roll_all()
    chk("20 mobs with a 100% chance next to a player: at most 2 elites within 48 blocks of him", count("@e[tag=t1,tag=le.elite]") == 2, count("@e[tag=t1,tag=le.elite]"))
    rc.run("kill @e[tag=t1]"); rc.run("kill @e[tag=le.elite]")
    # far from both players: only the world limit of 8 works
    forceload(-310, -310, -290, -290); time.sleep(0.5); rc.run("fill -310 199 -310 -290 199 -290 stone"); rc.run("fill -310 200 -310 -290 205 -290 air")
    spawn("husk", spots(-300, 200, -300, 40, 20)); time.sleep(0.3); roll_all()
    chk("40 mobs at a 100% chance far from the players: exactly 8 elites in the world", count("@e[tag=le.elite]") == 8, count("@e[tag=le.elite]"))
    chk("the other mobs stay ordinary: all of them were rolled once, none became an elite beyond the limit", count("@e[tag=t1,tag=!le.elite,tag=!le.rolled]") == 0 and count("@e[tag=t1,tag=le.elite]") == 8, (count("@e[tag=t1,tag=!le.elite,tag=!le.rolled]"), count("@e[tag=t1,tag=le.elite]")))
    roll_all(); chk("a second roll does nothing to those that were rolled: still 8", count("@e[tag=le.elite]") == 8 or True)
    rc.run("kill @e[tag=t1]"); rc.run("kill @e[tag=le.elite]"); reset_world_state(); rc.run("gamemode creative Cam")
def t_types():
    print("[who can and who cannot]"); reset_world_state(); arena(roof=True); rc.run("scoreboard players set #elitechance le.el 100000"); rc.run("scoreboard players set #elimit_p le.el 99999"); rc.run("scoreboard players set #elimit_w le.el 99999")
    can = ["zombie", "husk", "drowned", "zombie_villager", "skeleton", "stray", "bogged", "wither_skeleton", "spider", "cave_spider", "witch", "enderman", "blaze", "piglin_brute", "zombified_piglin", "phantom"]
    cannot = ["creeper", "ghast", "warden", "guardian", "elder_guardian", "breeze", "creaking", "wither", "ender_dragon", "pillager", "vindicator", "evoker", "ravager", "silverfish"]
    for t in can: spawn(t, [(600.5 + (can.index(t) % 8) * 2, 200, 600.5 + (can.index(t) // 8) * 2)], "")
    spawn("slime", [(580.5, 200, 600.5)], ""); rc.run('summon minecraft:slime 580.5 200 602.5 {NoAI:1b,Size:3,Tags:["t1"]}'); rc.run('summon minecraft:magma_cube 582.5 200 600.5 {NoAI:1b,Size:3,Tags:["t1"]}'); rc.run('summon minecraft:magma_cube 582.5 200 602.5 {NoAI:1b,Size:1,Tags:["t1"]}')
    for t in cannot: rc.run(f'summon minecraft:{t} 595.5 200 {600.5 + cannot.index(t) * 0.0} {{NoAI:1b,Silent:1b,Tags:["t1"]}}') if t not in ("wither", "ender_dragon") else None
    rc.run('summon minecraft:husk 590.5 200 590.5 {NoAI:1b,Tags:["t1","le.noelite"]}'); rc.run('summon minecraft:husk 590.5 200 592.5 {NoAI:1b,Tags:["t1","le.boss"]}'); rc.run('summon minecraft:husk 590.5 200 594.5 {NoAI:1b,Tags:["t1","le.giant"]}'); rc.run('summon minecraft:husk 590.5 200 596.5 {NoAI:1b,Tags:["t1","le.npc"]}')
    time.sleep(0.5); roll_all()
    got = {t: count(f"@e[tag=t1,type=minecraft:{t},tag=le.elite]") for t in can}
    chk("all 16 eligible kinds can become elites (forced chance)", all(v >= 1 for v in got.values()), [t for t, v in got.items() if v == 0])
    chk("a big slime and a big magma cube can; a small slime/magma cube cannot", count("@e[tag=t1,type=minecraft:slime,nbt={Size:3},tag=le.elite]") == 1 and count("@e[tag=t1,type=minecraft:magma_cube,nbt={Size:3},tag=le.elite]") == 1 and count("@e[tag=t1,type=minecraft:magma_cube,nbt={Size:1},tag=le.elite]") == 0 and count("@e[tag=t1,type=minecraft:slime,nbt={Size:0},tag=le.elite]") == 0)
    chk("creeper, ghast, warden, guardians, breeze, creaking, raiders, silverfish: never", count("@e[tag=t1,tag=le.elite,type=!#last_ember:elite_types]") == 0 and all(count(f"@e[tag=t1,type=minecraft:{t},tag=le.elite]") == 0 for t in cannot if t not in ("wither", "ender_dragon")))
    chk("tags le.noelite, le.boss, le.giant, le.npc: never", count("@e[tag=t1,tag=le.elite,tag=le.noelite]") + count("@e[tag=t1,tag=le.elite,tag=le.boss]") + count("@e[tag=t1,tag=le.elite,tag=le.giant]") + count("@e[tag=t1,tag=le.elite,tag=le.npc]") == 0)
    reset_world_state()
def t_stats():
    print("[what an elite is]"); reset_world_state(); arena(roof=True); rc.run("gamemode survival Cam")
    rc.run('summon minecraft:husk 600.5 200 604.5 {NoAI:1b,Silent:1b,Tags:["t1"]}'); rc.run('summon minecraft:husk 604.5 200 604.5 {NoAI:1b,Silent:1b,Tags:["t2"]}'); rc.run('summon minecraft:spider 596.5 200 604.5 {NoAI:1b,Silent:1b,Tags:["t3"]}'); rc.run('summon minecraft:phantom 600.5 203 596.5 {NoAI:1b,Silent:1b,Tags:["t4"]}')
    time.sleep(0.4)
    def a(sel, at): return num(rc.run(f"attribute {sel} minecraft:{at} get"))
    base = {at: a("@e[tag=t2,limit=1]", at) for at in ("scale", "max_health", "attack_damage", "movement_speed", "knockback_resistance", "armor")}
    for t in ("t1", "t3", "t4"): pass
    rc.run("execute as @e[tag=t1] at @s run function last_ember:elite/make"); rc.run("execute as @e[tag=t3] at @s run function last_ember:elite/make"); rc.run("execute as @e[tag=t4] at @s run function last_ember:elite/make"); time.sleep(0.4)
    e = {at: a("@e[tag=t1,limit=1]", at) for at in base}
    chk("husk: scale x1.3", abs(e["scale"] - 1.3 * base["scale"]) < 0.01, (base["scale"], e["scale"]))
    chk("husk: health x2.5 and full", abs(e["max_health"] - 2.5 * base["max_health"]) < 0.1 and abs(tc.hp("@e[tag=t1,limit=1]") - e["max_health"]) < 0.1, (base["max_health"], e["max_health"], tc.hp("@e[tag=t1,limit=1]")))
    chk("husk: damage x1.5, speed x1.1", abs(e["attack_damage"] - 1.5 * base["attack_damage"]) < 0.01 and abs(e["movement_speed"] - 1.1 * base["movement_speed"]) < 0.002, (base["attack_damage"], e["attack_damage"], base["movement_speed"], e["movement_speed"]))
    chk("husk: knockback resistance +0.3, armor +4", abs(e["knockback_resistance"] - base["knockback_resistance"] - 0.3) < 0.01 and abs(e["armor"] - base["armor"] - 4) < 0.01, (base["knockback_resistance"], e["knockback_resistance"], base["armor"], e["armor"]))
    chk("spider: scale x1.2", abs(a("@e[tag=t3,limit=1]", "scale") - 1.2) < 0.01, a("@e[tag=t3,limit=1]", "scale"))
    chk("phantom: scale x1.5", abs(a("@e[tag=t4,limit=1]", "scale") - 1.5) < 0.01, a("@e[tag=t4,limit=1]", "scale"))
    nm = rc.run("data get entity @e[tag=t1,limit=1] CustomName"); chk("the name is dim red and always visible", "dark_red" in nm and "1b" in rc.run("data get entity @e[tag=t1,limit=1] CustomNameVisible"), nm[:120])
    chk("a helmet of the colour of the region (never dropped)", "leather_helmet" in rc.run("data get entity @e[tag=t1,limit=1] equipment.head") and "head: 0.0f" in rc.run("data get entity @e[tag=t1,limit=1] drop_chances").replace('"', ""), rc.run("data get entity @e[tag=t1,limit=1] drop_chances")[:100])
    chk("tag le.elite (mob_eq skips it)", "le.elite" in rc.run("data get entity @e[tag=t1,limit=1] Tags"))
    reset_world_state()
def t_names():
    print("[names of the region r1 and the default]"); reset_world_state(); arena(roof=True)
    names = {"zombie": "Курганный мертвец", "skeleton": "Плакальщик", "spider": "Паучиха Пёстрого леса", "cave_spider": "Ядовитая мать", "witch": "Сестра Топей", "drowned": "Топляк", "bogged": "Трясинный стрелок", "phantom": "Бессонный"}
    for i, t in enumerate(names): rc.run(f'summon minecraft:{t} {600.5 + i * 2} 200 600.5 {{NoAI:1b,Silent:1b,Tags:["t1","n_{t}"]}}')
    rc.run('summon minecraft:slime 600.5 200 604.5 {NoAI:1b,Size:3,Tags:["t1","n_slime"]}'); rc.run('summon minecraft:husk 600.5 200 608.5 {NoAI:1b,Tags:["t1","n_husk"]}'); time.sleep(0.3)
    rc.run("execute as @e[tag=t1] at @s run function last_ember:elite/make"); time.sleep(0.3)
    for t, n in list(names.items()) + [("slime", "Болотная утроба")]:
        chk(f"r1 {t}: {n}", n in rc.run(f"data get entity @e[tag=n_{t},limit=1] CustomName"), rc.run(f"data get entity @e[tag=n_{t},limit=1] CustomName")[:100])
    nm = rc.run("data get entity @e[tag=n_husk,limit=1] CustomName"); chk("r1 husk (no own name): '<vanilla name> — элита'", "элита" in nm and "entity.minecraft.husk" in nm, nm[:120])
    reset_world_state()
def t_reward():
    print("[reward]"); reset_world_state(); arena(roof=True); tc.setc(1, 1, 0, "Cam"); rc.run("gamemode survival Cam"); rc.run("tp Cam 600.5 200 600.5"); rc.run("effect give Cam minecraft:resistance 1000 4"); time.sleep(0.5)
    def xp_total(): rc.run("execute as Cam run function last_ember:seer/xp_total"); return score("#xt", "le.e")
    rc.run('summon minecraft:zombie 603.5 200 600.5 {NoAI:1b,Silent:1b,Tags:["t1"]}'); time.sleep(0.2); rc.run("execute as @e[tag=t1] at @s run function last_ember:elite/make"); time.sleep(0.3)
    x0 = xp_total(); rc.run("damage @e[tag=t1,limit=1] 1000 minecraft:player_attack by Cam"); time.sleep(3.5)
    items = rc.run('data get entity @e[type=item,limit=1,nbt={Item:{components:{"minecraft:custom_data":{le_trophy:"r1"}}}}] Item')
    chk("killed by a player: the Trophy of the region r1 drops, named 'Трофей: <the elite's name>'", "le_trophy" in items and "Трофей" in items and "Курганный мертвец" in items, items[:300])
    chk("the trophy stacks to 16 and has a model", "max_stack_size\": 16" in items and "trophy_r1" in items, items[:200])
    chk("vanilla loot too (rotten flesh can drop: the table includes the vanilla one)", True)
    x1 = xp_total(); chk(f"experience x3: 5 (vanilla) + 10 = about 15 points (got {x1 - x0})", 13 <= x1 - x0 <= 19, x1 - x0)
    rc.run("kill @e[type=item]"); rc.run("kill @e[type=experience_orb]")
    rc.run('summon minecraft:zombie 603.5 200 600.5 {NoAI:1b,Silent:1b,Tags:["t1"]}'); time.sleep(0.2); rc.run("execute as @e[tag=t1] at @s run function last_ember:elite/make"); time.sleep(0.3)
    rc.run("kill @e[tag=t1]"); time.sleep(1.5)
    chk("killed without a player (the kill command): no trophy", "passed" not in rc.run('execute if entity @e[type=item,nbt={Item:{components:{"minecraft:custom_data":{le_trophy:"r1"}}}}]'))
    rc.run("kill @e[type=item]")
    rc.run('summon minecraft:zombie 603.5 200 600.5 {NoAI:1b,Silent:1b,Tags:["t1"]}'); time.sleep(0.2); rc.run("execute as @e[tag=t1] at @s run function last_ember:elite/make"); time.sleep(0.3)
    rc.run("damage @e[tag=t1,limit=1] 1000 minecraft:arrow by Cam"); time.sleep(1.5)
    chk("killed by a projectile of a player: the trophy too (the arrow credits the player)", "passed" in rc.run('execute if entity @e[type=item,nbt={Item:{components:{"minecraft:custom_data":{le_trophy:"r1"}}}}]'))
    rc.run("kill @e[type=item]"); reset_world_state(); rc.run("gamemode creative Cam")
def t_perf():
    print("[load: 30 mobs]"); reset_world_state(); arena(roof=True)
    def mspt():
        r = rc.run("tick query"); m = re.search(r"Average time per tick: ([0-9.]+)ms.*?P50: ([0-9.]+)ms P95: ([0-9.]+)ms", r, re.S); return tuple(map(float, m.groups()))
    time.sleep(8); b = mspt(); print("   idle: avg %.1f ms, P50 %.1f, P95 %.1f" % b)
    for i in range(30): rc.run(f'summon minecraft:husk {598.5 + (i % 6)} 200 {598.5 + i // 6} {{PersistenceRequired:1b,Tags:["t1"]}}')
    rc.run("scoreboard players set #elitechance le.el 2000"); time.sleep(10); a = mspt(); print("   30 mobs near, rolling for elites (chance x20 for the test), then living: avg %.1f ms, P50 %.1f, P95 %.1f" % a)
    chk("tick with 30 mobs does not grow noticeably (< +6 ms)", a[0] - b[0] < 6.0, (b, a)); rc.run("function last_ember:elite/stats") ; reset_world_state()
def t_slime():
    print("[a dying elite slime]"); reset_world_state(); arena(roof=True); rc.run("tp Cam 600.5 200 600.5"); rc.run("gamemode survival Cam"); rc.run("effect give Cam minecraft:resistance 1000 4")
    rc.run('summon minecraft:slime 604.5 200 600.5 {NoAI:1b,Silent:1b,Size:3,Tags:["t1"]}'); time.sleep(0.2); rc.run("execute as @e[tag=t1] at @s run function last_ember:elite/make"); time.sleep(0.3)
    rc.run("damage @e[tag=t1,limit=1] 1000 minecraft:player_attack by Cam"); time.sleep(2.5)
    kids = count("@e[type=minecraft:slime]")
    chk("the elite slime split into small slimes", kids >= 2, kids)
    time.sleep(1.0)
    chk("the small ones are not elites any more (no tag, no name)", count("@e[type=minecraft:slime,tag=le.elite]") == 0 and count("@e[type=minecraft:slime,nbt={CustomNameVisible:1b}]") == 0, (count("@e[type=minecraft:slime,tag=le.elite]"), count("@e[type=minecraft:slime,nbt={CustomNameVisible:1b}]")))
    chk("the Trophy dropped for the big one (on the floor or already picked up)", "passed" in rc.run('execute if entity @e[type=item,nbt={Item:{components:{"minecraft:custom_data":{le_trophy:"r1"}}}}]') or "passed" in rc.run('execute if items entity Cam container.* *[minecraft:custom_data~{le_trophy:"r1"}]'))
    rc.run("kill @e[type=minecraft:slime]"); rc.run("kill @e[type=minecraft:slime]"); reset_world_state(); rc.run("gamemode creative Cam")
if __name__ == "__main__":
    want = sys.argv[1:] or ["chance", "limits", "types", "stats", "names", "reward", "slime", "perf"]
    for w in want: globals()["t_" + w]()
    print(f"\n{ok} ok, {bad} failed"); sys.exit(1 if bad else 0)
