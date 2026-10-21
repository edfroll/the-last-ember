#!/usr/bin/env python3
"""T-010 checks (server + dev clients Cam, Cam2 in the game): knight, ranger, healer on tiers 0 and 6.
Usage: python3 tools/test_class.py [knight ranger healer1 healer2 healer3 ...]"""
import importlib.util, json, math, os, re, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon")
DIR = {"Cam": "server/client", "Cam2": "server/client2"}
ok = bad = 0
def check(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n)
    else: bad += 1; print("  FAIL", n, e)
def act(p, a):
    d = os.path.join(ROOT, DIR[p]); df = os.path.join(d, "shot-done.txt")
    if os.path.exists(df): os.remove(df)
    open(os.path.join(d, "shot-request.txt"), "w").write(a + "\n")
    for _ in range(80):
        time.sleep(0.05)
        if os.path.exists(df): return
def reset(p):
    rc.run(f"execute as {p} run function last_ember:char/reset"); time.sleep(1.6); rc.run(f"gamemode survival {p}")
def setc(race, cls, tier, p="Cam"):
    rc.run(f"clear {p}"); reset(p); rc.run(f"execute as {p} run function last_ember:char/set {{race:{race},class:{cls},tier:{tier}}}"); time.sleep(0.6)
def num(r, pat=r"([-0-9.]+)[fdsb]?$"):
    m = re.search(pat, r.strip()); return float(m.group(1)) if m else None
def hp(sel): return num(rc.run(f"data get entity {sel} Health"))
def score(p, o): m = re.search(r"has (-?\d+)", rc.run(f"scoreboard players get {p} {o}")); return int(m.group(1)) if m else None
def tp(p, x, y, z, yaw=0, pitch=0): rc.run(f"tp {p} {x} {y} {z} {yaw} {pitch}")
def t_knight():
    print("[knight]"); rc.run("difficulty normal")
    for tier in (0, 6):
        setc(1, 1, tier)
        sp = num(rc.run("attribute Cam minecraft:attack_speed get")); want = 4.0 * (1 + 0.2 + 0.2 * tier / 6)
        check(f"tier {tier}: attack speed {want:.2f}", abs(sp - want) < 0.01, sp)
        fx = rc.run("data get entity Cam active_effects"); amp = re.search(r"amplifier: (\d+)b?.*?resistance|resistance.*?amplifier: (\d+)", fx)
        check(f"tier {tier}: resistance {'II' if tier >= 4 else 'I'}", ("amplifier: 1b" in fx) == (tier >= 4) and "resistance" in fx, fx)
    # shield reflection (the client holds the shield up: the real blocking state)
    setc(1, 1, 0); tp("Cam", 0.5, 103, -14.5, 0, 0); rc.run("kill @e[tag=le.test]"); time.sleep(0.5)
    rc.run("summon minecraft:husk 0.5 103 -12.5 {NoAI:1b,Tags:[\"le.test\",\"le.keep\"],PersistenceRequired:1b}"); time.sleep(0.5)
    act("Cam", "!use_on"); time.sleep(0.8)
    for dealt, want in ((6, 1), (12, 3), (30, 7), (50, 8)):   # difficulty normal: the reflection is floor(25%) of the damage, 1..8
        h0 = hp("@e[tag=le.test,limit=1]")
        rc.run(f"damage Cam {dealt} minecraft:mob_attack by @e[tag=le.test,limit=1]"); time.sleep(0.9)
        h1 = hp("@e[tag=le.test,limit=1]"); check(f"blocked hit {dealt}: attacker takes {want}", h0 - h1 == want, (h0, h1))
        rc.run("data modify entity @e[tag=le.test,limit=1] Health set value 20.0f"); time.sleep(0.4)
    act("Cam", "!use_off"); time.sleep(0.8); h0 = hp("@e[tag=le.test,limit=1]"); rc.run("damage Cam 6 minecraft:mob_attack by @e[tag=le.test,limit=1]"); time.sleep(0.9)
    check("not blocking: no reflection", hp("@e[tag=le.test,limit=1]") == h0)
    # a seer with a shield does not reflect
    setc(1, 3, 0); tp("Cam", 0.5, 103, -14.5, 0, 0); rc.run("item replace entity Cam weapon.offhand with minecraft:shield"); time.sleep(0.5)
    act("Cam", "!use_on"); time.sleep(0.8); h0 = hp("@e[tag=le.test,limit=1]"); rc.run("damage Cam 6 minecraft:mob_attack by @e[tag=le.test,limit=1]"); time.sleep(0.9)
    check("a seer's shield does not reflect", hp("@e[tag=le.test,limit=1]") == h0); act("Cam", "!use_off"); rc.run("kill @e[tag=le.test]")
def t_bless():
    print("[blessing]")
    for who in ("Cam", "Cam2"): rc.run(f"scoreboard players set {who} le.blday -1"); rc.run(f"tag {who} remove le.sated"); rc.run(f"scoreboard players set {who} le.bless 0")
    setc(1, 1, 0); setc(2, 2, 0, "Cam2")
    rc.run("tp Cam 0.5 103 5.5"); rc.run("tp Cam2 3.5 103 5.5"); rc.run("item replace entity Cam armor.chest with minecraft:chainmail_chestplate[minecraft:damage=100]")
    rc.run("item replace entity Cam weapon.mainhand with minecraft:stone_sword[minecraft:damage=50]")
    rc.run("item replace entity Cam armor.head with minecraft:iron_helmet[minecraft:damage=40,minecraft:custom_data={le_cursed:1b}]")
    rc.run("tick rate 100"); t0 = time.time(); got = False
    while time.time() - t0 < 25:
        time.sleep(0.5)
        if "le.sated" in rc.run("tag Cam2 list") and (score("Cam", "le.blday") or -1) >= 0: got = True; break
        if time.time() - t0 > 6 and abs(score("Cam", "le.bless") - 30) < 3: pass
    rc.run("tick rate 20")
    check("after 60 s at the bonfire: the partner (r 8) is sated", got)
    ch = rc.run("data get entity Cam equipment.chest.components"); sw = rc.run("data get entity Cam SelectedItem.components"); hd = rc.run("data get entity Cam equipment.head.components")
    d1 = num(re.search(r"minecraft:damage\": (\d+)", ch).group(0), r"(\d+)$") if re.search(r"minecraft:damage\": (\d+)", ch) else None
    check("chainmail repaired by 30% of max (100 -> 28)", d1 is not None and abs(d1 - 28) <= 1, ch)
    check("sword repaired by 30% of max (131*... 50 -> 10)", "minecraft:damage\": 10" in sw or "minecraft:damage\": 11" in sw or "minecraft:damage\": 9" in sw, sw)
    check("cursed item not repaired", "minecraft:damage\": 40" in hd, hd)
    check("once per game day: counter holds", score("Cam", "le.blday") >= 0)
    rc.run("tick rate 100"); time.sleep(14); rc.run("tick rate 20")
    ch2 = rc.run("data get entity Cam equipment.chest.components"); m2 = re.search(r"minecraft:damage\": (\d+)", ch2)
    check("second blessing the same day does not happen (the chainmail is not repaired again)", m2 is not None and int(m2.group(1)) >= 20, ch2)
    # damage resets the count
    rc.run("scoreboard players set Cam le.blday -1"); rc.run("tick rate 100"); time.sleep(5); b0 = score("Cam", "le.bless"); rc.run("damage Cam 1 minecraft:generic"); time.sleep(1.2); b1 = score("Cam", "le.bless"); rc.run("tick rate 20")
    check("damage resets the blessing count (>0 -> 0)", b0 and b0 > 0 and b1 == 0, (b0, b1))

def face(p, x, y, z, tx, ty, tz):
    dx, dy, dz = tx - x, ty - (y + 1.62), tz - z; yaw = math.degrees(math.atan2(-dx, dz)); pitch = -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    rc.run(f"tp {p} {x} {y} {z} {yaw:.1f} {pitch:.1f}")
def shoot(U, theta, v=3.0, owner=True):
    rc.run("kill @e[type=minecraft:arrow]"); vx, vy = v * math.cos(math.radians(theta)), v * math.sin(math.radians(theta))
    own = f"Owner:[I;{U}]," if owner else ""
    rc.run(f"summon minecraft:arrow 300.5 251.0 301.5 {{{own}Motion:[{vx}d,{vy}d,0.0d],pickup:0b}}"); t0 = time.time()
    while time.time() - t0 < 25:
        time.sleep(0.25)
        if rc.run("data get entity @e[type=minecraft:arrow,limit=1] inGround").strip().endswith("1b"): break
    pos = rc.run("data get entity @e[type=minecraft:arrow,limit=1] Pos"); dmg = rc.run("data get entity @e[type=minecraft:arrow,limit=1] damage")
    rc.run("kill @e[type=minecraft:arrow]"); return float(re.findall(r"\[([-0-9.]+)d", pos)[0]) - 300.5, float(re.findall(r": ([-0-9.]+)d", dmg)[0])
def t_ranger():
    print("[ranger]")
    rc.run("forceload add 300 300 700 302"); time.sleep(4); rc.run("fill 300 250 300 700 250 302 minecraft:stone")
    res = {}
    for race, tier in ((1, 0), (1, 6), (2, 6)):
        setc(race, 2, tier); U = rc.run("data get entity Cam UUID").split("[I;")[1].strip().rstrip("]"); res[(race, tier)] = shoot(U, 25)
    setc(1, 1, 0); U = rc.run("data get entity Cam UUID").split("[I;")[1].strip().rstrip("]"); base = shoot(U, 25)
    d0 = res[(1, 0)][1] * 1.5; d6 = res[(1, 6)][1] * 1.5; de = res[(2, 6)][1] * 1.5
    check("ranger tier 0: range x2, damage x1", 1.8 <= res[(1, 0)][0] / base[0] <= 2.2 and abs(d0 - base[1]) < 0.01, (res[(1, 0)], base))
    check("ranger tier 6: range x2, damage x2", 1.8 <= res[(1, 6)][0] / base[0] <= 2.2 and abs(d6 - 2 * base[1]) < 0.01, (res[(1, 6)], base))
    check("elf ranger tier 6: damage x2.5", abs(de - 2.5 * base[1]) < 0.01, res[(2, 6)])
    print("   range base %.1f ranger %.1f; damage base %.2f ranger tier0 %.2f tier6 %.2f elf tier6 %.2f (x speed 1.5 back)" % (base[0], res[(1, 0)][0], base[1], d0, d6, de))
def t_horn():
    print("[horn]")
    for tier, near, far in ((0, 20, 30), (6, 28, 36)):
        if tier == 6: time.sleep(31)          # the cooldown group of the horn belongs to the player, not to the stack
        setc(1, 2, tier); tp("Cam", 0.5, 103, -14.5, 0, 0)
        rc.run("kill @e[tag=le.test]"); time.sleep(0.4)
        for nm, d in (("near", near), ("far", far)):
            rc.run(f"summon minecraft:husk 0.5 103 {-14.5 + d} {{NoAI:1b,Tags:[\"le.test\",\"le.keep\",\"le.{nm}\"],PersistenceRequired:1b}}")
        time.sleep(1.0); rc.run("item replace entity Cam weapon.mainhand from entity Cam hotbar.2" if False else "item replace entity Cam weapon.mainhand from entity Cam container.0")
        inv = rc.run("data get entity Cam Inventory"); m = re.search(r"Slot: (\d+)b, id: \"minecraft:stick\"", inv)
        if m: rc.run(f"item replace entity Cam weapon.mainhand from entity Cam container.{m.group(1)}" if int(m.group(1)) > 8 else f"item replace entity Cam weapon.mainhand from entity Cam hotbar.{m.group(1)}")
        act("Cam", "!use_on"); time.sleep(1.0); act("Cam", "!use_off"); time.sleep(0.8)
        fn = "glowing" in rc.run("data get entity @e[tag=le.near,limit=1] active_effects"); ff = "glowing" in rc.run("data get entity @e[tag=le.far,limit=1] active_effects")
        check(f"tier {tier}: horn lights the husk at {near} ({fn}) and not at {far} ({ff})", fn and not ff)
        rc.run("effect clear @e[tag=le.near] minecraft:glowing"); act("Cam", "!use_on"); time.sleep(1.0); act("Cam", "!use_off"); time.sleep(0.8)
        check(f"tier {tier}: the cooldown holds (no second blast within 30 s)", "glowing" not in rc.run("data get entity @e[tag=le.near,limit=1] active_effects"))
    # not a ranger: silent
    setc(1, 1, 0, "Cam2"); tp("Cam2", 0.5, 103, -14.5, 0, 0); rc.run("kill @e[tag=le.test]"); time.sleep(0.4)
    rc.run("summon minecraft:husk 0.5 103 -4.5 {NoAI:1b,Tags:[\"le.test\",\"le.keep\",\"le.near\"],PersistenceRequired:1b}")
    rc.run("execute as Cam2 run function last_ember:char/gen/horn_item"); inv = rc.run("data get entity Cam2 Inventory"); m = re.search(r"Slot: (\d+)b, id: \"minecraft:stick\"", inv)
    if m: rc.run(f"item replace entity Cam2 weapon.mainhand from entity Cam2 hotbar.{m.group(1)}")
    act("Cam2", "!use_on"); time.sleep(1.0); act("Cam2", "!use_off"); time.sleep(0.8)
    check("a horn in other hands: nothing lights up", "glowing" not in rc.run("data get entity @e[tag=le.near,limit=1] active_effects"))
    rc.run("kill @e[tag=le.test]")
def t_tame():
    print("[taming]")
    setc(1, 2, 0); tp("Cam", 0.5, 103, -14.5, 0, 0); rc.run("kill @e[tag=le.test]"); time.sleep(0.4); tamed = 0
    for i in range(5):
        rc.run(f"summon minecraft:wolf 0.5 103 {-12.5} {{NoAI:1b,Tags:[\"le.test\",\"le.keep\"]}}"); time.sleep(0.4)
        rc.run("clear Cam minecraft:bone"); rc.run("give Cam minecraft:bone 1"); rc.run("item replace entity Cam weapon.mainhand from entity Cam hotbar.0" if False else "item replace entity Cam weapon.mainhand with minecraft:bone")
        face("Cam", 0.5, 103, -14.5, 0.5, 103.5, -12.5); time.sleep(0.5); act("Cam", "!use"); time.sleep(1.2)
        if "[I;" in rc.run("data get entity @e[type=minecraft:wolf,tag=le.test,limit=1] Owner"): tamed += 1
        rc.run("kill @e[tag=le.test]"); time.sleep(0.3)
    check("ranger: 5 of 5 wolves tamed with the first bone", tamed == 5, tamed)
    rc.run("summon minecraft:horse 0.5 103 -12.5 {NoAI:1b,Tags:[\"le.test\",\"le.keep\"]}"); time.sleep(0.4); rc.run("item replace entity Cam weapon.mainhand with minecraft:air")
    face("Cam", 0.5, 103, -14.5, 0.5, 104, -12.5); time.sleep(0.5); act("Cam", "!use"); time.sleep(1.2)
    check("ranger: a horse is tamed by the mount attempt", "1b" in rc.run("data get entity @e[type=minecraft:horse,tag=le.test,limit=1] Tame"))
    rc.run("kill @e[tag=le.test]")

# ------------------------------------------------------------------ healer
CAU = (-10, 103, -20); CIN = (-9.5, 103, -19.5)
def uuid(p): return rc.run(f"data get entity {p} UUID").split("[I;")[1].strip().rstrip("]")
def cauldron_setup(water=3):
    tp("Cam", -9.5, 103, -22.0, 0, 0); time.sleep(2.0)
    rc.run("kill @e[type=minecraft:interaction,tag=le.testpot]"); rc.run("kill @e[type=minecraft:item,x=-9.5,y=104,z=-19.5,distance=..6]")
    rc.run(f"setblock {CAU[0]} {CAU[1]} {CAU[2]} " + ("minecraft:cauldron" if water == 0 else f"minecraft:water_cauldron[level={water}]"))
    rc.run(f'summon minecraft:interaction {CIN[0]} {CIN[1]} {CIN[2]} {{width:1.05f,height:1.0f,Tags:["le.bonfire","le.pot","le.testpot"]}}'); time.sleep(0.3)
    rc.run("scoreboard players set @e[tag=le.testpot] le.bidx 99")
def throw(item, who="Cam", count=1, extra=""):
    U = uuid(who); rc.run(f"summon minecraft:item {CIN[0]} 104 {CIN[2]} {{Item:{{id:\"minecraft:{item}\",count:{count}{extra}}},Thrower:[I;{U}],Owner:[I;{U}],Motion:[0.0d,0.0d,0.0d]}}"); time.sleep(0.5)
def throw_item_nbt(nbt, who="Cam"):
    U = uuid(who); rc.run(f"summon minecraft:item {CIN[0]} 104 {CIN[2]} {{Item:{nbt},Thrower:[I;{U}],Owner:[I;{U}],Motion:[0.0d,0.0d,0.0d]}}"); time.sleep(0.5)
def cscore(o):
    m = re.search(r"has (-?\d+)", rc.run(f"scoreboard players get @e[tag=le.testpot,limit=1] {o}")); return int(m.group(1)) if m else None
def wait_idle(rate=150, timeout=60):
    rc.run(f"tick rate {rate}"); t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(0.4)
        if cscore("le.cstate") == 0 and cscore("le.cmask") == 0 and time.time() - t0 > 1.5: break
    rc.run("tick rate 20"); time.sleep(0.4)
def drain():
    out = []
    while True:
        r = rc.run(f"data get entity @e[type=minecraft:item,x={CIN[0]},y=104,z={CIN[2]},distance=..4,limit=1,sort=nearest] Item")
        if "has the following entity data" not in r: break
        out.append(r); rc.run(f"kill @e[type=minecraft:item,x={CIN[0]},y=104,z={CIN[2]},distance=..4,limit=1,sort=nearest]"); time.sleep(0.1)
    return out
def healer_setup(tier=0):
    setc(1, 4, tier); tp("Cam", -9.5, 103, -22.0, 0, 0); time.sleep(1.0)
def brew(items, tier=0, water=3):
    healer_setup(tier); cauldron_setup(water)
    for it in items: throw(it)
    wait_idle(); return drain()
def t_boost():
    print("[potion boost]")
    setc(1, 4, 0); rc.run("clear Cam minecraft:potion"); rc.run("clear Cam minecraft:splash_potion")
    rc.run('give Cam minecraft:potion[minecraft:potion_contents={potion:"minecraft:strength"}]'); rc.run('give Cam minecraft:potion[minecraft:potion_contents={potion:"minecraft:healing"}]')
    rc.run('give Cam minecraft:splash_potion[minecraft:potion_contents={potion:"minecraft:poison"}]'); rc.run('give Cam minecraft:lingering_potion[minecraft:potion_contents={potion:"minecraft:regeneration"}]')
    rc.run('give Cam minecraft:tipped_arrow[minecraft:potion_contents={potion:"minecraft:poison"}] 4'); time.sleep(2.5)
    inv = rc.run("data get entity Cam Inventory")
    check("drinkable strength: duration x1.5 = 5400", "duration: 5400" in inv, inv[:0])
    check("splash poison: duration 1350", "duration: 1350" in inv); check("lingering regeneration: duration 1350", inv.count("duration: 1350") >= 2)
    check("potions are marked le_boost and have the line", inv.count("le_boost: 1b") >= 4 and "Усилено знахарем" in inv)
    check("tipped arrows are not touched (4 boosted vials only)", "tipped_arrow" in inv and inv.count("le_boost: 1b") == 4, inv.count("le_boost: 1b"))
    # the boost happens once: pass to a non-healer and back
    n1 = inv.count("duration: 5400")
    rc.run("execute as Cam run function last_ember:char/gen/kit_all"); time.sleep(2.2); inv2 = rc.run("data get entity Cam Inventory")
    check("the boost does not stack over time", inv2.count("duration: 5400") == n1 and "duration: 8100" not in inv2)
    # upgrade chance 25%: 40 potions
    rc.run("clear Cam"); ups = 0
    for i in range(40): rc.run('give Cam minecraft:potion[minecraft:potion_contents={potion:"minecraft:swiftness"}]' if i < 36 else 'give Cam minecraft:potion[minecraft:potion_contents={potion:"minecraft:swiftness"}]'); 
    time.sleep(0.3)
    for rnd in range(3):
        time.sleep(1.3)
    inv3 = rc.run("data get entity Cam Inventory"); ups = inv3.count("amplifier: 1b"); tot = inv3.count("le_boost: 1b")
    print(f"   upgraded to II: {ups} of {tot} (expected about 25%)")
    check("level +1 chance about 25% (and never above II)", tot >= 20 and 0.08 <= ups / tot <= 0.5 and "amplifier: 2b" not in inv3, (ups, tot))
def t_murky():
    print("[murky vials]")
    setc(1, 3, 0); rc.run("clear Cam"); rc.run("execute as Cam run function last_ember:potion/murky {effect:\"weakness\",duration:600,amp:0}"); time.sleep(2.4)
    inv = rc.run("data get entity Cam Inventory")
    check("a seer keeps the murky vial murky", "le_murky: 1b" in inv and "Мутная склянка" in inv)
    rc.run("item replace entity Cam weapon.mainhand from entity Cam hotbar.0" if False else "clear Cam minecraft:trial_key"); inv_ = rc.run("data get entity Cam Inventory"); m_ = re.search(r"Slot: (\d+)b, id: \"minecraft:potion\"", inv_)
    if m_: rc.run(f"item replace entity Cam weapon.mainhand from entity Cam hotbar.{m_.group(1)}")
    rc.run("effect clear Cam minecraft:weakness"); act("Cam", "!use_on"); time.sleep(2.4); act("Cam", "!use_off"); time.sleep(0.5)
    check("a murky vial can be drunk by anyone (the effect applies)", "weakness" in rc.run("data get entity Cam active_effects"))
    setc(1, 4, 0); rc.run("clear Cam"); rc.run("execute as Cam run function last_ember:potion/murky {effect:\"weakness\",duration:600,amp:0}"); time.sleep(2.4)
    inv = rc.run("data get entity Cam Inventory")
    check("a healer identifies it: the name, the effects, no mark", "le_murky" not in inv and "Мутная" not in inv and "effect.minecraft.weakness" in inv and "tooltip_display" not in inv, inv[-500:])
def recipe_check(name, items, expect, tier=0, count_range=None):
    res = [r for r in brew(items, tier) if "minecraft:bucket" not in r and "minecraft:glass_bottle" not in r]; txt = " ".join(res)
    ok_ = len(res) > 0 and all(e in txt for e in expect)
    check(f"recipe {name} (tier {tier}): {len(res)} vial(s)" + (f", in range {count_range}" if count_range else ""), ok_ and (count_range is None or count_range[0] <= len(res) <= count_range[1]), txt[:300])
    return len(res)
def t_brew():
    print("[cauldron: recipes]")
    R = [("healing", ["brown_mushroom", "cooked_beef", "sugar"], ["instant_health", "minecraft:potion\""]),
         ("strength", ["red_mushroom", "bone", "gunpowder"], ["id: \"minecraft:strength\"", "duration: 5400"]),
         ("speed", ["brown_mushroom", "rabbit_foot"], ["id: \"minecraft:speed\"", "duration: 5400"]),
         ("night_vision", ["brown_mushroom", "pumpkin", "glow_berries"], ["night_vision", "duration: 5400"]),
         ("poison (splash)", ["brown_mushroom", "spider_eye", "rotten_flesh"], ["minecraft:poison", "splash_potion", "duration: 1350"]),
         ("fire_resistance", ["brown_mushroom", "lava_bucket", "honey_bottle"], ["fire_resistance", "duration: 5400"]),
         ("water_breathing", ["brown_mushroom", "cod", "kelp"], ["water_breathing", "duration: 5400"]),
         ("antidote", ["brown_mushroom", "honey_bottle", "glow_berries", "milk_bucket"], ["le_antidote: 1b", "Противоядие"]),
         ("oil of poison", ["brown_mushroom", "spider_eye", "slime_ball"], ["le_oiltype: \"poison\""]),
         ("oil of fire", ["brown_mushroom", "charcoal", "gunpowder"], ["le_oiltype: \"fire\""])]
    for name, items, ex in R: recipe_check(name, items, ex, 0, (1, 3))
    # bucket returned for lava / milk
    res = brew(["brown_mushroom", "lava_bucket", "honey_bottle"], 0); txt = " ".join(res)
    check("the lava bucket returns empty, the honey bottle returns as a bottle", "minecraft:bucket" in txt and "minecraft:glass_bottle" in txt, txt[-300:])
    # the count by tier: 1..3 at tier 0, 2..6 at tier 6
    c0 = [recipe_check("healing", R[0][1], R[0][2], 0) for _ in range(6)]; c6 = [recipe_check("healing", R[0][1], R[0][2], 6) for _ in range(6)]
    print(f"   vials per brew: tier 0 {c0}, tier 6 {c6}")
    check("tier 0: 1..3 per brew, tier 6: 2..6 per brew, tier 6 gives more on average", min(c0) >= 1 and max(c0) <= 3 and min(c6) >= 2 and max(c6) <= 6 and sum(c6) > sum(c0), (c0, c6))
def t_brew2():
    print("[cauldron: rules]")
    healer_setup(0); cauldron_setup(3)
    throw("cobblestone"); check("a foreign item is pushed out", cscore("le.cmask") == 0 and len(drain()) == 1)
    throw("brown_mushroom", count=3); m = cscore("le.cmask"); rest = drain(); check("a stack: one mushroom taken, two pushed out", m == 1 and len(rest) == 1 and "count: 2" in rest[0], (m, rest))
    throw("brown_mushroom"); check("a second mushroom is pushed out (one of each)", cscore("le.cmask") == 1 and len(drain()) == 1)
    cauldron_setup(3); throw("brown_mushroom", who="Cam2"); check("ingredients of a non-healer are pushed out", cscore("le.cmask") == 0 and len(drain()) == 1)
    cauldron_setup(3); throw("brown_mushroom"); throw("spider_eye"); throw("slime_ball"); throw("bone"); check("an ingredient that fits no recipe is pushed out", cscore("le.cmask") == 1 + 256 + 32768 and len(drain()) == 1)
    wait_idle(150, 40); res = drain()
    cauldron_setup(0); throw("brown_mushroom"); throw("cooked_beef"); throw("sugar"); wait_idle(150, 30)
    check("no water: nothing brews", cscore("le.cstate") == 0 and cscore("le.cmask") == 7 and len(drain()) == 0)
    cauldron_setup(2); throw("brown_mushroom"); throw("cooked_beef"); throw("sugar"); wait_idle(); drain()
    check("one level of water is used per brew (2 -> 1)", "level=1" in rc.run("data get block -10 103 -20 {}") or "level\": \"1\"" in rc.run("data get block -10 103 -20 {}") or "passed" in rc.run("execute if block -10 103 -20 minecraft:water_cauldron[level=1]"))
    # modifiers: the potion thrown in first, then the modifier
    for mod, item, ex in (("longer", "sugar", ["duration: 7200", "дольше"]), ("longer (honey)", "honey_bottle", ["duration: 7200"]), ("stronger", "bone_meal", ["amplifier: 1b", "duration: 1800", "сильнее"]),
                          ("splash", "gunpowder", ["splash_potion", "взрывное"]), ("lingering", "cobweb", ["lingering_potion", "туманное"])):
        cauldron_setup(3); pot = "swiftness" if mod == "stronger" else "strength"
        throw_item_nbt('{id:"minecraft:potion",count:1,components:{"minecraft:potion_contents":{potion:"minecraft:%s"}}}' % pot); throw(item); wait_idle(); res = " ".join(drain())
        check(f"modifier {mod}: {ex}", all(e in res for e in ex) and "le_mod: 1b" in res, res[:400])
    cauldron_setup(3); throw_item_nbt('{id:"minecraft:potion",count:1,components:{"minecraft:custom_data":{le_mod:1b},"minecraft:potion_contents":{potion:"minecraft:strength"}}}'); check("a potion with a modifier takes no second one", cscore("le.cmask") == 0 and len(drain()) == 1)

def t_oil():
    print("[oil]")
    for tier, hits in ((0, 8), (6, 16)):
        setc(1, 4, tier); tp("Cam", 0.5, 103, -14.5, 0, 0); rc.run("kill @e[tag=le.test]"); time.sleep(0.4); rc.run("clear Cam")
        rc.run("item replace entity Cam weapon.mainhand with minecraft:stone_sword"); rc.run("execute as Cam run function last_ember:potion/give_oil_poison"); time.sleep(0.4)
        inv = rc.run("data get entity Cam Inventory"); m = re.search(r"Slot: (\d+)b, id: \"minecraft:potion\"", inv)
        rc.run(f"item replace entity Cam weapon.offhand from entity Cam hotbar.{m.group(1)}" if int(m.group(1)) < 9 else "item replace entity Cam weapon.offhand from entity Cam container." + m.group(1)); rc.run(f"clear Cam minecraft:potion")
        rc.run("item replace entity Cam weapon.offhand with minecraft:air"); rc.run("execute as Cam run function last_ember:potion/give_oil_poison"); time.sleep(0.4)
        inv = rc.run("data get entity Cam Inventory"); m = re.search(r"Slot: (\d+)b, id: \"minecraft:potion\"", inv); sl = int(m.group(1))
        rc.run(f"item replace entity Cam weapon.offhand from entity Cam {'hotbar' if sl < 9 else 'container'}.{sl}"); rc.run(f"item replace entity Cam {'hotbar' if sl < 9 else 'container'}.{sl} with minecraft:air")
        act("Cam", "!use_on"); time.sleep(1.8); act("Cam", "!use_off"); time.sleep(0.6)
        sw = rc.run("data get entity Cam SelectedItem.components")
        check(f"tier {tier}: the oil puts {hits} hits on the sword", f"n: {hits}" in sw and "poison" in sw and f"{hits} ударов" in sw or f"Масло яда: {hits}" in sw, sw[:300])
        rc.run("summon minecraft:pillager 0.5 103 -12.5 {NoAI:1b,Tags:[\"le.test\",\"le.keep\"],PersistenceRequired:1b}"); time.sleep(0.5)
        rc.run("damage @e[tag=le.test,limit=1] 1 minecraft:player_attack by Cam"); time.sleep(0.6)
        check(f"tier {tier}: a hit poisons the husk and costs one hit", "poison" in rc.run("data get entity @e[tag=le.test,limit=1] active_effects") and f"n: {hits - 1}" in rc.run("data get entity Cam SelectedItem.components"))
        for k in range(hits - 1):
            rc.run("effect clear @e[tag=le.test] minecraft:poison"); time.sleep(1.1); rc.run("damage @e[tag=le.test,limit=1] 1 minecraft:player_attack by Cam"); time.sleep(0.3)
        sw = rc.run("data get entity Cam SelectedItem.components")
        check(f"tier {tier}: after {hits} hits the oil is gone", "type: \"none\"" in sw and "Масло" not in sw, sw[:300])
        rc.run("kill @e[tag=le.test]")
    # carried to another player with the sword
    setc(1, 4, 0); tp("Cam", 0.5, 103, -14.5, 0, 0); rc.run("clear Cam"); rc.run("item replace entity Cam weapon.mainhand with minecraft:stone_sword[minecraft:custom_data={le_oil:{type:\"fire\",n:5}}]")
    rc.run("execute as Cam run item replace entity Cam weapon.mainhand from entity Cam weapon.mainhand"); sw = rc.run("data get entity Cam SelectedItem.components")
    check("the mark lives on the item (it moves with the sword)", "fire" in sw)
def t_amulet():
    print("[amulet]")
    for tier, cd in ((0, 1200), (6, 600)):
        setc(1, 4, tier); setc(1, 1, 0, "Cam2"); tp("Cam", 0.5, 103, -14.5, 0, 0); tp("Cam2", 3.5, 103, -14.5, 0, 0); time.sleep(1.0)
        rc.run("scoreboard players set Cam le.amcd 0"); rc.run("effect clear Cam2"); rc.run("damage Cam2 19 minecraft:generic"); time.sleep(0.8)
        fx = rc.run("data get entity Cam2 active_effects"); check(f"tier {tier}: the partner gets Resistance III + Absorption I", "resistance" in fx and "absorption" in fx and "amplifier: 2b" in fx, fx)
        rc.run("effect clear Cam2"); rc.run("effect give Cam2 minecraft:instant_health 1 10 true"); time.sleep(0.5); rc.run("damage Cam2 19 minecraft:generic"); time.sleep(0.8)
        check(f"tier {tier}: the cooldown holds", "absorption" not in rc.run("data get entity Cam2 active_effects"))
        sw = score("Cam", "le.amcd"); gt = int(re.search(r"is (\d+)", rc.run("time query gametime")).group(1)); print(f"   cooldown left at tier {tier}: {sw - gt} ticks")
        check(f"tier {tier}: cooldown ~{cd // 20} s", cd - 120 <= sw - gt <= cd, sw - gt)
    setc(1, 4, 0); rc.run("effect clear Cam"); rc.run("scoreboard players set Cam le.amcd 0"); rc.run("effect give Cam minecraft:instant_health 1 10 true"); time.sleep(0.4); rc.run("damage Cam 16 minecraft:generic"); time.sleep(0.8)
    check("the healer does not protect himself", "absorption" not in rc.run("data get entity Cam active_effects"))
    # two partners below 6: the weaker one
    setc(1, 4, 0); setc(1, 1, 0, "Cam2"); tp("Cam", 0.5, 103, -14.5); tp("Cam2", 3.5, 103, -14.5); time.sleep(1.0); rc.run("scoreboard players set Cam le.amcd 0")
    rc.run("summon minecraft:armor_stand 0.5 103 -12.5 {Tags:[\"le.test\"]}")
def t_throw():
    print("[potion throw range]")
    rc.run("forceload add 300 300 700 302"); time.sleep(4); rc.run("fill 300 250 300 700 250 302 minecraft:stone")
    def land(U, theta, v=0.5, who=True):
        rc.run("kill @e[type=minecraft:splash_potion]"); vx, vy = v * math.cos(math.radians(theta)), v * math.sin(math.radians(theta))
        own = f"Owner:[I;{U}]," if who else ""
        rc.run("tick rate 5"); rc.run(f"summon minecraft:splash_potion 300.5 251.0 301.5 {{{own}Motion:[{vx}d,{vy}d,0.0d],Item:{{id:\"minecraft:splash_potion\",count:1}}}}"); x = None; t0 = time.time()
        while time.time() - t0 < 30:
            time.sleep(0.04); r = rc.run("data get entity @e[type=minecraft:splash_potion,limit=1] Pos")
            m = re.search(r"\[([-0-9.]+)d", r)
            if not m: break
            x = float(m.group(1))
        rc.run("tick rate 20"); return (x or 300.5) - 300.5
    setc(1, 4, 0); U = uuid("Cam"); mob = [land(U, 35, who=False) for _ in range(3)]; hl = [land(U, 35) for _ in range(3)]
    setc(1, 1, 0); U = uuid("Cam"); kn = [land(U, 35) for _ in range(3)]
    a = lambda l: sum(l) / len(l)
    print(f"   range: nobody {a(mob):.2f}, healer {a(hl):.2f} (x{a(hl) / a(mob):.2f}), knight {a(kn):.2f}")
    check("healer: thrown potions fly 1.5x farther (+-5%)", 1.43 <= a(hl) / a(mob) <= 1.57, (mob, hl)); check("a knight's potion is not changed", abs(a(kn) - a(mob)) < 0.5, (kn, mob))
def t_misc():
    print("[antidote, fire oil, water]")
    setc(1, 4, 0); rc.run("clear Cam"); tp("Cam", 0.5, 103, -14.5, 0, 0)
    rc.run("execute as Cam run function last_ember:potion/give_antidote"); rc.run("effect give Cam minecraft:poison 30 0"); rc.run("effect give Cam minecraft:wither 30 0"); time.sleep(0.4)
    inv = rc.run("data get entity Cam Inventory"); m = re.search(r"Slot: (\d+)b, id: \"minecraft:potion\"", inv); sl = int(m.group(1))
    rc.run(f"item replace entity Cam weapon.mainhand from entity Cam {'hotbar' if sl < 9 else 'container'}.{sl}"); act("Cam", "!use_on"); time.sleep(3.2); act("Cam", "!use_off"); time.sleep(1.0)
    fx = rc.run("data get entity Cam active_effects")
    check("antidote: poison and wither are gone", "poison" not in fx and "wither" not in fx, fx)
    rc.run("effect give Cam minecraft:poison 30 0"); time.sleep(0.4); check("antidote: immunity - a new poison is cleared at once", "poison" not in rc.run("data get entity Cam active_effects"))
    rc.run("scoreboard players set Cam le.immune 0"); time.sleep(0.4); rc.run("effect give Cam minecraft:poison 30 0"); time.sleep(0.4)
    check("antidote: after 60 s the immunity ends", "poison" in rc.run("data get entity Cam active_effects")); rc.run("effect clear Cam")
    setc(1, 4, 0); tp("Cam", 0.5, 103, -14.5, 0, 0); rc.run("kill @e[tag=le.test]"); time.sleep(0.4)
    rc.run("item replace entity Cam weapon.mainhand with minecraft:stone_sword[minecraft:custom_data={le_oil:{type:\"fire\",n:3}}]")
    rc.run("summon minecraft:pillager 0.5 103 -12.5 {NoAI:1b,Tags:[\"le.test\",\"le.keep\"],PersistenceRequired:1b}"); time.sleep(0.5)
    rc.run("damage @e[tag=le.test,limit=1] 1 minecraft:player_attack by Cam"); time.sleep(0.5)
    check("oil of fire sets the mob on fire", "passed" in rc.run("execute if entity @e[tag=le.test,nbt={Fire:1s}]") or int(re.search(r"(-?\d+)s", rc.run("data get entity @e[tag=le.test,limit=1] Fire")).group(1)) > 0)
    rc.run("kill @e[tag=le.test]")
    # water: bucket and bottles into the cauldron by a real click, only for a healer
    for who, cls, expect in (("Cam", 4, True), ("Cam", 1, False)):
        setc(1, cls, 0); cauldron_setup(0); rc.run("clear Cam"); rc.run("item replace entity Cam weapon.mainhand with minecraft:water_bucket"); tp("Cam", -9.5, 103, -22.0, 0, 0)
        face("Cam", -9.5, 103, -22.0, -9.5, 103.6, -19.5); time.sleep(0.6); act("Cam", "!use"); time.sleep(1.0)
        full = "passed" in rc.run("execute if block -10 103 -20 minecraft:water_cauldron[level=3]")
        check(f"class {cls}: a water bucket on the cauldron {'fills it' if expect else 'does nothing'}", full == expect)
    setc(1, 4, 0); cauldron_setup(0); rc.run("clear Cam")
    for k in range(3):
        rc.run('item replace entity Cam weapon.mainhand with minecraft:potion[minecraft:potion_contents={potion:"minecraft:water"}]'); face("Cam", -9.5, 103, -22.0, -9.5, 103.6, -19.5); time.sleep(0.5); act("Cam", "!use"); time.sleep(0.8)
    check("three water bottles fill it to level 3", "passed" in rc.run("execute if block -10 103 -20 minecraft:water_cauldron[level=3]"))

def t_multi():
    print("[two players at once]")
    # two knights at one bonfire
    for who in ("Cam", "Cam2"): rc.run(f"scoreboard players set {who} le.blday -1"); rc.run(f"tag {who} remove le.sated"); rc.run(f"scoreboard players set {who} le.bless 0")
    setc(1, 1, 0); setc(3, 1, 6, "Cam2"); tp("Cam", 0.5, 103, 5.5); tp("Cam2", -1.5, 103, 5.5)
    for who in ("Cam", "Cam2"): rc.run(f"item replace entity {who} armor.chest with minecraft:chainmail_chestplate[minecraft:damage=100]")
    rc.run("tick rate 100"); t0 = time.time()
    while time.time() - t0 < 30:
        time.sleep(0.5)
        if (score("Cam", "le.blday") or -1) >= 0 and (score("Cam2", "le.blday") or -1) >= 0: break
    rc.run("tick rate 20"); time.sleep(0.5)
    ok2 = all(any(f"minecraft:damage\": {v}" in rc.run(f"data get entity {w} equipment.chest.components") for v in (27, 28, 29)) for w in ("Cam", "Cam2"))
    check("two knights at one bonfire: both blessed and repaired (100 -> 28)", ok2, [rc.run(f"data get entity {w} equipment.chest.components") for w in ("Cam", "Cam2")])
    check("both knights and sated tags", "le.sated" in rc.run("tag Cam list") and "le.sated" in rc.run("tag Cam2 list"))
    # two rangers blow at the same moment
    time.sleep(1); setc(1, 2, 6); setc(2, 2, 0, "Cam2"); tp("Cam", 0.5, 103, -14.5, 0, 0); tp("Cam2", 6.5, 103, -14.5, 0, 0); rc.run("kill @e[tag=le.test]"); time.sleep(0.4)
    rc.run("summon minecraft:husk 0.5 103 5.5 {NoAI:1b,Tags:[\"le.test\",\"le.keep\",\"le.a\"],PersistenceRequired:1b}"); rc.run("summon minecraft:husk 6.5 103 -34.5 {NoAI:1b,Tags:[\"le.test\",\"le.keep\",\"le.b\"],PersistenceRequired:1b}")
    time.sleep(1.0)
    for who in ("Cam", "Cam2"):
        inv = rc.run(f"data get entity {who} Inventory"); m = re.search(r"Slot: (\d+)b, id: \"minecraft:stick\"", inv)
        rc.run(f"item replace entity {who} weapon.mainhand from entity {who} {'hotbar' if int(m.group(1)) < 9 else 'container'}.{m.group(1)}")
    act("Cam", "!use_on"); act("Cam2", "!use_on"); time.sleep(1.0); act("Cam", "!use_off"); act("Cam2", "!use_off"); time.sleep(0.8)
    fa = "glowing" in rc.run("data get entity @e[tag=le.a,limit=1] active_effects"); fb = "glowing" in rc.run("data get entity @e[tag=le.b,limit=1] active_effects")
    check("two rangers blow at once: Cam (tier 6, r 32) lights the husk at 20, Cam2 (tier 0, r 24) lights the husk at 20", fa and fb, (fa, fb)); rc.run("kill @e[tag=le.test]")
    # the healer brews while the partner throws his own things in
    setc(1, 4, 0); setc(1, 1, 0, "Cam2"); tp("Cam", -9.5, 103, -22.0, 0, 0); tp("Cam2", -8.5, 103, -22.0, 0, 0); cauldron_setup(3)
    for it in ("brown_mushroom", "cooked_beef"): throw(it)
    throw("brown_mushroom", who="Cam2"); throw("spider_eye", who="Cam2"); throw("sugar"); wait_idle(); res = drain()
    pots = [r for r in res if "minecraft:potion" in r and "instant_health" in r]
    inv2 = rc.run("data get entity Cam2 Inventory")
    check("the healer's recipe is brewed; the partner's items come back to the partner", 1 <= len(pots) <= 3 and ("brown_mushroom" in inv2 or any("brown_mushroom" in r for r in res)) and ("spider_eye" in inv2 or any("spider_eye" in r for r in res)), ([r[:60] for r in res], inv2[:200]))
SECT = {"knight": t_knight, "bless": t_bless, "ranger": t_ranger, "horn": t_horn, "tame": t_tame, "boost": t_boost, "murky": t_murky, "brew": t_brew, "brew2": t_brew2, "oil": t_oil, "amulet": t_amulet, "throw": t_throw, "misc": t_misc, "multi": t_multi}
if __name__ == "__main__":
    for s in (sys.argv[1:] or list(SECT)): SECT[s]()
    print(f"\n{ok} ok, {bad} failed"); sys.exit(1 if bad else 0)
