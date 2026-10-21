#!/usr/bin/env python3
"""T-007 tests with two real clients (Cam, Cam2): what stays, trail on the spot, pick-up by owner and teammate,
second death -> first trail to the urn, lava and void -> urn, death in a wall -> nearest free spot, the urn hand-out with
overflow into the bowl, the Ember, item fidelity. Test urn r0 at (200,110,160) (gen_death.py death/test_urns.txt)."""
import importlib.util, os, re, socket, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("rcon", os.path.join(ROOT, "tools/rcon.py")); rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
p = rc.props(); S = socket.create_connection(("127.0.0.1", int(p["rcon.port"])), timeout=60); rc.pkt(S, 1, 3, p["rcon.password"]); rc.read(S)
def R(c): return rc.exchange(S, c)
DIR = {"Cam": "server/client", "Cam2": "server/client2"}
res = []
def ok(name, cond, info=""): res.append(bool(cond)); print(("PASS " if cond else "FAIL ") + name + (f"  [{info}]" if info else ""), flush=True)
def act(pl, a):
    d = os.path.join(ROOT, DIR[pl]); done = os.path.join(d, "shot-done.txt")
    if os.path.exists(done): os.remove(done)
    open(os.path.join(d, "shot-request.txt"), "w").write(f"!{a}\n")
    for _ in range(60):
        if os.path.exists(done): break
        time.sleep(0.05)
    time.sleep(0.5)
def face(pl, x, y, z, tx, ty, tz): R(f"tp {pl} {x} {y} {z}"); R(f"execute as {pl} at @s anchored eyes facing {tx} {ty} {tz} run tp @s ~ ~ ~ ~ ~"); time.sleep(0.5)
def pick(pl, x, y, z):
    R(f"fill {x-1} {y} {z+1} {x+1} {y+1} {z+2} minecraft:air"); R(f"setblock {x} {y-1} {z+2} minecraft:stone")
    face(pl, x + 0.5, y, z + 2.0, x + 0.5, y + 0.3, z + 0.5); act(pl, "use"); time.sleep(0.8)
def die(pl): R(f"effect clear {pl} minecraft:resistance"); R(f"kill {pl}"); time.sleep(3.5); R(f"effect give {pl} minecraft:resistance infinite 255 true")
def inv(pl): return R(f"data get entity {pl} Inventory")
def trails(): return re.findall(r"t(\d+): \{", R("data get storage last_ember:ash t"))
def rec(i, path=""): return R(f"data get storage last_ember:ash t.t{i}{path}")
def urn_count(): return R("data get storage last_ember:ash urns.r0.trails").count("owner:")
def ground(x, z):  # put the player on the surface at (x, z)
    R(f"execute in minecraft:overworld positioned {x} 0 {z} positioned over motion_blocking_no_leaves run tp Cam ~ ~ ~"); time.sleep(1.0)
SWORD = 'minecraft:diamond_sword[minecraft:custom_name={"text":"Клинок теста","color":"red"},minecraft:enchantments={"minecraft:sharpness":3},minecraft:custom_data={probe:42}]'
BOOK = 'minecraft:enchanted_book[minecraft:stored_enchantments={"minecraft:mending":1}]'
POT = 'minecraft:potion[minecraft:potion_contents={potion:"minecraft:strong_healing"},minecraft:custom_name="Зелье теста"]'
KEEP = 'minecraft:stick[minecraft:custom_data={le_keep:1b},minecraft:custom_name="Посох (le_keep)"]'
KEY = 'minecraft:amethyst_shard[minecraft:custom_data={le_key:1b},minecraft:custom_name="Ключ главы"]'
def kit():
    R("clear Cam"); R("xp set Cam 0 levels"); R("xp set Cam 0 points")
    R(f"item replace entity Cam hotbar.0 with {SWORD}")
    R("item replace entity Cam hotbar.1 with minecraft:bread 5"); R(f"item replace entity Cam hotbar.4 with {KEEP}")
    R(f"item replace entity Cam hotbar.6 with {KEY}"); R(f"item replace entity Cam inventory.0 with {BOOK}"); R(f"item replace entity Cam inventory.10 with {POT}")
    R("item replace entity Cam inventory.20 with minecraft:cobblestone 30")
    for s, it in (("armor.head", "leather_helmet"), ("armor.chest", "leather_chestplate"), ("armor.legs", "leather_leggings"), ("armor.feet", "leather_boots"), ("weapon.offhand", "shield")):
        R(f"item replace entity Cam {s} with minecraft:{it}")
    R("xp add Cam 7 levels"); R("xp add Cam 5 points")

for pl in DIR: R(f"gamemode survival {pl}"); R(f"effect give {pl} minecraft:resistance infinite 255 true"); R(f"effect give {pl} minecraft:saturation infinite 1 true")
R("time set noon"); R("gamerule advance_time false"); R("execute in minecraft:overworld run forceload add 112 112 271 271")
R("data modify storage last_ember:ash t set value {}"); R("data modify storage last_ember:ash urns.r0.trails set value []"); R("kill @e[tag=le.ash]")
for pl in DIR: R(f"scoreboard players set {pl} le.ash 0"); R(f"spawnpoint {pl} 230 110 230")
R("fill 225 109 225 235 109 235 minecraft:stone"); R("fill 225 110 225 235 112 235 minecraft:air")
# 1. what stays / what goes
ground(170, 170); kit()
before_sword = re.search(r'\{[^{}]*?Slot: 0b[^{}]*?\}|\{components: \{"minecraft:custom_name".*?id: "minecraft:diamond_sword"\}', inv("Cam"))
R("execute as Cam run function last_ember:ember/give_to_me"); time.sleep(0.3)
die("Cam")
iv, eq = inv("Cam"), R("data get entity Cam equipment")
kept_ok = all(s in iv for s in ("diamond_sword", "le_keep", "le_key", "le_ember")) and not any(s in iv for s in ("bread", "enchanted_book", "potion", "cobblestone"))
ok("death: kept = selected slot (sword), le_keep, le_key, Ember; lost = bread, book, potion, cobblestone", kept_ok, iv[-160:])
ok("death: armor and off-hand kept", all(s in eq for s in ("leather_helmet", "leather_chestplate", "leather_leggings", "leather_boots", "shield")))
ok("death: XP taken", "has 0" in R("xp query Cam levels"))
ts = trails(); ok("trail recorded and placed (interaction + display)", len(ts) == 1 and "passed" in R("execute if entity @e[type=minecraft:interaction,tag=le.ash]") and "passed" in R("execute if entity @e[type=minecraft:item_display,tag=le.ash_disp]"), str(ts))
t1 = ts[0]; x, y, z = (int(re.search(r"contents: (-?\d+)", rec(t1, k)).group(1)) for k in (".x", ".y", ".z"))
ok("trail at the death spot (within 2 blocks of 170,_,170)", abs(x - 170) <= 2 and abs(z - 170) <= 2, f"{x} {y} {z}")
ok("trail contents: 4 stacks, 7 levels", rec(t1, ".items").count("id:") == 4 and "7" in rec(t1, ".lv"), rec(t1, ".lv"))
ok("Ember not duplicated", sum(1 for pl in DIR if "le_ember" in inv(pl)) == 1 and R("execute as @e[type=minecraft:item] if items entity @s contents *[minecraft:custom_data~{le_ember:1b}] run tag @s add q") == "" and "failed" in R("execute if entity @e[tag=q]"))
# 2. owner picks it up (real right click)
pick("Cam", x, y, z)
iv2 = inv("Cam")
ok("owner picks up: all 4 stacks back, XP back, trail gone", all(s in iv2 for s in ("bread", "enchanted_book", "potion", "cobblestone")) and "has 7" in R("xp query Cam levels") and not trails() and "failed" in R("execute if entity @e[tag=le.ash]"))
ok("item fidelity: book enchantment, potion name and contents intact", 'stored_enchantments": {"minecraft:mending": 1}' in iv2 and "Зелье теста" in iv2 and "strong_healing" in iv2)
# 3. teammate picks up
ground(150, 180); R("xp add Cam 3 levels"); die("Cam"); t2 = trails()[0]
x, y, z = (int(re.search(r"contents: (-?\d+)", rec(t2, k)).group(1)) for k in (".x", ".y", ".z"))
R("clear Cam2"); pick("Cam2", x, y, z)
ok("teammate picks up the trail", "enchanted_book" in inv("Cam2") and not trails())
R("clear Cam2"); R("xp set Cam2 0 levels")
# 4. second death -> first trail to the urn
u0 = urn_count(); kit(); ground(165, 185); die("Cam"); ta = trails()
kit(); ground(185, 165); die("Cam"); tb = trails()
ok("second death: first trail goes to the urn, second stays on the ground", len(tb) == 1 and tb != ta and urn_count() == u0 + 1 and "Cam" in R("data get storage last_ember:ash urns.r0.names"), f"{ta}->{tb}, urn {urn_count()}")
ok("urn lit: candles on", "passed" in R("execute if block 199 116 159 minecraft:candle[lit=true]"))
# 5. lava -> urn
u0 = urn_count(); kit(); R("fill 140 100 140 144 103 144 minecraft:stone"); R("fill 141 101 141 143 103 143 minecraft:lava"); R("tp Cam 142 102 142")
R("effect clear Cam minecraft:resistance"); time.sleep(8); R("effect give Cam minecraft:resistance infinite 255 true")
# u0+2: the trail of the previous death (still on the ground) went to the urn as well
ok("death in lava: straight to the urn (no new trail)", urn_count() >= u0 + 2 and len(trails()) == 0 and "failed" in R("execute if entity @e[tag=le.ash]"), f"urn {urn_count()} trails {trails()}")
# 6. void -> urn
u0 = urn_count(); kit(); R("tp Cam 190 -120 190"); R("effect clear Cam minecraft:resistance"); time.sleep(5); R("effect give Cam minecraft:resistance infinite 255 true")
ok("death in the void: straight to the urn", urn_count() == u0 + 1 and len(trails()) == 0, f"urn {urn_count()}")
# 7. death inside a wall -> nearest free spot
kit(); ground(123, 123); gy = int(float(re.search(r", ([-\d.]+)d, ", R("data get entity Cam Pos")).group(1)))
R(f"fill 121 {gy} 121 125 {gy + 4} 125 minecraft:stone"); ld0 = R("data get entity Cam LastDeathLocation"); R(f"tp Cam 123 {gy + 2} 123"); R("effect clear Cam minecraft:resistance")
for _ in range(60):  # wait for the suffocation death, then immunity again at once
    time.sleep(0.25)
    if R("data get entity Cam LastDeathLocation") != ld0: break
R("effect give Cam minecraft:resistance infinite 255 true"); time.sleep(3)
tw = trails(); ok("death in a wall: trail on the nearest free spot within 8 blocks", len(tw) == 1, str(tw))
if tw:
    x, y, z = (int(re.search(r"contents: (-?\d+)", rec(tw[0], k)).group(1)) for k in (".x", ".y", ".z"))
    ok("  the spot is free with ground below", "passed" in R(f"execute if block {x} {y} {z} #last_ember:ash_free") and "passed" not in R(f"execute if block {x} {y - 1} {z} #last_ember:ash_free"), f"{x} {y} {z}")
# 8. urn hand-out with overflow into the bowl
R("clear Cam2"); R("give Cam2 minecraft:dirt 2304")  # 36 full stacks -> no room
face("Cam2", 201.7, 111, 162.4, 200.5, 112.5, 160.5); act("Cam2", "use"); time.sleep(1.2)
ok("urn hand-out: urn empty, candles off", urn_count() == 0 and "passed" in R("execute if block 199 116 159 minecraft:candle[lit=false]"))
ok("overflow lands in the bowl (items at the cauldron)", "passed" in R("execute positioned 200.5 111 163.5 if entity @e[type=minecraft:item,distance=..1.5]"))
R("clear Cam2"); time.sleep(0.3); R("tp Cam2 200.5 111.2 163.5"); time.sleep(1.5)
ok("items from the bowl can be picked up", "enchanted_book" in inv("Cam2"))
print(f"\n{sum(res)}/{len(res)} passed")
