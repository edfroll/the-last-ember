#!/usr/bin/env python3
"""T-025 checks on the R1 world (tools/build/rebuild.sh): the Garden of Silence and the Creaking armour. Clients Cam and Cam2 in the game.
  build    what the generator put: 6 hearts between pale oak logs, 12 faces, 10 sensors under moss carpet with bones and signs, the door
           shut, the book on the lectern, the key on its pedestal, the stand with the 4 pieces, the biome inside / outside
  hearts   a heart at night wakes and gives its creaking to a player near it; Cam breaks one heart by hand (attack key), the others
           are broken by setblock ... destroy: the count goes down, at 0 the garden falls asleep once (creakings crumble, door open,
           eyeblossoms closed, faces asleep); garden/reset puts it back
  faces    night -> towards the orangery with open eyes, day -> outward, closed; a player looking (<= 70 deg, <= 24) holds the face;
           asleep -> outward even at night
  silence  Cam walks over a sensor: 2 creakings 10..16 from it, behind Cam (> 120 deg), invulnerable, tagged; sensor cooldown 60 s,
           garden 20 s; sneaking over a sensor wakes nothing; they crumble after 60 s / when nobody is near; never more than 6
  key      Call before the key -> the pedestal; right click takes it (generation of T-013), the pedestal stays empty, Call goes elsewhere;
           the key carried to the Circle of the Weepers is accepted by its pedestal
  armor    the stand before the sleep: nothing; after: a set once per player (Cam2 gets his own); armour 15, toughness 0, knockback 0.1;
           durability, enchantable, repairable; kept on death
  still    Stillness: a monster in the look at 8 -> slowness III + weakness I, at 9 -> nothing (elf: 12 yes), 30 deg -> no, through a wall
           -> no, boss / NPC / creaking -> no, one target (the nearest of two in the look)
  zones    the orangery and the house cannot be broken (adventure), no monsters in the house
  restart  hearts, sleep, key survive a restart (stops and starts the server; the clients log in again by themselves? no: relaunch)
  perf     the garden loop with 2 players walking in it and 2 wearers of the armour
Usage: python3 tools/test_garden.py [build hearts faces silence key armor still zones perf]"""
import importlib.util, json, math, os, re, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
R = rc.run
ok = bad = 0
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n, flush=True)
    else: bad += 1; print("  FAIL", n, e, flush=True)
M = json.load(open(os.path.join(ROOT, "server/build/r1/garden.json")))
HEARTS = M["hearts"]; FACES = M["faces"]; SENS = M["sensors"]; PATH = M["path"]
def gd(n): return tc.score(n, "le.gd")
def passed(cmd): return "passed" in R(cmd)
def pos(sel):
    v = re.findall(r"(-?\d+\.?\d*)d", R(f"data get entity {sel} Pos")); return [float(x) for x in v] if len(v) == 3 else None
def wait(cond, t=10.0, step=0.3):
    t0 = time.time()
    while time.time() - t0 < t:
        if cond(): return True
        time.sleep(step)
    return cond()
def count(sel): m = re.search(r"(\d+)", R(f"execute store result score #tc le.gd if entity {sel}") or ""); return gd("#tc")
def blk(x, y, z, b): return passed(f"execute if block {x} {y} {z} {b}")
FL = "forceload add 224 -456 436 -244"
def stage(p2=True, night=False):
    for p in ("Cam", "Cam2"):
        if not passed(f"execute if entity @a[name={p},tag=le.cinit]"): tc.setc(1, 1, 0, p)
    R("weather clear 100000"); R("time set " + ("midnight" if night else "noon")); R("gamerule advance_time false"); R("difficulty hard")
    for p in ("Cam", "Cam2"):
        R(f"gamemode survival {p}"); R(f"effect give {p} minecraft:resistance infinite 4 true"); R(f"effect give {p} minecraft:saturation infinite 1 true")
        R(f"effect give {p} minecraft:regeneration infinite 2 true")
    R("tp Cam 240.5 121 -261.5 0 0"); R("tp Cam2 236.5 121 -261.5 0 0" if p2 else "gamemode spectator Cam2")
    if not p2: R("tp Cam2 240 200 -262")
    R(FL); wait(lambda: all(passed(f"execute if loaded {h['x']} {h['y']} {h['z']}") for h in HEARTS), 40)
    R("kill @e[type=minecraft:creaking]"); R("scoreboard players set #gcd le.gd 0")
    for s in SENS: R(f"scoreboard players set #sc{s['id']} le.gd 0")
def unstage(): R("forceload remove 224 -456 436 -244"); R("difficulty peaceful")
def path_at(i): x, z, y = PATH[i]; return x + 0.5, y, z + 0.5

def t_build():
    print("[build: the blocks of the generator]"); stage(False)
    for h in HEARTS:
        x, y, z = h["x"], h["y"], h["z"]
        chk(f"heart {h['id']} ({h['kind']}) at {x} {y} {z}: creaking_heart between pale oak logs",
            blk(x, y, z, "minecraft:creaking_heart[natural=true]") and blk(x, y - 1, z, "minecraft:pale_oak_log") and blk(x, y + 1, z, "minecraft:pale_oak_log"))
    for f in FACES:
        x, z, b = f["x"], f["z"], f["base"]; ox, oz = f["out"]
        fx, fz = x + 2 * ox if False else x, z
        chk(f"face {f['id']} ({f['kind']}): mask blocks there", any(blk(x + dx, b + dy, z + dz, "#minecraft:pale_oak_logs") or blk(x + dx, b + dy, z + dz, "minecraft:pale_oak_trapdoor")
                                                                 for dx in (-2, -1, 0, 1, 2) for dz in (-2, -1, 0, 1, 2) for dy in (1, 2, 3, 4)))
    signs = 0
    for s in SENS:
        x, y, z = s["x"], s["y"], s["z"]
        chk(f"sensor {s['id']}: sculk_sensor under pale moss carpet", blk(x, y, z, "minecraft:sculk_sensor") and blk(x, y + 1, z, "minecraft:pale_moss_carpet"))
        if s["sign"]:
            sx, sy, sz = s["sign"]; t = R(f"data get block {sx} {sy} {sz} front_text.messages")
            signs += "тихо" in t
    chk("a sign 'Здесь ходят тихо.' at every second sensor", signs == sum(1 for s in SENS if s["sign"]) == 5, signs)
    dx, dy, dz = M["door"]
    chk("the door of the house is shut", blk(dx, dy, dz, "minecraft:pale_oak_door[open=false]"))
    lx, ly, lz = M["lectern"]
    chk("the lectern holds 'Записки садовника'", "Записки садовника" in R(f"data get block {lx} {ly} {lz} Book"))
    kx, ky, kz = M["key"]
    wait(lambda: count("@e[type=minecraft:interaction,tag=le.gdkey]") == 1, 4)
    chk("the key on its pedestal (display + interaction)", count("@e[type=minecraft:interaction,tag=le.gdkey]") == 1 and count("@e[type=minecraft:item_display,tag=le.gdkey_disp]") == 1)
    wait(lambda: count("@e[type=minecraft:armor_stand,tag=le.gdstand]") == 1, 4)
    st = "".join(R(f"data get entity @e[type=minecraft:armor_stand,tag=le.gdstand,limit=1] equipment.{s}.components.\"minecraft:custom_data\"") for s in ("head", "chest", "legs", "feet"))
    chk("the stand wears the 4 pieces of the Creaking armour", st.count("le_creak") == 4, st[:200])
    chk("biome pale_garden in the garden (5 points)", all(passed(f"execute positioned {x} 100 {z} if biome ~ ~ ~ minecraft:pale_garden") for x, z in ((330, -350), (250, -270), (420, -260), (260, -420), (338, -321))))
    chk("not pale_garden outside (30 beyond the west and the north edge)", not passed("execute positioned 200 100 -350 if biome ~ ~ ~ minecraft:pale_garden") and not passed("execute positioned 330 100 -480 if biome ~ ~ ~ minecraft:pale_garden"))
    chk("fade of R1 does not repaint the garden", "pale_garden" not in open(os.path.join(ROOT, "datapack/data/last_ember/function/region/gen/fade_r1.mcfunction")).read())
    unstage()

def open_blooms():
    R("function last_ember:garden/gen/blooms_count"); return gd("#bo")
def t_hearts():
    print("[hearts]"); stage(True, night=True)
    R("function last_ember:garden/reset"); time.sleep(1.2)
    chk("reset: 6 hearts, awake", gd("#left") == 6 and gd("#asleep") == 0)
    # heart 1 at night with Cam near: awake, its creaking comes
    h = HEARTS[0]; x, y, z = h["x"], h["y"], h["z"]
    R(f"tp Cam {x + 6.5} {y + 12} {z + 0.5}"); R(f"execute as Cam at @s run tp @s ~ ~ ~ facing {x} {y} {z}")
    R(f"spreadplayers {x + 6} {z} 0 2 false Cam")
    awake = wait(lambda: blk(x, y, z, "minecraft:creaking_heart[creaking_heart_state=awake]"), 20)
    chk("heart 1 is awake at night", awake, R(f"execute if block {x} {y} {z} minecraft:creaking_heart run say x") )
    cr = wait(lambda: count(f"@e[type=minecraft:creaking,nbt={{home_pos:[I;{x},{y},{z}]}}]") >= 1, 40)
    chk("its creaking comes to the player near it", cr)
    # Cam breaks heart 1 by hand: stand next to it, look at it, hold the attack key
    R(f"clear Cam"); R("item replace entity Cam weapon.mainhand with minecraft:diamond_axe[minecraft:enchantments={efficiency:5}]")
    cx = x + 1.5 if blk(x + 1, y - 1, z, "#minecraft:pale_oak_logs") is False else x + 1.5
    # find a free side: an air cell next to the heart at feet level y-1 with ground under it, or stand on the trunk's root
    side = None
    for ddx, ddz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if blk(x + ddx, y, z + ddz, "#last_ember:garden_air") and blk(x + ddx, y - 1, z + ddz, "#last_ember:garden_air"): side = (ddx, ddz); break
    if side:
        R(f"tp Cam {x + side[0] * 1.0 + 0.5} {y - 1} {z + side[1] * 1.0 + 0.5}")
        R(f"execute as Cam at @s anchored eyes run tp @s ~ ~ ~ facing {x + 0.5} {y + 0.5} {z + 0.5}")
        tc.act("Cam", "!attack_on"); gone = wait(lambda: not blk(x, y, z, "minecraft:creaking_heart"), 12); tc.act("Cam", "!attack_off")
        chk("Cam breaks heart 1 with the axe (real input)", gone)
    else:
        R(f"setblock {x} {y} {z} air destroy"); chk("heart 1: no free side to stand at (broken by command)", False)
    chk("the count follows: 5 left", wait(lambda: gd("#left") == 5, 3), gd("#left"))
    chk("the creaking of heart 1 is gone with it", wait(lambda: count(f"@e[type=minecraft:creaking,nbt={{home_pos:[I;{x},{y},{z}]}}]") == 0, 5))
    chk("storage h1 = 0", "h1: 0b" in R("data get storage last_ember:garden h"))
    R("time set noon")
    for h in HEARTS[1:5]:
        R(f"setblock {h['x']} {h['y']} {h['z']} air destroy")
    chk("4 more broken: 1 left, still awake", wait(lambda: gd("#left") == 1, 3) and gd("#asleep") == 0, (gd("#left"), gd("#asleep")))
    # a sensor creaking that should crumble on the sleep
    R("execute positioned 300 120 -300 run summon minecraft:creaking 300 96 -300 {Tags:[\"le.garden_cr\"],Invulnerable:1b}")
    dx, dy, dz = M["door"]
    h = HEARTS[5]; R(f"setblock {h['x']} {h['y']} {h['z']} air destroy")
    chk("the last heart: the garden falls asleep", wait(lambda: gd("#asleep") == 1, 3))
    chk("sleep: no creaking of a heart left", wait(lambda: count("@e[type=minecraft:creaking,tag=!le.garden_cr]") == 0, 5), count("@e[type=minecraft:creaking]"))
    chk("sleep: the creakings of the sensors crumble", wait(lambda: count("@e[type=minecraft:creaking,tag=le.garden_cr]") == 0, 3))
    chk("sleep: storage asleep 1b", "asleep: 1b" in R("data get storage last_ember:garden"))
    R(f"setblock {dx} {dy} {dz} minecraft:pale_oak_door[facing=north,half=lower,hinge=left,open=true]"); R(f"setblock {dx} {dy+1} {dz} minecraft:pale_oak_door[facing=north,half=upper,hinge=left,open=true]")
    time.sleep(2.2)
    chk("sleep: the door stays open", blk(dx, dy, dz, "minecraft:pale_oak_door[open=true]"))
    R(f"setblock {dx} {dy} {dz} minecraft:pale_oak_door[facing=north,half=lower,hinge=left,open=false]"); R(f"setblock {dx} {dy+1} {dz} minecraft:pale_oak_door[facing=north,half=upper,hinge=left,open=false]")
    # eyeblossoms: open them all, players near -> closed again within 5 s
    R("time set midnight"); R("function last_ember:garden/gen/blooms_open")
    n0 = open_blooms()
    for a, b in (((280, -300), (380, -400)), ((280, -400), (380, -300))):
        R(f"tp Cam {a[0]} 200 {a[1]}"); R(f"tp Cam2 {b[0]} 200 {b[1]}"); time.sleep(6)
    smp = []
    near = [b for b in M["blooms"] if any(math.hypot(b[0] - q[0], b[2] - q[2]) <= 40 for q in (pos("Cam"), pos("Cam2")))]
    for i in range(10): smp.append(sum("passed" in R("execute if block %d %d %d minecraft:open_eyeblossom" % tuple(b)) for b in near)); time.sleep(1.0)
    chk(f"sleep: open eyeblossoms ({n0}) close again, within 40 of the players at most 3 open at a time", n0 > 100 and max(smp) <= 3, (n0, len(near), smp)); print("    near", len(near), "open", smp)
    chk("sleep: a second sleep does not happen (hearts gone, state kept)", gd("#asleep") == 1)
    # reset back to awake
    R("function last_ember:garden/reset"); time.sleep(1.5)
    chk("garden/reset: 6 hearts back, awake", gd("#left") == 6 and gd("#asleep") == 0 and all(blk(h["x"], h["y"], h["z"], "minecraft:creaking_heart") for h in HEARTS))
    R("time set noon"); R("kill @e[type=minecraft:creaking]")
    unstage()

def fstate(f): return gd("#fc") if False else (1 if blk(*face_eye(f), "minecraft:pale_oak_wood") else 0)
def face_eye(f):
    txt = open(os.path.join(ROOT, f"datapack/data/last_ember/function/garden/gen/f/{f['id']}.mcfunction")).read()
    m = re.search(r"if block (-?\d+) (-?\d+) (-?\d+) minecraft:pale_oak_wood", txt); return tuple(int(v) for v in m.groups())
def face_centre(f):
    txt = open(os.path.join(ROOT, f"datapack/data/last_ember/function/garden/gen/f/{f['id']}.mcfunction")).read()
    m = re.search(r"execute positioned (-?[\d.]+) (-?[\d.]+) (-?[\d.]+) as @a", txt); return tuple(float(v) for v in m.groups())
def t_faces():
    print("[faces]"); stage(True)
    R("function last_ember:garden/reset"); time.sleep(1)
    R("tp Cam 330.5 200 -350.5"); R("tp Cam2 335.5 200 -350.5")          # far above: nobody within 24 of a face
    R("time set noon"); time.sleep(2.5)
    chk("day: all 12 faces outward (eyes closed)", wait(lambda: all(fstate(f) == 0 for f in FACES), 4), [fstate(f) for f in FACES])
    R("time set midnight")
    chk("night: all 12 faces turn towards the orangery (eyes open)", wait(lambda: all(fstate(f) == 1 for f in FACES), 4), [fstate(f) for f in FACES])
    # a player looks at face 1 from 10 blocks: day comes, the face holds
    f = FACES[0]; cx, cy, cz = face_centre(f); ox, oz = f["out"]
    lx, lz = cx + ox * 10 + oz * 2, cz + oz * 10 + ox * 2
    R(f"tp Cam {lx} {cy + 20} {lz}"); R(f"spreadplayers {lx} {lz} 0 1 false Cam"); time.sleep(0.3)
    R(f"execute as Cam at @s anchored eyes run tp @s ~ ~ ~ facing {cx} {cy} {cz}")
    R("time set noon"); time.sleep(3)
    chk("day while Cam looks at face 1 from ~10: it holds (still in)", fstate(f) == 1, R("data get entity Cam Pos"))
    R(f"execute as Cam at @s anchored eyes run tp @s ~ ~ ~ facing {cx} {cy} {cz}"); R("execute as Cam at @s run tp @s ~ ~ ~ ~60 ~"); time.sleep(3)
    chk("Cam looks 60 deg aside: it still holds", fstate(f) == 1)
    R("execute as Cam at @s run tp @s ~ ~ ~ ~30 ~")
    chk("Cam looks 90 deg aside: the face turns outward", wait(lambda: fstate(f) == 0, 4))
    R("time set midnight"); wait(lambda: fstate(f) == 1, 4)
    lx, lz = cx + ox * 28, cz + oz * 28
    R(f"tp Cam {lx} {cy + 30} {lz}"); R(f"spreadplayers {lx} {lz} 0 1 false Cam"); time.sleep(0.3)
    R(f"execute as Cam at @s anchored eyes run tp @s ~ ~ ~ facing {cx} {cy} {cz}"); R("time set noon")
    chk("Cam looks at it from ~28 (> 24): it turns all the same", wait(lambda: fstate(f) == 0, 4), R("data get entity Cam Pos"))
    R("time set midnight"); R("tp Cam 330.5 200 -350.5"); wait(lambda: all(fstate(f) == 1 for f in FACES), 4)
    R("function last_ember:garden/sleep_now")
    chk("asleep at night: the faces turn outward, eyes closed", wait(lambda: all(fstate(f) == 0 for f in FACES), 4), [fstate(f) for f in FACES])
    R("function last_ember:garden/reset"); R("time set noon"); time.sleep(1.2)
    unstage()

def sensor_stage(s):
    """Cam 4 blocks from sensor s on the path side, facing it"""
    x, y, z = s["x"], s["y"], s["z"]
    best = min(PATH, key=lambda p: abs(p[0] - x) + abs(p[1] - z) if abs(p[0] - x) + abs(p[1] - z) >= 4 else 99)
    return best
def walk_over(s, sneak=False, t=2.0):
    x, y, z = s["x"], s["y"], s["z"]; sc0 = gd(f"#sc{s['id']}")
    # 3 blocks before the sensor, walk across it
    # the teleport itself is a vibration: hold the sensor's cooldown until it is quiet again, then walk
    R(f"scoreboard players set #sc{s['id']} le.gd 2147483647")
    if sneak: tc.act("Cam", "!sneak_on"); time.sleep(0.4)
    R(f"tp Cam {x + 0.5} {y + 1} {z + 3.5} 180 20")
    wait(lambda: not blk(x, y, z, "minecraft:sculk_sensor[sculk_sensor_phase=active]") and not blk(x, y, z, "minecraft:sculk_sensor[sculk_sensor_phase=cooldown]"), 4, 0.2)
    time.sleep(0.6); R(f"scoreboard players set #sc{s['id']} le.gd {sc0}")
    tc.act("Cam", "!fwd_on"); time.sleep(t); tc.act("Cam", "!fwd_off")
    if sneak: R("tp Cam 330.5 200 -300.5"); time.sleep(0.3); tc.act("Cam", "!sneak_off")      # off the sensor before standing up
def garden_cr(): return count("@e[type=minecraft:creaking,tag=le.garden_cr]")
def t_silence():
    print("[silence]"); stage(False)
    R("function last_ember:garden/reset"); time.sleep(1); R("kill @e[type=minecraft:creaking]")
    s = SENS[6]; x, y, z = s["x"], s["y"], s["z"]                     # a sensor at the orangery: open ground round it
    # sneaking: nothing
    walk_over(s, sneak=True, t=3.0); time.sleep(1.5)
    chk("sneaking over a sensor wakes nothing", garden_cr() == 0 and not blk(x, y, z, "minecraft:sculk_sensor[sculk_sensor_phase=active]"), garden_cr())
    walk_over(s, t=1.6)
    got = wait(lambda: garden_cr() == 2, 4)
    chk("walking over it: 2 creakings", got, garden_cr())
    if got:
        cp = pos("Cam"); ry = float(re.findall(r"(-?[\d.]+)f", R("data get entity Cam Rotation"))[0])
        lx, lz = -math.sin(math.radians(ry)), math.cos(math.radians(ry))
        okd = okb = okt = True
        for i in range(2):
            p = pos(f"@e[type=minecraft:creaking,tag=le.garden_cr,limit=1,sort=nearest,x={x},y={y},z={z}]") if i == 0 else pos(f"@e[type=minecraft:creaking,tag=le.garden_cr,limit=1,sort=furthest,x={x},y={y},z={z}]")
            d = math.dist(p, (x + 0.5, y + 0.5, z + 0.5)); okd &= 10 <= d <= 16
            vx, vz = p[0] - cp[0], p[2] - cp[2]; ang = math.degrees(math.acos(max(-1, min(1, (vx * lx + vz * lz) / max(1e-6, math.hypot(vx, vz))))))
            okb &= ang > 120
        nb = R("data get entity @e[type=minecraft:creaking,tag=le.garden_cr,limit=1] Invulnerable") + R("data get entity @e[type=minecraft:creaking,tag=le.garden_cr,limit=1] PersistenceRequired")
        chk("they stand 10..16 from the sensor", okd)
        chk("they stand behind Cam (> 120 deg from his look)", okb)
        chk("invulnerable and persistent", nb.count("1b") == 2, nb)
    # cooldowns: the same sensor again (60 s), another sensor at once (garden 20 s)
    R("kill @e[type=minecraft:creaking]"); time.sleep(1.5)
    walk_over(s, t=1.6); time.sleep(2)
    chk("the same sensor again at once: nothing (garden and sensor cooldown)", garden_cr() == 0, garden_cr())
    R("scoreboard players set #gcd le.gd 0"); walk_over(s, t=1.6); time.sleep(2)
    chk("garden cooldown cleared, sensor cooldown (60 s) holds", garden_cr() == 0, garden_cr())
    s2 = SENS[7]; walk_over(s2, t=1.6)
    chk("another sensor at once: 2 creakings (its own cooldown free)", wait(lambda: garden_cr() == 2, 4), garden_cr())
    # crumble after 60 s: make them old
    R("execute store result score #now le.gd run time query gametime")
    R("scoreboard players operation @e[type=minecraft:creaking,tag=le.garden_cr] le.gdt = #now le.gd")
    chk("60 s later they crumble", wait(lambda: garden_cr() == 0, 3))
    # nobody near -> crumble
    R("scoreboard players set #gcd le.gd 0"); R(f"scoreboard players set #sc{SENS[8]['id']} le.gd 0"); walk_over(SENS[8], t=1.6)
    wait(lambda: garden_cr() == 2, 4)
    R("tp Cam 100 200 -100"); R("gamemode spectator Cam")
    chk("all players leave the garden (+32): they crumble", wait(lambda: garden_cr() == 0, 3))
    R("gamemode survival Cam")
    # the limit: 8 sensor creakings summoned -> 6 stay
    R("tp Cam 330.5 95 -300.5")
    for i in range(8): R(f"summon minecraft:creaking {300 + i} 100 -280 {{Tags:[\"le.garden_cr\"],Invulnerable:1b}}")
    R("execute store result score #now le.gd run time query gametime"); R("scoreboard players add #now le.gd 1200")
    R("scoreboard players operation @e[type=minecraft:creaking,tag=le.garden_cr] le.gdt = #now le.gd")
    chk("never more than 6 creakings in the garden", wait(lambda: count("@e[type=minecraft:creaking,x=214,y=30,z=-466,dx=232,dy=200,dz=232]") == 6, 3), count("@e[type=minecraft:creaking]"))
    # 6 in the garden -> a sensor wakes nobody
    R("scoreboard players set #gcd le.gd 0"); R(f"scoreboard players set #sc{SENS[9]['id']} le.gd 0"); walk_over(SENS[9], t=1.6); time.sleep(2)
    chk("with 6 creakings a sensor adds none", count("@e[type=minecraft:creaking]") == 6)
    R("kill @e[type=minecraft:creaking]")
    # asleep: sensors are quiet
    R("function last_ember:garden/sleep_now"); R("scoreboard players set #gcd le.gd 0"); R(f"scoreboard players set #sc{SENS[6]['id']} le.gd 0")
    walk_over(SENS[6], t=1.6); time.sleep(2)
    chk("asleep: a sensor wakes nothing", garden_cr() == 0)
    R("function last_ember:garden/reset"); unstage()

def inv(p):
    R(f"execute store result score #ni le.gd run data get entity {p} Inventory"); return "".join(R(f"data get entity {p} Inventory[{i}]") for i in range(gd("#ni") or 0))
def look_at(p, x, y, z): R(f"execute as {p} at @s anchored eyes run tp @s ~ ~ ~ facing {x} {y} {z}")
def t_key():
    print("[key]"); stage(False)
    R("function last_ember:garden/reset"); R("clear Cam"); time.sleep(1.2)
    kx, ky, kz = M["key"]
    # Call target before the key (chapter 1 keys: the others found? use the function directly)
    R("data modify storage last_ember:keys k.thread_labyrinth.got set value 1b")
    R("data modify storage last_ember:keys k.signet_king.got set value 1b"); R("data modify storage last_ember:keys k.crown_witches.got set value 1b")
    R("scoreboard players set #best le.alt 2147483647"); R("execute store result score #px le.alt run data get entity Cam Pos[0]"); R("execute store result score #pz le.alt run data get entity Cam Pos[2]")
    R("function last_ember:altar/gen/call_tear_creaker")
    chk("Call before the key -> the pedestal of the orangery", tc.score("#tx", "le.alt") == kx and tc.score("#tz", "le.alt") == kz)
    R(f"tp Cam {kx + 0.5} {ky} {kz + 2.5}"); look_at("Cam", kx + 0.5, ky + 0.5, kz + 0.5); time.sleep(0.4)
    tc.act("Cam", "!use"); time.sleep(1.0)
    chk("right click takes the key", "le_key" in inv("Cam") and "tear_creaker" in inv("Cam"), inv("Cam")[:200])
    chk("the pedestal is empty", count("@e[tag=le.gdkey]") == 0 and count("@e[tag=le.gdkey_disp]") == 0)
    time.sleep(2.2)
    chk("... and stays empty (a second later)", count("@e[tag=le.gdkey]") == 0 and gd("#key") == 2)
    chk("storage: got 1b (Call no longer leads here)", "got: 1b" in R("data get storage last_ember:keys k.tear_creaker"))
    chk("hearts untouched by the key", gd("#left") == 6 and gd("#asleep") == 0)
    # carry it to the Circle of the Weepers: the pedestal of tear_creaker (-411 111 -180)
    R("forceload add -420 -190 -400 -170"); R("tp Cam -411.5 112 -177.5"); time.sleep(2)
    look_at("Cam", -410.5, 111.9, -179.5); time.sleep(0.3)
    tc.act("Cam", "!use"); time.sleep(1.2)
    st = R("data get storage last_ember:keys k.tear_creaker.st")
    chk("the key carried to the Circle: its pedestal takes it", "1" in st.split(":")[-1] and "tear_creaker" not in inv("Cam"), st)
    # take it back off (empty hand)
    tc.act("Cam", "!use"); time.sleep(1.0)
    chk("... and gives it back to an empty hand", "tear_creaker" in inv("Cam"))
    R("forceload remove -420 -190 -400 -170")
    R("clear Cam"); R("function last_ember:garden/reset"); unstage()

def attr(p, a): return tc.num(R(f"attribute {p} minecraft:{a} get"), r"is (-?[\d.]+)")
def t_armor():
    print("[armor]"); stage(True)
    R("function last_ember:garden/reset"); R("clear Cam"); R("clear Cam2"); time.sleep(1.2)
    sx, sy, sz = M["stand"]
    R("tp Cam 242.5 121 -271.5"); R("tp Cam2 242.5 121 -272.5")
    look_at("Cam", sx + 0.5, sy + 1.0, sz + 0.5); time.sleep(0.4); tc.act("Cam", "!use"); time.sleep(0.8)
    chk("before the sleep: the stand gives nothing", "le_creak" not in inv("Cam"))
    R("function last_ember:garden/sleep_now"); time.sleep(0.5)
    tc.act("Cam", "!use"); time.sleep(0.8)
    chk("after the sleep: a full set (4 pieces)", inv("Cam").count("le_creak") == 4, inv("Cam")[:300])
    tc.act("Cam", "!use"); time.sleep(0.8)
    chk("a second click: no second set", inv("Cam").count("le_creak") == 4)
    look_at("Cam2", sx + 0.5, sy + 1.0, sz + 0.5); time.sleep(0.4); tc.act("Cam2", "!use"); time.sleep(0.8)
    chk("Cam2 gets his own set", inv("Cam2").count("le_creak") == 4)
    st = "".join(R(f"data get entity @e[type=minecraft:armor_stand,tag=le.gdstand,limit=1] equipment.{s}.components.\"minecraft:custom_data\"") for s in ("head", "chest", "legs", "feet"))
    chk("the stand keeps its pieces", st.count("le_creak") == 4)
    R("clear Cam"); R("loot give Cam loot last_ember:item/creaking_armor")
    for sl, pc in (("head", "helmet"), ("chest", "chestplate"), ("legs", "leggings"), ("feet", "boots")):
        R(f"loot replace entity Cam armor.{sl} loot last_ember:item/creaking_{pc}")
    time.sleep(0.3)
    a, t, k = attr("Cam", "armor"), attr("Cam", "armor_toughness"), attr("Cam", "knockback_resistance")
    chk("worn: armour 15, toughness 0, knockback resistance 0.1", a == 15 and t == 0 and abs(k - 0.1) < 1e-6, (a, t, k))
    it = R("data get entity Cam equipment.chest.components")
    chk("chestplate: max damage 240, enchantable 12, repairable pale oak logs, name, lore",
        "240" in it and "enchantable" in it and "pale_oak_logs" in it and "Скрипучая броня" in it and "помнит" in it, it[:400])
    du = [tc.num(R(f"data get entity Cam equipment.{s}.components.\"minecraft:max_damage\""), r"(\d+)$") for s in ("head", "chest", "legs", "feet")]
    chk("durability 165 / 240 / 225 / 195", du == [165, 240, 225, 195], du)
    chk("not in #metal_gear", "creaking" not in open(os.path.join(ROOT, "datapack/data/last_ember/tags/item/metal_gear.json")).read())
    R("kill Cam"); time.sleep(3)
    chk("death keeps the worn armour", "".join(R(f"data get entity Cam equipment.{s}.components.\"minecraft:custom_data\"") for s in ("head", "chest", "legs", "feet")).count("le_creak") == 4)
    R("clear Cam"); R("clear Cam2"); R("function last_ember:garden/reset"); unstage()

def arena():
    R("fill 1700 199 1700 1740 199 1740 minecraft:stone"); R("fill 1700 200 1700 1740 206 1740 minecraft:air")
    R("forceload add 1700 1700 1740 1740")
def wear(p):
    R(f"clear {p}")
    for sl, pc in (("head", "helmet"), ("chest", "chestplate"), ("legs", "leggings"), ("feet", "boots")):
        R(f"loot replace entity {p} armor.{sl} loot last_ember:item/creaking_{pc}")
def husk(x, z, tag="t"):
    R(f"summon minecraft:husk {x} 200 {z} {{Tags:[\"le.keep\",\"le.st_{tag}\",\"le.noelite\"],NoAI:1b,PersistenceRequired:1b}}")
def slowed(tag):
    r = R(f"data get entity @e[tag=le.st_{tag},limit=1] active_effects"); return "slowness" in r and "amplifier: 2b" in r and "weakness" in r
def clear_t(): R("kill @e[type=minecraft:husk,x=1700,y=190,z=1700,dx=40,dy=20,dz=40]"); R("kill @e[type=minecraft:zombie,x=1700,y=190,z=1700,dx=40,dy=20,dz=40]")
def t_still():
    print("[still: the Stillness of the full set]"); stage(False); arena(); time.sleep(1)
    tc.setc(1, 1, 0, "Cam"); wear("Cam"); R("difficulty hard")
    R("tp Cam 1710.5 200 1720.5 -90 0")                                # looks to +x
    clear_t(); husk(1718.5, 1720.5, "a"); time.sleep(1.0)
    chk("husk at 8 in the look: slowness III + weakness I", slowed("a"))
    clear_t(); husk(1719.6, 1720.5, "a"); time.sleep(1.0)
    chk("husk at 9: nothing", not slowed("a"))
    R("tp Cam 1710.5 200 1720.5 -60 0"); clear_t(); husk(1716.5, 1720.5, "a"); time.sleep(1.0)
    chk("husk at 6 but 30 deg aside: nothing", not slowed("a"))
    R("tp Cam 1710.5 200 1720.5 -90 0")
    clear_t(); R("fill 1714 200 1718 1714 203 1723 minecraft:stone"); husk(1717.5, 1720.5, "a"); time.sleep(1.0)
    chk("husk at 7 behind a wall: nothing", not slowed("a"))
    R("fill 1714 200 1718 1714 203 1723 minecraft:air")
    clear_t(); R("fill 1714 200 1718 1714 200 1723 minecraft:tall_grass"); husk(1717.5, 1720.5, "a"); time.sleep(1.0)
    chk("husk at 7 behind grass and a carpet: stilled", slowed("a"))
    R("fill 1714 200 1718 1714 201 1723 minecraft:air")
    clear_t(); husk(1714.5, 1720.5, "a"); husk(1717.5, 1720.5, "b"); time.sleep(1.0)
    chk("two in the look: only the nearest", slowed("a") and not slowed("b"))
    for tg in ("le.boss", "le.giant", "le.npc"):
        clear_t(); husk(1716.5, 1720.5, "a"); R(f"tag @e[tag=le.st_a] add {tg}"); time.sleep(1.0)
        chk(f"a {tg} husk: nothing", not slowed("a"))
    clear_t(); R("summon minecraft:creaking 1716.5 200 1720.5 {Tags:[\"le.st_a\",\"le.keep\"],NoAI:1b}"); time.sleep(1.0)
    chk("a creaking: nothing", not slowed("a"))
    R("kill @e[type=minecraft:creaking,tag=le.st_a]")
    clear_t(); R("item replace entity Cam armor.head with minecraft:leather_helmet"); husk(1716.5, 1720.5, "a"); time.sleep(1.0)
    chk("three pieces only: nothing", not slowed("a"))
    tc.setc(2, 1, 0, "Cam"); wear("Cam"); R("tp Cam 1710.5 200 1720.5 -90 0")
    clear_t(); husk(1722.5, 1720.5, "a"); time.sleep(1.0)
    chk("elf: husk at 12 stilled", slowed("a"))
    R("tp Cam 1710.5 200 1720.5 -67 0"); clear_t(); husk(1718.5, 1720.5, "a"); time.sleep(1.0)
    chk("elf: 23 deg aside stilled (cone 25)", slowed("a"))
    R("tp Cam 1710.5 200 1720.5 -60 0"); clear_t(); husk(1718.5, 1720.5, "a"); time.sleep(1.0)
    chk("elf: 30 deg aside: nothing", not slowed("a"))
    tc.setc(1, 1, 0, "Cam"); clear_t(); R("clear Cam"); R("forceload remove 1700 1700 1740 1740"); unstage()

def t_zones():
    print("[zones]"); stage(False)
    R("tp Cam 338.5 92 -312.5"); time.sleep(1.2)
    chk("in the orangery: adventure (blocks cannot be broken)", "adventure" in R("data get entity Cam playerGameType") or passed("execute if entity @a[name=Cam,gamemode=adventure]"))
    R("tp Cam 242.5 121 -264.5"); time.sleep(1.2)
    R("tp Cam 243.5 121 -272.5"); time.sleep(1.2)
    chk("in the house: adventure", passed("execute if entity @a[name=Cam,gamemode=adventure]"))
    R("summon minecraft:zombie 241.5 121 -271.5 {PersistenceRequired:1b}"); time.sleep(2.2)
    chk("a monster in the house is removed (no_spawn)", count("@e[type=minecraft:zombie,x=236,y=117,z=-277,dx=12,dy=15,dz=10]") == 0)
    R("tp Cam 290.5 120 -300.5"); R("spreadplayers 290 -300 0 1 false Cam"); time.sleep(1.2)
    chk("out in the garden: survival again", passed("execute if entity @a[name=Cam,gamemode=survival]"))
    unstage()

tm = None
def tmz():
    global tm
    if tm is None:
        sp = importlib.util.spec_from_file_location("tmz", os.path.join(ROOT, "tools/test_maze.py")); tm = importlib.util.module_from_spec(sp)
        src = open(os.path.join(ROOT, "tools/test_maze.py")).read(); src = src[:src.index("\nT = {\"layout\"")]       # the helpers only
        exec(compile(src, "test_maze", "exec"), tm.__dict__)
    return tm
def t_perf():
    print("[perf]"); stage(True)
    R("function last_ember:garden/reset"); wear("Cam"); wear("Cam2")
    R("tp Cam 300.5 120 -300.5"); R("spreadplayers 300 -300 0 1 false Cam"); R("tp Cam2 320.5 120 -330.5"); R("spreadplayers 320 -340 0 1 false Cam2")
    for i in range(6): R(f"summon minecraft:husk {300 + i} 120 -305 {{Tags:[\"le.keep\",\"le.gperf\"],PersistenceRequired:1b}}")
    R("spreadplayers 302 -306 0 4 false @e[type=minecraft:husk,tag=le.gperf]")
    R("execute as Cam at @s run tp @s ~ ~ ~ facing entity @e[tag=le.gperf,limit=1,sort=nearest] eyes")
    time.sleep(3)
    def walk():
        tc.act("Cam2", "!fwd_on"); time.sleep(4); tc.act("Cam2", "!fwd_off")
    m = tmz(); p0 = m.prof(10, walk)
    g = sum(v for k, v in p0.items() if k.startswith("last_ember:garden/loop")); c = p0.get("last_ember:creak/wear", 0)
    print(f"     profiler: garden/loop {g:.3f} ms per tick (all of it: 2 wearers of the full set, 6 husks near, sensors, faces, hearts), tick {p0.get('tick', 0):.1f} ms")
    for k, v in sorted(p0.items(), key=lambda kv: -kv[1])[:8]: print(f"       {k} {v:.3f}")
    chk("garden/loop (with the Stillness of 2 wearers) under 0.2 ms per tick", 0 < g < 0.2, p0)
    R("kill @e[type=minecraft:husk,tag=le.gperf]"); R("clear Cam"); R("clear Cam2"); unstage()

def t_restart():
    print("[restart]"); stage(False)
    R("function last_ember:garden/reset"); time.sleep(1)
    h = HEARTS[2]; R(f"setblock {h['x']} {h['y']} {h['z']} air destroy"); time.sleep(1.5)
    kx, ky, kz = M["key"]; R("clear Cam"); R(f"tp Cam {kx + 0.5} {ky} {kz + 2.5}"); look_at("Cam", kx + 0.5, ky + 0.5, kz + 0.5); time.sleep(0.4); tc.act("Cam", "!use"); time.sleep(1)
    s0 = (gd("#left"), gd("#asleep"), gd("#key")); R("tag Cam add le.creak_got")
    tmz().restart(); stage(False)
    chk("after a restart: 5 hearts, awake, key taken", (gd("#left"), gd("#asleep"), gd("#key")) == s0 == (5, 0, 2), (s0, (gd("#left"), gd("#asleep"), gd("#key"))))
    time.sleep(2)
    chk("... the pedestal stays empty, the stand stands", count("@e[tag=le.gdkey]") == 0 and count("@e[type=minecraft:armor_stand,tag=le.gdstand]") == 1)
    R("function last_ember:garden/sleep_now"); time.sleep(0.5)
    tmz().restart(); stage(False)
    chk("after a restart: still asleep", gd("#asleep") == 1 and "asleep: 1b" in R("data get storage last_ember:garden"))
    dx, dy, dz = M["door"]; R(f"setblock {dx} {dy} {dz} minecraft:pale_oak_door[facing=north,half=lower,hinge=left,open=true]"); R(f"setblock {dx} {dy+1} {dz} minecraft:pale_oak_door[facing=north,half=upper,hinge=left,open=true]"); time.sleep(2.2)
    chk("... the door stays open", blk(dx, dy, dz, "minecraft:pale_oak_door[open=true]"))
    R(f"setblock {dx} {dy} {dz} minecraft:pale_oak_door[facing=north,half=lower,hinge=left,open=false]"); R(f"setblock {dx} {dy+1} {dz} minecraft:pale_oak_door[facing=north,half=upper,hinge=left,open=false]")
    R("scoreboard players reset * le.gd"); R("reload"); time.sleep(2)
    chk("scores lost (reset *) -> taken back from the storage", gd("#asleep") == 1 and gd("#key") == 2 and gd("#left") == 5, (gd("#asleep"), gd("#key"), gd("#left")))
    R("clear Cam"); R("tag Cam remove le.creak_got"); R("function last_ember:garden/reset"); unstage()

T = dict(build=t_build, hearts=t_hearts, faces=t_faces, silence=t_silence, key=t_key, armor=t_armor, still=t_still, zones=t_zones, perf=t_perf, restart=t_restart)
if __name__ == "__main__":
    for n in (sys.argv[1:] or [k for k in T if k != "restart"]): T[n]()
    print(f"\n{ok} ok, {bad} failed")
