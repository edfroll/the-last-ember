#!/usr/bin/env python3
"""T-005 tests with two real clients (Cam in server/client, Cam2 in server/client2) and test bonfires
(gen_bonfires.py bonfires/test_bonfires.txt): t_main(1) 200 110 200 lit start, t_one(2) 230.., t_two(3) 260..
Right clicks and Q are real client input via the dev agent (!use / !drop)."""
import importlib.util, os, re, socket, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("rcon", os.path.join(ROOT, "tools/rcon.py")); rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
p = rc.props(); S = socket.create_connection(("127.0.0.1", int(p["rcon.port"])), timeout=30); rc.pkt(S, 1, 3, p["rcon.password"]); rc.read(S)
def R(c): return rc.exchange(S, c)
DIR = {"Cam": "server/client", "Cam2": "server/client2"}
res = []
def ok(name, cond, info=""): res.append(bool(cond)); print(("PASS " if cond else "FAIL ") + name + (f"  [{info}]" if info else ""), flush=True)
def act(player, a):
    d = os.path.join(ROOT, DIR[player]); done = os.path.join(d, "shot-done.txt")
    if os.path.exists(done): os.remove(done)
    open(os.path.join(d, "shot-request.txt"), "w").write(f"!{a}\n")
    for _ in range(60):
        if os.path.exists(done): break
        time.sleep(0.05)
    time.sleep(0.35)
def face(player, x, y, z, tx, ty, tz):  # look from the eyes at the target point
    R(f"tp {player} {x} {y} {z}"); R(f"execute as {player} at @s anchored eyes facing {tx} {ty} {tz} run tp @s ~ ~ ~ ~ ~"); time.sleep(0.4)
def has_ember(pl): return "passed" in R(f"execute if items entity {pl} container.* *[minecraft:custom_data~{{le_ember:1b}}]")
def sb(pl): m = re.search(r"has (-?\d+)", R(f"scoreboard players get {pl} le.sb")); return int(m.group(1)) if m else None
def lit(x, y, z): return "passed" in R(f"execute if block {x} {y} {z} minecraft:campfire[lit=true]")
def state(i): m = re.search(r"contents: (\d)", R(f"data get storage last_ember:bonfires by.b{i}.state")); return int(m.group(1)) if m else None
def pos(pl):
    m = re.search(r"\[([-\d.]+)d, ([-\d.]+)d, ([-\d.]+)d\]", R(f"data get entity {pl} Pos")); return tuple(float(v) for v in m.groups()) if m else None
def respawn_at(pl):
    R(f"effect clear {pl} minecraft:resistance"); R(f"kill {pl}"); time.sleep(3.0); q = pos(pl); R(f"effect give {pl} minecraft:resistance infinite 255 true"); return q

R("time set noon"); R("weather clear")
# reset test state: t_one/t_two unlit, everyone bound to the start bonfire, socket empty
for i, x in ((2, 230), (3, 260)):
    R(f"data modify storage last_ember:bonfires by.b{i}.state set value 0"); R(f"setblock {x} 109 200 minecraft:cobbled_deepslate"); R(f"setblock {x} 110 200 minecraft:campfire[lit=false]")
R("kill @e[type=minecraft:item_display,tag=le.ember_disp]"); R("data merge storage last_ember:ember {socket:-1}"); R("tag @a remove le.carrier")
R("kill @e[type=minecraft:item]")
for pl in DIR: R(f"scoreboard players set {pl} le.sb 1"); R(f"execute as {pl} run function last_ember:bonfire/bind_start")
for pl in DIR:
    R(f"gamemode survival {pl}"); R(f"clear {pl}"); R(f"effect give {pl} minecraft:resistance infinite 255 true"); R(f"effect give {pl} minecraft:saturation infinite 1 true")
R("execute in minecraft:overworld run forceload add 176 176 287 223")
ok("first entry: both bound to the start bonfire (main, lit from the start)", sb("Cam") == 1 and sb("Cam2") == 1 and lit(200, 110, 200) and state(1) == 1)
q = respawn_at("Cam2"); ok("respawn at the start bonfire pad (200,110,197)", q and abs(q[0] - 200.5) < 1.6 and abs(q[2] - 197.5) < 1.6, str(q))
R("execute as Cam run function last_ember:ember/give_to_me"); time.sleep(0.3)
ok("Cam is the carrier and has the Ember", has_ember("Cam") and "passed" in R("execute if entity @a[name=Cam,tag=le.carrier]"))
# non-carrier tries to light t_one (hearth 230 110 200)
face("Cam2", 230.5, 110, 202.5, 230.5, 110.4, 200.5); act("Cam2", "use")
ok("Cam2 (not carrier) cannot light the bonfire", not lit(230, 110, 200) and state(2) == 0)
# carrier lights it; both within 16 get bound
face("Cam", 228.5, 110, 200.5, 230.5, 110.4, 200.5); act("Cam", "use")
ok("Cam (carrier) lights t_one: lit campfire, hay below, registry state 1", lit(230, 110, 200) and "passed" in R("execute if block 230 109 200 minecraft:hay_block") and state(2) == 1)
ok("both players within 16 now respawn at t_one", sb("Cam") == 2 and sb("Cam2") == 2)
# rest at the lit main bonfire: Cam2 only
face("Cam2", 200.5, 110, 202.5, 200.5, 110.4, 200.5); act("Cam2", "use")
ok("Cam2 rests at t_main: only Cam2 rebinds", sb("Cam2") == 1 and sb("Cam") == 2)
q = respawn_at("Cam"); ok("Cam respawns at t_one pad (230,110,197)", q and abs(q[0] - 230.5) < 1.6 and abs(q[2] - 197.5) < 1.6, str(q))
q = respawn_at("Cam2"); ok("Cam2 respawns at t_main pad (200,110,197)", q and abs(q[0] - 200.5) < 1.6 and abs(q[2] - 197.5) < 1.6, str(q))
# beds do not move the respawn point
for bed in ("minecraft:red_bed", "minecraft:straw_bed"):
    R("setblock 300 110 300 minecraft:air"); R("setblock 300 110 301 minecraft:air")
    R("fill 296 109 296 304 109 304 minecraft:stone"); R(f"setblock 300 110 301 {bed}[facing=south,part=head] strict"); R(f"setblock 300 110 300 {bed}[facing=south,part=foot] strict")
    R("execute in minecraft:overworld run forceload add 288 288 319 319"); R("time set midnight")
    R("fill 296 110 296 304 113 299 minecraft:air"); R("kill @e[type=#last_ember:monsters,distance=..40,x=300,y=110,z=300]")
    face("Cam", 300.5, 110, 298.5, 300.5, 110.3, 300.5); time.sleep(0.5); act("Cam", "use"); time.sleep(1.0)
    st = R("data get entity Cam SleepTimer"); m = re.search(r"(\d+)s", st)
    ok(f"{bed.split(':')[1]}: the player really sleeps in it", m is not None and int(m.group(1)) > 0, st[-30:]); time.sleep(1.0)
    R("time set noon"); time.sleep(1.5)
    q = respawn_at("Cam"); ok(f"{bed.split(':')[1]}: sleeping does not move the respawn point (still t_one)", q and abs(q[0] - 230.5) < 1.6 and abs(q[2] - 197.5) < 1.6, str(q))
# stela transfer at t_one (stela at 232 110 200)
R("clear Cam"); R("execute as Cam run function last_ember:ember/give_to_me")
face("Cam", 232.5, 110, 202.5, 232.5, 110.6, 200.5); act("Cam", "use")
ok("Cam puts the Ember into the t_one stela socket", not has_ember("Cam") and "passed" in R("execute if entity @e[type=minecraft:item_display,tag=le.ember_disp]") and "contents: 2" in R("data get storage last_ember:ember socket"))
face("Cam2", 233.5, 110, 202.5, 232.5, 110.6, 200.5); act("Cam2", "use")
ok("Cam2 takes it: Cam2 is the carrier, socket empty", has_ember("Cam2") and "passed" in R("execute if entity @a[name=Cam2,tag=le.carrier]") and "failed" in R("execute if entity @a[name=Cam,tag=le.carrier]") and "contents: -1" in R("data get storage last_ember:ember socket"))
# attempts to get rid of it
# put the Ember into the selected hotbar slot so that Q really throws it
R("execute unless items entity Cam2 weapon.mainhand *[minecraft:custom_data~{le_ember:1b}] run item replace entity Cam2 weapon.mainhand from entity Cam2 hotbar.0")
R("execute if items entity Cam2 weapon.mainhand *[minecraft:custom_data~{le_ember:1b}] if items entity Cam2 hotbar.0 *[minecraft:custom_data~{le_ember:1b}] unless items entity Cam2 hotbar.1 * run tag Cam2 add le.tmp")
g0 = R("data get storage last_ember:ember gen")
act("Cam2", "drop"); time.sleep(0.5)
print("   gen before/after Q:", g0[-4:], R("data get storage last_ember:ember gen")[-4:])
R("execute as @e[type=minecraft:item] if items entity @s contents *[minecraft:custom_data~{le_ember:1b}] run tag @s add le.q")
ok("Q: the Ember comes back, no Ember on the ground", has_ember("Cam2") and "failed" in R("execute if entity @e[tag=le.q]"))
R("setblock 240 110 205 minecraft:chest"); face("Cam2", 240.5, 110, 207.5, 240.5, 110.5, 205.5)
R("item replace block 240 110 205 container.0 from entity Cam2 hotbar.0"); R("clear Cam2 *[minecraft:custom_data~{le_ember:1b}]"); time.sleep(0.6)
ok("chest: the Ember comes back to Cam2, chest slot emptied", has_ember("Cam2") and "failed" in R("execute if items block 240 110 205 container.* *[minecraft:custom_data~{le_ember:1b}]"))
R("summon minecraft:item_frame 241 111 207 {Facing:2b,Tags:[\"tf\"]}"); R("summon minecraft:armor_stand 243 110 207 {Tags:[\"ta\"]}")
R("item replace entity @e[tag=tf,limit=1] contents from entity Cam2 hotbar.0"); R("clear Cam2 *[minecraft:custom_data~{le_ember:1b}]"); time.sleep(0.6)
ok("item frame: back to Cam2, frame empty", has_ember("Cam2") and "failed" in R("execute if items entity @e[tag=tf,limit=1] contents *[minecraft:custom_data~{le_ember:1b}]"))
R("item replace entity @e[tag=ta,limit=1] weapon.mainhand from entity Cam2 hotbar.0"); R("clear Cam2 *[minecraft:custom_data~{le_ember:1b}]"); time.sleep(0.6)
ok("armor stand: back to Cam2, stand empty", has_ember("Cam2") and "failed" in R("execute if items entity @e[tag=ta,limit=1] weapon.mainhand *[minecraft:custom_data~{le_ember:1b}]"))
R("setblock 245 109 210 minecraft:hopper"); face("Cam2", 245.5, 110, 210.5, 245.5, 108, 212.5); act("Cam2", "drop"); time.sleep(0.8)
ok("Q over a hopper: back to Cam2, hopper empty", has_ember("Cam2") and "failed" in R("execute if items block 245 109 210 container.* *[minecraft:custom_data~{le_ember:1b}]"))
n = sum(1 for pl in DIR if has_ember(pl)); ok("exactly one valid Ember among players", n == 1, f"{n}")
R("kill @e[tag=tf]"); R("kill @e[tag=ta]")
print(f"\n{sum(res)}/{len(res)} passed")
