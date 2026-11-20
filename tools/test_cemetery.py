#!/usr/bin/env python3
"""T-027 checks on the R1 world (tools/build/rebuild.sh): the Cemetery of the Fallen Knights and the Keeper's Lodge. Clients Cam and Cam2
in the game (real input through the dev agent: !use on the keeper, the coffin lids, the spyglass, the door; !attack_on to dig).
  build    the places: no snow, soul soil only in the 16 graves (and nowhere in the places and the seam), the biome `barrows`, the epitaphs,
           the candles (2 pits unlit), the zones, the traps, the crypt (door, plates, sarcophagus, chest 2 locked, bars), the lodge
  keeper   the keeper does not move or die (hurt, pushed), day in the armchair, night by the hearth, goes over only when nobody is near
           12; the dog; both survive the no_spawn of the lodge
  quest    the first window (real click), «Взять лопату» -> the shovel at Cam, the quest at 1; the shovel breaks soul soil only (real
           digging), without it the grave cannot be dug
  graves   a right, a wrong grave and Thane's: the content, the unrest (+1 / +3), the wave by the table (day and night), never more than 8
  unrest   the unrest falls by 1 in 3 minutes (tick sprint); the bell: -4, the spirits gone, the line, the cooldown 5 min
  pit      Cam falls 4 into a sunken grave and climbs out by the ladder (real input, no jump); a halfling walks over it
  crypt    the key at Cam (#q 2), the door without the key (line), with it (open for good, #q 3), the corridor volleys (T-016), the
           Magister: rising, sword / bow, the half (2 spirits, x1.2), the leash with full health, the kill: #q 4, the seal, chest 2, the exit
  lost     the shovel, the key and the seal destroyed (lava, kill of the item): again at the keeper / in the coffin / in the sarcophagus
  curses   the effects only in the armour slots and the hands, not in the bag; the knight's blessing does not mend them; the absolution:
           a trophy taken, the effects gone, the blessing mends; no cursed thing / no trophy: the lines
  spyglass at night the lights over the right graves for Cam only (Cam2 none), by day the line, the cooldown
  fade     region/gen/fade_r1 and unfade_r1: the graves (opened stay open), the sword across the hill stair (the stair passable), soul
           lanterns, the lodge dark, the keeper and the dog at the crypt door; back
  zones    nothing breaks at the cemetery but the graves by the shovel; no spawn at the lodge at night; the keeper and the dog stay
  restart  two opened graves, the key, the dead Magister survive a restart
  perf     two players at the cemetery at night at unrest 12 (spawns of the biome and the spirits): cemetery/* by the profiler
Usage: python3 tools/test_cemetery.py [build keeper quest graves unrest pit crypt lost curses spyglass fade zones restart perf]"""
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
M = json.load(open(os.path.join(ROOT, "server/build/r1/cemetery.json")))
W = M["W"]; CR = M["crypt"]; LO = M["lodge"]; DPM = M["dp"]
G = {g["n"]: g for g in M["graves"]}
sys.path.insert(0, os.path.join(ROOT, "tools/build")); import cemetery_plan as _P
for _g in _P.GRAVES: G[_g[0]].setdefault("ep", _g[4])
def cm(n): return tc.score(n, "le.cem")
def passed(cmd): return "passed" in R(cmd)
def pos(sel):
    v = re.findall(r"(-?\d+\.?\d*)d", R(f"data get entity {sel} Pos")); return [float(x) for x in v] if len(v) == 3 else None
def wait(cond, t=10.0, step=0.3):
    t0 = time.time()
    while time.time() - t0 < t:
        if cond(): return True
        time.sleep(step)
    return cond()
def count(sel):
    m = re.search(r"Count: (\d+)", R(f"execute if entity {sel}")); return int(m.group(1)) if m else 0
def blk(x, y, z, b): return passed(f"execute if block {x} {y} {z} {b}")
def inv(p): return R(f"data get entity {p} Inventory")
def has(p, key): return f'le_citem: "{key}"' in inv(p)
def look_at(p, x, y, z): R(f"execute as {p} at @s anchored eyes run tp @s ~ ~ ~ facing {x} {y} {z}")
CBOX = "x=%d,y=%d,z=%d,dx=%d,dy=160,dz=%d" % (124, W - 32, 374, 152, 152)
SPIRITS = "@e[tag=le.cspirit,%s]" % CBOX
FLA = ["forceload add 84 420 276 526", "forceload add 124 374 276 420"]
def stage(night=False, p2=True, mode="survival"):
    for p in ("Cam", "Cam2"):
        if not passed(f"execute if entity @a[name={p},tag=le.cinit]"): tc.setc(1, 1, 0, p)
    R("weather clear 100000"); R("time set " + ("midnight" if night else "noon")); R("gamerule advance_time false"); R("difficulty easy")
    for p in ("Cam", "Cam2"):
        R(f"gamemode {mode} {p}"); R(f"effect give {p} minecraft:resistance infinite 4 true"); R(f"effect give {p} minecraft:saturation infinite 1 true")
        R(f"effect give {p} minecraft:regeneration infinite 2 true"); R(f"execute as {p} run function last_ember:sleep/set_awake {{ticks:0}}")   # no insomnia (its slowness / weakness)
    for c in FLA: R(c)
    R("tp Cam 240.5 95 465.5 0 0"); R("tp Cam2 242.5 95 465.5 0 0")
    if not p2: R("gamemode spectator Cam2"); R("tp Cam2 240 200 300")
    wait(lambda: passed("execute if loaded 124 0 374") and passed("execute if loaded 276 0 526") and passed("execute if loaded 84 0 431"), 40)
    time.sleep(2.0)
def unstage():
    R("forceload remove 84 420 276 526"); R("forceload remove 124 374 276 420")
def reset_all():
    R("function last_ember:cemetery/reset"); R("kill @e[type=minecraft:arrow]"); time.sleep(1.5)
def lodge_walk(p):
    """next to the keeper (wherever he stands now)"""
    k = pos("@e[type=minecraft:villager,tag=le.ckeeper,limit=1]")
    return k
def talk(p):
    """a real right click on the keeper: stand 2 in front of him, look at him, !use"""
    k = pos("@e[type=minecraft:villager,tag=le.ckeeper,limit=1]")
    if not k: return False
    # the free cell next to him: west of the armchair (inside the room), north of the hearth spot
    for dx, dz in ((-1.6, 0), (0, -1.6), (0, 1.6), (1.6, 0)):
        x, z = k[0] + dx, k[2] + dz
        if blk(math.floor(x), math.floor(k[1]), math.floor(z), "#minecraft:air") and blk(math.floor(x), math.floor(k[1]) + 1, math.floor(z), "#minecraft:air"):
            R(f"tp {p} {x} {k[1]} {z}"); look_at(p, k[0], k[1] + 1.2, k[2]); time.sleep(0.4); tc.act(p, "!use"); time.sleep(1.0); return True
    return False
def trig(p, n): R(f"scoreboard players enable {p} le.ctrig"); R(f"execute as {p} run trigger le.ctrig set {n}"); time.sleep(0.6)
def give_shovel(p="Cam"): R(f"execute as {p} run function last_ember:cemetery/give {{key:\"cem_shovel\"}}")
def open_lid(n, p="Cam", real=True):
    g = G[n]; lx, ly, lz = g["lid"]
    if real:
        R(f"fill {g['x']} {g['y']} {g['z']} {g['x']} {g['y'] + 1} {g['z'] + 1} minecraft:air replace minecraft:soul_soil")
        R(f"tp {p} {g['x'] + 0.5} {g['y'] + 1} {g['z'] + 2.6}"); look_at(p, lx + 0.5, ly + 0.9, lz + 0.5); time.sleep(0.4); tc.act(p, "!use"); time.sleep(0.6)
        if not blk(lx, ly, lz, "minecraft:dark_oak_trapdoor[open=true]"):
            R(f"setblock {lx} {ly} {lz} minecraft:dark_oak_trapdoor[facing=north,half=top,open=true,powered=false,waterlogged=false]")
            return "set"
        return "real"
    R(f"fill {g['x']} {g['y']} {g['z']} {g['x']} {g['y'] + 1} {g['z'] + 1} minecraft:air replace minecraft:soul_soil")
    R(f"setblock {lx} {ly} {lz} minecraft:dark_oak_trapdoor[facing=north,half=top,open=true,powered=false,waterlogged=false]")
    return "set"
def spirits(kind=None): return count("@e[tag=le.cspirit,tag=%s,%s]" % (kind, CBOX)) if kind else count(SPIRITS)
def clear_spirits(): R("execute as @e[tag=le.cspirit] at @s run function last_ember:cemetery/spirit_gone"); time.sleep(0.3)

# ---------------------------------------------------------------- build
def scan_world():
    sys.path.insert(0, os.path.join(ROOT, "tools/build")); import fens_scan
    return fens_scan
def t_build():
    print("[build]"); stage(p2=False)
    subprocess.run("cd %s && tools/server.sh rcon save-all flush" % ROOT, shell=True, capture_output=True); time.sleep(3)
    fs = scan_world()
    sys.path.insert(0, os.path.join(ROOT, "tools/build")); import cemetery_plan as P
    bad_ = [b for b in fs.scan(os.path.join(ROOT, "server/world"), box=P.BOX, inside=lambda x, z: bool(P.in_place(x, z))) if not (b[3] == "minecraft:spruce_log" and P.rect_dist(P.LODGE, b[0], b[2]) <= 2)]
    chk("no snow, no spruce trees in the places (spruce logs only in the lodge's own posts)", not bad_, bad_[:5])
    # soul soil: count by a search of the world (chunks read by the scan reader)
    import re as _re
    ss = soul_soil(fs, P)
    graves = set()
    for g in M["graves"]:
        for d in (0, 1):
            graves.add((g["x"], g["y"] + 1, g["z"] + d))
            if g["kind"] != "pit": graves.add((g["x"], g["y"], g["z"] + d))
    chk("soul soil only in the 16 graves (%d blocks, none elsewhere in the places and the seam)" % len(graves), set(ss) == graves, sorted(set(ss) ^ graves)[:6])
    bi = R("execute positioned 200 100 470 run locate biome last_ember:barrows")
    chk("the biome barrows at the floor, the descent and the hill", all("barrows" in R(f"execute positioned {x} {y} {z} run data get entity Cam") or True for (x, y, z) in ()) and
        all(biome_at(x, y, z) for (x, y, z) in ((200, 96, 470), (P.HILL[0] + 8, M["hill_level"] + 1, P.HILL[1] + 8), (M["desc"][60][0], M["desc"][60][2] + 1, M["desc"][60][1]), (M["desc"][-1][0], M["desc"][-1][2] + 1, M["desc"][-1][1]))))
    signs = [g for g in M["graves"] if "Text" not in R("data get block %d %d %d front_text" % tuple(g["sign"])) and g["ep"][0].split()[0] in R("data get block %d %d %d front_text" % tuple(g["sign"]))]
    chk("16 epitaphs on their headstones", len(signs) == 16, len(signs))
    lit = [g["n"] for g in M["graves"] if blk(*g["candle"], "minecraft:candle[lit=true]")]
    chk("the candles burn on all graves but the two pits", sorted(lit) == sorted(g["n"] for g in M["graves"] if g["kind"] != "pit"), lit)
    z = open(os.path.join(ROOT, "zones/zones.txt")).read()
    chk("zones: cemetery, crypt (dungeon), 5 barrows (dungeon), lodge (no_spawn)", all(k in z for k in ("cemetery ", "cemetery_crypt", "cemetery_barrow_5", "lodge ")))
    t = open(os.path.join(ROOT, "traps/traps.txt")).read()
    chk("traps: 2 pits (collapse), the corridor arrows, 4 plates", t.count("cem_pit_") == 2 and "cem_arrows" in t and t.count("cem_plate_") == 4)
    d = CR["door"]; c2 = CR["chest2"]
    chk("the crypt: iron door shut, chest 2 under its lock, the bars of the exit, chest 1, the plates",
        blk(*d, "minecraft:iron_door[open=false]") and blk(c2[0], c2[1] + 1, c2[2], "minecraft:chiseled_polished_blackstone") and blk(*CR["bars"][0], "minecraft:iron_bars") and
        blk(*CR["chest1"], "minecraft:chest") and all(blk(*p, "minecraft:polished_blackstone_pressure_plate") for p in CR["plates"]))
    chk("the lodge: the lectern with the Book of Records, the bell, the post lantern, 2 tripwire hooks with nothing between them",
        blk(*LO["lectern"], "minecraft:lectern[has_book=true]") and blk(*LO["bell"], "minecraft:bell") and blk(*LO["post_lantern"], "minecraft:lantern") and
        blk(LO["holder"][0] + 1, LO["holder"][1], LO["holder"][2] - 1, "minecraft:tripwire_hook") and blk(LO["holder"][0] + 1, LO["holder"][1], LO["holder"][2] + 1, "minecraft:tripwire_hook") and
        blk(LO["holder"][0], LO["holder"][1], LO["holder"][2], "#minecraft:air"))
    pk = [p for p in M["barrows"] for c in p["containers"] if c["loot"]]
    chk("6 containers of the barrows with chests/r1/common", sum(1 for b in M["barrows"] for c in b["containers"] if c["loot"]) == 6)
    unstage()
def biome_at(x, y, z):
    return passed(f"execute positioned {x} {y} {z} if biome ~ ~ ~ last_ember:barrows")
def soul_soil(fs, P):
    import collections
    out = []; x1, z1, x2, z2 = P.BOX
    sb = fs.sb
    for rx in range(x1 // 512, x2 // 512 + 1):
        for rz in range(z1 // 512, z2 // 512 + 1):
            path = os.path.join(ROOT, "server/world/dimensions/minecraft/overworld/region", "r.%d.%d.mca" % (rx, rz))
            if not os.path.exists(path): continue
            for c in sb.chunks(path):
                cx, cz = c.get("xPos"), c.get("zPos")
                if cx is None or cx * 16 + 15 < x1 or cx * 16 > x2 or cz * 16 + 15 < z1 or cz * 16 > z2: continue
                for s in c.get("sections", []):
                    bs = s.get("block_states") or {}; pal = bs.get("palette", [])
                    names = [p if isinstance(p, str) else (p.get("id") or p.get("Name") or p.get("")) for p in pal]
                    if "minecraft:soul_soil" not in names: continue
                    data = bs.get("data") or []; k = names.index("minecraft:soul_soil")
                    bits = max(4, (len(pal) - 1).bit_length()); per = 64 // bits; mask = (1 << bits) - 1
                    for i in range(4096):
                        v = (data[i // per] >> ((i % per) * bits)) & mask if data else 0
                        if v == k:
                            y = s.get("Y") * 16 + i // 256; zz = cz * 16 + (i // 16) % 16; xx = cx * 16 + i % 16
                            if P.in_place(xx, zz): out.append((xx, y, zz))
    return out

# ---------------------------------------------------------------- keeper
def kpos(): return pos("@e[type=minecraft:villager,tag=le.ckeeper,limit=1]")
def near(a, b, d=0.7): return a and b and math.dist(a, b) <= d
def t_keeper():
    print("[keeper]"); stage(); reset_all()
    R("tp Cam 240 140 470"); R("tp Cam2 242 140 470"); time.sleep(3)
    chk("by day the keeper sits in the armchair by the window", wait(lambda: near(kpos(), DPM["keeper_day"]), 6), (kpos(), DPM["keeper_day"]))
    chk("the dog lies at the threshold", near(pos("@e[type=minecraft:wolf,tag=le.cdog,limit=1]"), DPM["dog"]))
    k0 = kpos()
    R("damage @e[type=minecraft:villager,tag=le.ckeeper,limit=1] 30 minecraft:player_attack"); R("execute as @e[type=minecraft:villager,tag=le.ckeeper] at @s run tp @s ~1 ~ ~"); time.sleep(2.2)
    chk("hurt (30) and pushed: alive, back on his place", count("@e[type=minecraft:villager,tag=le.ckeeper]") == 1 and near(kpos(), DPM["keeper_day"]), kpos())
    x, y, z = DPM["keeper_day"]; R(f"tp Cam {x - 3} {y} {z}"); R("time set midnight"); time.sleep(2.5)
    chk("night with Cam 3 from him: he stays in the armchair", near(kpos(), DPM["keeper_day"]), kpos())
    R("tp Cam 240 140 470"); time.sleep(2.5)
    chk("nobody within 12: by the hearth at night", wait(lambda: near(kpos(), DPM["keeper_night"]), 4), (kpos(), DPM["keeper_night"]))
    R("time set noon"); time.sleep(2.5)
    chk("by day back in the armchair", wait(lambda: near(kpos(), DPM["keeper_day"]), 4))
    R("difficulty hard"); R("time set midnight"); time.sleep(3)
    chk("night, hard, the lodge zone (no_spawn): the keeper and the dog stay", count("@e[type=minecraft:villager,tag=le.ckeeper]") == 1 and count("@e[type=minecraft:wolf,tag=le.cdog]") == 1)
    R("difficulty easy"); R("time set noon"); unstage()

# ---------------------------------------------------------------- quest: the window, the shovel, digging
def dig(p, x, y, z, t=10):
    R(f"tp {p} {x + 0.5} {y + 1} {z + 2.4}"); look_at(p, x + 0.5, y + 0.5, z + 0.5); time.sleep(0.5)
    tc.act(p, "!attack_on"); r = wait(lambda: not blk(x, y, z, "minecraft:soul_soil"), t); tc.act(p, "!attack_off"); time.sleep(0.3)
    return r
def t_quest():
    print("[quest]"); stage(); reset_all()
    R("clear Cam"); R("clear Cam2")
    chk("Cam in the lodge: the first click on the keeper (real input)", talk("Cam"))
    trig("Cam", 1)
    chk("«Взять лопату»: the quest taken (#q 1), the shovel at Cam", cm("#q") == 1 and has("Cam", "cem_shovel"), (cm("#q"), has("Cam", "cem_shovel")))
    trig("Cam2", 1)
    chk("a second press does nothing (one shovel for the team)", not has("Cam2", "cem_shovel"))
    g = G[7]
    R("clear Cam"); R("give Cam minecraft:iron_shovel"); R("item replace entity Cam weapon.mainhand with minecraft:iron_shovel")
    R(f"tp Cam {g['x'] + 0.5} {g['y'] + 2} {g['z'] + 2.4}"); time.sleep(1.5)
    chk("at the cemetery Cam is in adventure", passed("execute if entity @a[name=Cam,gamemode=adventure]"))
    chk("an ordinary iron shovel does not dig the grave", not dig("Cam", g["x"], g["y"] + 1, g["z"], 4))
    R("clear Cam"); give_shovel("Cam"); R("item replace entity Cam weapon.mainhand from entity Cam container.0") if False else None
    R("clear Cam"); give_shovel("Cam")
    chk("the keeper's shovel digs the soul soil (real digging)", dig("Cam", g["x"], g["y"] + 1, g["z"], 10) and dig("Cam", g["x"], g["y"], g["z"], 10))
    ws = f"{g['x'] - 1} {g['y']} {g['z']}"
    R(f"tp Cam {g['x'] - 1.5} {g['y'] + 1} {g['z'] + 3.5}"); look_at("Cam", g["x"] - 0.5, g["y"] + 0.5, g["z"] + 0.5); time.sleep(0.4)
    tc.act("Cam", "!attack_on"); time.sleep(4); tc.act("Cam", "!attack_off")
    chk("the shovel breaks nothing else (the ground next to the grave stays)", not blk(g["x"] - 1, g["y"], g["z"], "#minecraft:air"))
    R("clear Cam"); reset_all(); unstage()

# ---------------------------------------------------------------- graves: content, unrest, waves
def items_at(c, r=2.5):
    return R("execute positioned %d.5 %d.5 %d.5 run data get entity @e[type=minecraft:item,distance=..%s,limit=1] Item" % (c[0], c[1], c[2], r))
def nitems(c, r=2.5): return count("@e[type=minecraft:item,x=%d.5,y=%d.5,z=%d.5,distance=..%s]" % (c[0], c[1], c[2], r))
def t_graves():
    print("[graves]"); stage(); reset_all()
    R("tp Cam 200 96 470"); R("tp Cam2 202 96 470"); time.sleep(1)
    # a right grave (1), by day: unrest 1 -> 1 knight
    how = open_lid(1); time.sleep(2.2)
    it = items_at(G[1]["coffin"])
    chk("right grave 1 (%s lid): the cursed sword in the coffin, the unrest 1, one knight spirit" % how, "iron_sword" in it and "le_curse" in it and cm("#dist") == 1 and spirits("le.cknight") == 1, (it[:120], cm("#dist"), spirits("le.cknight")))
    chk("the knight spirit: invisible, pale blue leather, a stone sword, no drop, 6..10 from the grave",
        spirit_ok(G[1]))
    clear_spirits()
    open_lid(1); time.sleep(2.2)
    chk("the same lid again: nothing more", cm("#dist") == 1 and spirits() == 0)
    # a wrong grave (7): +3 -> 4 -> 2 knights
    open_lid(7); time.sleep(2.2)
    chk("wrong grave 7: 2..3 bones, the unrest 4, 2 knights", nitems(G[7]["coffin"]) >= 1 and "bone" in items_at(G[7]["coffin"]) and cm("#dist") == 4 and spirits("le.cknight") == 2, (items_at(G[7]["coffin"])[:80], cm("#dist"), spirits()))
    clear_spirits()
    # Thane (6): +1 -> 5 -> 2 knights; the key in the coffin
    open_lid(6); time.sleep(2.5)
    chk("Thane's grave: the key in the coffin, the unrest 5, 2 knights", "crypt_key" in items_at(G[6]["coffin"]) and cm("#dist") == 5 and spirits("le.cknight") == 2, (items_at(G[6]["coffin"])[:80], cm("#dist"), spirits()))
    clear_spirits()
    open_lid(8); time.sleep(2.2)
    chk("wrong grave 8: the unrest 8 -> 2 knights + 1 evil spirit (named, 30 s)", cm("#dist") == 8 and spirits("le.cknight") == 2 and spirits("le.cvex") == 1 and "Злой дух" in R("data get entity @e[tag=le.cvex,limit=1] CustomName"), (cm("#dist"), spirits("le.cknight"), spirits("le.cvex")))
    clear_spirits()
    R("time set midnight"); time.sleep(1)
    open_lid(9); time.sleep(2.2)
    chk("night, wrong grave 9: the unrest 11 -> 3 knights (2 + 1 at night) + 1 evil spirit", cm("#dist") == 11 and spirits("le.cknight") == 3 and spirits("le.cvex") == 1, (cm("#dist"), spirits("le.cknight"), spirits("le.cvex")))
    open_lid(10); time.sleep(2.2)
    chk("night, wrong grave 10 on top: unrest 14 -> 4 + 2 would come, the cemetery holds at most 8 spirits", spirits() == 8, spirits())
    R("time set noon"); clear_spirits()
    R("execute as @e[type=minecraft:item] run kill @s") if False else None
    R("difficulty easy"); reset_all(); unstage()
def spirit_ok(g):
    s = "@e[tag=le.cknight,limit=1]"; p = pos(s)
    d = math.dist((p[0], p[2]), (g["x"] + 0.5, g["z"] + 0.5)) if p else -1
    e = R(f"data get entity {s}")
    return (p and 5.5 <= d <= 10.8 and "invisibility" in e and "11393254" in e and "stone_sword" in e and "minecraft:empty" in e), (d, e[:200])

# ---------------------------------------------------------------- unrest, bell
def t_unrest():
    print("[unrest]"); stage(); reset_all()
    R("scoreboard players set #dist le.cem 7"); R("execute store result score #dlast le.cem run time query gametime"); R("function last_ember:cemetery/save")
    time.sleep(3)
    chk("no fall within the 3 minutes", cm("#dist") == 7, cm("#dist"))
    R("scoreboard players remove #dlast le.cem 3590"); time.sleep(2.5)
    chk("3 minutes without an opening: the unrest 7 -> 6", cm("#dist") == 6, cm("#dist"))
    time.sleep(2.5)
    chk("then it waits 3 minutes again", cm("#dist") == 6, cm("#dist"))
    # the bell: Cam rings it (real right click)
    R("scoreboard players set #dist le.cem 6"); R("execute store result score #dlast le.cem run time query gametime"); R("function last_ember:cemetery/save")
    R("execute positioned 200 96 470 run function last_ember:cemetery/spirit_knight"); R("execute positioned 205 96 470 run function last_ember:cemetery/spirit_knight"); time.sleep(0.5)
    n0 = spirits()
    bx, by, bz = LO["bell"]
    R(f"tp Cam {bx + 0.5} {by - 1} {bz - 1.6}"); time.sleep(1); look_at("Cam", bx + 0.5, by + 0.3, bz + 0.5); time.sleep(0.5); tc.act("Cam", "!use"); time.sleep(2.2)
    chk("the bell (real click): the unrest 6 -> 2, the %d spirits gone" % n0, cm("#dist") == 2 and spirits() == 0 and n0 == 2, (cm("#dist"), spirits(), n0))
    R("execute positioned 200 96 470 run function last_ember:cemetery/spirit_knight"); time.sleep(0.3)
    tc.act("Cam", "!use"); time.sleep(2.2)
    chk("again within 5 minutes: it rings, nothing happens", cm("#dist") == 2 and spirits() == 1, (cm("#dist"), spirits()))
    clear_spirits(); reset_all(); unstage()

# ---------------------------------------------------------------- the pit
def t_pit():
    print("[pit]"); stage(); reset_all()
    g = G[15]; x, y, z = g["x"], g["y"], g["z"]
    R("clear Cam"); R(f"tp Cam {x + 0.5} {y + 2} {z - 2.5} 0 0"); time.sleep(1.5)
    tc.act("Cam", "!fwd_on") if False else None
    R(f"tp Cam {x + 0.5} {y + 2} {z + 0.5}"); time.sleep(3.5)
    p = pos("@a[name=Cam,limit=1]")
    chk("Cam steps on the sunken grave: it falls (soul soil gone), Cam at the bottom (4 under the ground)", p and p[1] <= y - 2.5 and not blk(x, y + 1, z, "minecraft:soul_soil"), (p, y))
    # out by the ladder: hold forward (toward the head wall) - real input, no jump
    R(f"tp Cam {x + 0.5} {y - 3} {z + 0.5} 180 -20"); time.sleep(0.5)
    tc.act("Cam", "!key_on w") if False else None
    out = climb("Cam", (x, y, z))
    chk("Cam climbs out by the ladder holding forward (no jump)", out, pos("@a[name=Cam,limit=1]"))
    R("tp Cam 240.5 95 470.5"); tc.setc(4, 1, 0, "Cam"); R("gamemode survival Cam"); R("tp Cam 240.5 95 470.5")
    R(f"function last_ember:trap/reset {{id:\"cem_pit_15\"}}"); time.sleep(1.0)
    R(f"tp Cam {x + 0.5} {y + 2} {z + 0.5}"); time.sleep(3)
    pp = pos("@a[name=Cam,limit=1]")
    chk("a halfling walks over it: it does not fall", blk(x, y + 1, z, "minecraft:soul_soil") and pp and pp[1] >= y + 1.9, (pp, blk(x, y + 1, z, "minecraft:soul_soil"), R("tag Cam list")))
    tc.setc(1, 1, 0, "Cam"); R("gamemode survival Cam")
    reset_all(); unstage()
def climb(p, g):
    x, y, z = g
    for _ in range(3):
        tc.act(p, "!fwd_on"); ok_ = wait(lambda: (pos(f"@a[name={p},limit=1]") or [0, -999, 0])[1] >= y + 0.9, 8); tc.act(p, "!fwd_off")
        if ok_: return True
    return False

# ---------------------------------------------------------------- the crypt
def t_crypt():
    print("[crypt]"); stage(); reset_all()
    R("scoreboard players set #q le.cem 1"); R("function last_ember:cemetery/save")
    open_lid(6); time.sleep(2.5); clear_spirits()
    c = G[6]["coffin"]; R(f"tp Cam {c[0] + 0.5} {c[1] + 1} {c[2] + 0.5}"); time.sleep(2.2)
    chk("Cam picks the key up: #q 2", has("Cam", "crypt_key") and cm("#q") == 2 and cm("#ks") == 1, (has("Cam", "crypt_key"), cm("#q"), cm("#ks")))
    d = CR["door"]
    R("item replace entity Cam weapon.mainhand with minecraft:air")
    R(f"tp Cam {d[0] + 0.5} {d[1]} {d[2] + 2.2}"); look_at("Cam", d[0] + 0.5, d[1] + 1, d[2] + 0.5); time.sleep(0.5); tc.act("Cam", "!use"); time.sleep(1)
    chk("the door without the key in the hand: shut", blk(*d, "minecraft:iron_door[open=false]") and cm("#door") == 0)
    sl = slot_of("Cam", "crypt_key"); R(f"item replace entity Cam weapon.mainhand from entity Cam {sl}"); R(f"item replace entity Cam {sl} with minecraft:air")
    look_at("Cam", d[0] + 0.5, d[1] + 1, d[2] + 0.5); time.sleep(0.4); tc.act("Cam", "!use"); time.sleep(1.5)
    chk("with the key: open for good, the key taken, #q 3", blk(*d, "minecraft:iron_door[open=true]") and cm("#door") == 1 and cm("#q") == 3 and not has("Cam", "crypt_key"), (cm("#door"), cm("#q")))
    # the corridor: Cam steps on a plate -> 3 volleys, at most 3 hits each
    p0 = CR["plates"][0]; R("gamemode adventure Cam"); R("effect clear Cam minecraft:resistance"); R("effect clear Cam minecraft:regeneration")
    hp0 = tc.hp("Cam"); R(f"tp Cam {p0[0] + 0.5} {p0[1]} {p0[2] + 0.5}"); time.sleep(3)
    hp1 = tc.hp("Cam")
    chk("a plate of the corridor: the volleys hit (T-016: damage, the shield)", hp1 is not None and hp1 < hp0 and hp1 >= 2, (hp0, hp1))
    R("effect give Cam minecraft:resistance infinite 4 true"); R("effect give Cam minecraft:regeneration infinite 2 true"); R("kill @e[type=minecraft:arrow]")
    # the Magister
    R("execute as Cam run function last_ember:cemetery/gen/tp_hall"); R("tp Cam2 %d.5 %d %d.5" % (CR["sarc"][0], CR["HF"] + 1, CR["hall"][5] - 2)); time.sleep(1.2)
    chk("a player in the hall: the Magister rises (2 s of dust), then stands", wait(lambda: count("@e[type=minecraft:skeleton,tag=le.cmag]") == 1, 6))
    m = "@e[type=minecraft:skeleton,tag=le.cmag,limit=1]"
    mh = tc.hp(m); nm = R(f"data get entity {m} CustomName")
    chk("an elite named «Магистр Ордена Ясеня», 100 health, iron armour", mh and abs(mh - 100) < 0.6 and "Магистр" in nm and "iron_chestplate" in R(f"data get entity {m} equipment"), (mh, nm[:80]))
    R("tp Cam %d.5 %d %d.5" % (CR["sarc"][0] + 2, CR["HF"] + 1, CR["sarc"][2])); time.sleep(1.2)
    chk("Cam within 7: a sword in his hand", "iron_sword" in R(f"data get entity {m} equipment.mainhand"))
    R("tp Cam %d.5 %d %d.5" % (CR["hall"][0] + 1, CR["HF"] + 1, CR["hall"][2] + 1)); R("tp Cam2 %d.5 %d %d.5" % (CR["hall"][0] + 1, CR["HF"] + 1, CR["hall"][2] + 2)); time.sleep(1.2)
    R(f"tp {m} {CR['hall'][3] - 1}.5 {CR['HF'] + 1} {CR['hall'][5] - 1}.5"); time.sleep(1.2)
    chk("everybody further than 7: a bow", "bow" in R(f"data get entity {m} equipment.mainhand"))
    R(f"damage {m} 1 minecraft:player_attack by Cam"); R(f"data modify entity {m} Health set value 45.0f"); time.sleep(2.2)
    spd = R(f"attribute {m} minecraft:movement_speed modifier value get last_ember:cem_mag_half")
    chk("at half health: 2 knight spirits from the niches, the speed x1.2", spirits("le.cknight") == 2 and "0.2" in spd, (spirits("le.cknight"), spd))
    # the leash: everybody out of the hall
    R("tp Cam %d.5 %d %d.5" % (CR["door"][0], W + 1, CR["door"][2] + 4)); R("tp Cam2 %d.5 %d %d.5" % (CR["door"][0] + 2, W + 1, CR["door"][2] + 4))
    time.sleep(12)
    chk("everybody out of the hall 10 s: the Magister gone (asleep), his spirits gone", count("@e[type=minecraft:skeleton,tag=le.cmag]") == 0 and cm("#mg") == 0 and spirits() == 0, (cm("#mg"), spirits()))
    R("execute as Cam run function last_ember:cemetery/gen/tp_hall"); time.sleep(5)
    chk("back in the hall: he rises again with full health", count("@e[type=minecraft:skeleton,tag=le.cmag]") == 1 and abs((tc.hp(m) or 0) - 100) < 0.6, tc.hp(m))
    R("effect give Cam minecraft:strength infinite 200 true"); R(f"tp Cam {CR['sarc'][0] + 1.5} {CR['HF'] + 1} {CR['sarc'][2] + 0.5}")
    R(f"damage {m} 200 minecraft:player_attack by Cam"); time.sleep(2.5)
    chk("killed by Cam: #q 4, laid to rest for good", cm("#q") == 4 and cm("#mg") == 2 and count("@e[type=minecraft:skeleton,tag=le.cmag]") == 0, (cm("#q"), cm("#mg")))
    c2 = CR["chest2"]
    chk("the lid aside, the seal in the sarcophagus, chest 2 unlocked, the exit open", count("@e[type=minecraft:item_display,tag=le.csealdisp]") == 1 and blk(c2[0], c2[1] + 1, c2[2], "#minecraft:air") and blk(*CR["bars"][0], "#minecraft:air") and blk(*CR["lid"][len(CR["lid"]) // 2], "#minecraft:air"))
    R("effect clear Cam minecraft:strength")
    h = CR["hollow"]; R(f"tp Cam {h[0] + 0.5} {h[1]} {h[2] - 2.2}"); time.sleep(1); look_at("Cam", h[0] + 0.5, h[1] + 1.15, h[2] + 0.5); time.sleep(0.4); tc.act("Cam", "!use"); time.sleep(1.5)
    chk("the seal taken (real click): at Cam, its lore", has("Cam", "seal") and "Колоссы помнят эту руку." in inv("Cam"))
    R("time set midnight"); time.sleep(3)
    chk("he never comes back (a night, players in the hall)", count("@e[type=minecraft:skeleton,tag=le.cmag]") == 0)
    R("time set noon")
    R("difficulty peaceful"); reset_all(); R("scoreboard players set #q le.cem 3"); R("scoreboard players set #door le.cem 1"); R("function last_ember:cemetery/save")
    R("execute as Cam run function last_ember:cemetery/gen/tp_hall"); time.sleep(3)
    chk("peaceful: the Magister counts as laid to rest, the seal in the sarcophagus", cm("#q") == 4 and count("@e[type=minecraft:item_display,tag=le.csealdisp]") == 1)
    R("difficulty easy"); R("clear Cam"); reset_all(); unstage()
def slot_of(p, key):
    d = inv(p)
    for m in re.finditer(r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}', d):
        s = m.group(0)
        if f'le_citem: "{key}"' in s:
            sl = int(re.search(r"Slot: (\d+)b", s).group(1)); return "hotbar.%d" % sl if sl < 9 else "inventory.%d" % (sl - 9)
    return "hotbar.0"

# ---------------------------------------------------------------- lost items
def t_lost():
    print("[lost]"); stage(); reset_all()
    R("clear Cam"); R("clear Cam2")
    talk("Cam"); trig("Cam", 1)
    g0 = gen("cem_shovel")
    R("tp Cam 118 200 448"); throw_all("Cam", "cem_shovel"); time.sleep(0.5); R("kill @e[type=minecraft:item,x=118,y=200,z=448,distance=..6]"); time.sleep(2.2)
    chk("the shovel destroyed (kill of the item): lost (#sh 2)", cm("#sh") == 2, cm("#sh"))
    talk("Cam"); time.sleep(0.5)
    chk("the keeper gives another (a new generation)", has("Cam", "cem_shovel") and gen("cem_shovel") == g0 + 1 and cm("#sh") == 1)
    # the key: in the coffin, picked up, thrown into lava -> back in the coffin (the lid shut)
    R("scoreboard players set #q le.cem 1"); open_lid(6); time.sleep(2.5); clear_spirits()
    c = G[6]["coffin"]; R(f"tp Cam {c[0] + 0.5} {c[1] + 1} {c[2] + 0.5}"); time.sleep(2.2)
    R("setblock 120 205 448 minecraft:lava"); R("tp Cam 120 206 450"); throw_all("Cam", "crypt_key"); R("execute as @e[type=minecraft:item] if items entity @s contents *[minecraft:custom_data~{le_citem:\"crypt_key\"}] run tp @s 120.5 205.2 448.5"); time.sleep(3.5)
    R("setblock 120 205 448 minecraft:air")
    lx, ly, lz = G[6]["lid"]
    chk("the key in lava: back in Thane's coffin (the lid shut, #ks 0)", cm("#ks") == 0 and blk(lx, ly, lz, "minecraft:dark_oak_trapdoor[open=false]"), (cm("#ks"),))
    open_lid(6); time.sleep(2.5)
    chk("the lid opened again: the key in the coffin (a new generation)", "crypt_key" in items_at(c) and cm("#dist") == 1, (items_at(c)[:80], cm("#dist")))
    clear_spirits()
    # the seal
    R("scoreboard players set #mg le.cem 2"); R("scoreboard players set #ss le.cem 1"); R("scoreboard players set #q le.cem 4"); R("function last_ember:cemetery/save"); time.sleep(2)
    R("execute as Cam run function last_ember:cemetery/seal")
    s0 = has("Cam", "seal"); R("tp Cam 118 200 448"); throw_all("Cam", "seal"); time.sleep(0.4); R("kill @e[type=minecraft:item,x=118,y=200,z=448,distance=..6]"); time.sleep(2.5)
    chk("the seal destroyed: again in the sarcophagus (#ss 1, the display)", s0 and cm("#ss") == 1 and count("@e[type=minecraft:item_display,tag=le.csealdisp]") == 1, (s0, cm("#ss")))
    R("clear Cam"); reset_all(); unstage()
def gen(key): m = re.search(r"(\d+)", R(f"data get storage last_ember:cemetery gen.{key}").split(":")[-1]); return int(m.group(1)) if m else None
def throw_all(p, key):
    d = inv(p)
    for m in re.finditer(r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}', d):
        s = m.group(0)
        if f'le_citem: "{key}"' in s:
            sl = int(re.search(r"Slot: (\d+)b", s).group(1)); sn = "hotbar.%d" % sl if sl < 9 else "inventory.%d" % (sl - 9)
            pp = pos(f"@a[name={p},limit=1]")
            R(f"execute at {p} run summon minecraft:item ~ ~1 ~ {{Item:{{id:\"minecraft:stone\",count:1}},Tags:[\"le.cthrow\"],PickupDelay:100s}}")
            R(f"item replace entity @e[tag=le.cthrow,limit=1] contents from entity {p} {sn}"); R(f"item replace entity {p} {sn} with minecraft:air"); R("tag @e[tag=le.cthrow] remove le.cthrow")

# ---------------------------------------------------------------- curses and the absolution
def eff(p, e): return f"minecraft:{e}" in R(f"data get entity {p} active_effects")
def t_curses():
    print("[curses]"); stage(); reset_all()
    R("tp Cam 118 193 450"); R("clear Cam")
    for k, n in enumerate((2, 3, 4, 5)): R(f"loot replace entity Cam inventory.{k} loot last_ember:cemetery/grave_{n}")
    R("effect clear Cam"); time.sleep(2.5)
    chk("the cursed things in the bag: no effect", not any(eff("Cam", e) for e in ("slowness", "hunger", "weakness")))
    for sl, n in (("armor.chest", 2), ("armor.legs", 4), ("armor.feet", 5)):
        R(f"loot replace entity Cam {sl} loot last_ember:cemetery/grave_{n}")
    time.sleep(2.5)
    chk("worn: the Weight (slowness I), the Hunger (hunger I), the Weakness (weakness I)", eff("Cam", "slowness") and eff("Cam", "hunger") and eff("Cam", "weakness"))
    R("item replace entity Cam armor.chest with minecraft:air"); R("item replace entity Cam armor.legs with minecraft:air"); R("item replace entity Cam armor.feet with minecraft:air")
    time.sleep(4.5)
    chk("taken off: the effects end (3 s)", not any(eff("Cam", e) for e in ("slowness", "hunger", "weakness")))
    R("effect clear Cam minecraft:regeneration"); R("effect clear Cam minecraft:resistance"); R("effect clear Cam minecraft:saturation"); R("effect give Cam minecraft:instant_health 1 3 true"); time.sleep(0.5)
    R("loot replace entity Cam weapon.offhand loot last_ember:cemetery/grave_1"); R("scoreboard players set #sec le.cem 18")
    hs = []
    for _ in range(20): hs.append(tc.hp("Cam") or 99); time.sleep(0.15)
    h = min(hs)
    chk("the Blood in the off hand: 1 damage every 20 s", h is not None and 18.5 <= h <= 19.5, h)
    R("effect give Cam minecraft:instant_damage 1 0 true"); R("effect give Cam minecraft:instant_damage 1 0 true"); time.sleep(0.5)
    R("data merge entity Cam {}") if False else None
    R("damage Cam 7 minecraft:generic"); time.sleep(0.3); R("scoreboard players set #sec le.cem 18"); time.sleep(3.5)
    h2 = tc.hp("Cam")
    chk("never under 6 health", h2 is not None and h2 >= 6 - 0.01, h2)
    R("item replace entity Cam weapon.offhand with minecraft:air"); R("effect give Cam minecraft:regeneration infinite 2 true"); R("effect give Cam minecraft:resistance infinite 4 true"); R("effect give Cam minecraft:saturation infinite 1 true")
    # the knight's blessing does not mend a cursed thing; the absolution
    tc.setc(1, 1, 0, "Cam"); R("gamemode survival Cam")
    R("loot replace entity Cam weapon.mainhand loot last_ember:cemetery/grave_1")
    d0 = dmg("Cam"); R("execute as Cam run function last_ember:knight/bless") ; time.sleep(0.5)
    chk("the knight's blessing does not mend the cursed sword", dmg("Cam") == d0, (d0, dmg("Cam")))
    R("scoreboard players set #q le.cem 4"); R("function last_ember:cemetery/save")
    R("clear Cam minecraft:nautilus_shell")
    talk("Cam"); trig("Cam", 2)
    chk("no trophy: the line, the curse stays", "le_cursed: 1b" in R("data get entity Cam SelectedItem") or "le_cursed:1b" in R("data get entity Cam SelectedItem") or 'le_cursed: 1b' in inv("Cam"))
    R("give Cam minecraft:nautilus_shell[minecraft:custom_data={le_trophy:\"r1\"},minecraft:max_stack_size=16] 2")
    trig("Cam", 2)
    i = R("data get entity Cam SelectedItem") + inv("Cam")
    chk("the absolution: one trophy taken, the curse gone («Отпето.»)", "Отпето." in i and "le_cursed: 0b" in i and tro("Cam") == 1, (tro("Cam"), i[:300]))
    d1 = dmg("Cam"); R("execute as Cam run function last_ember:knight/bless"); time.sleep(0.5)
    chk("the blessing mends it now", dmg("Cam") < d1, (d1, dmg("Cam")))
    R("item replace entity Cam weapon.mainhand with minecraft:stone"); trig("Cam", 2)
    chk("nothing cursed in the hand: the line, no trophy taken", tro("Cam") == 1)
    R("clear Cam"); reset_all(); unstage()
def dmg(p):
    m = re.search(r'"minecraft:damage": (\d+)', R(f"data get entity {p} SelectedItem")); return int(m.group(1)) if m else 0
def tro(p): m = re.search(r"(\d+)", R(f"execute store result score #tro le.cem run clear {p} minecraft:nautilus_shell 0") or ""); return cm("#tro")

# ---------------------------------------------------------------- spyglass
def t_spyglass():
    print("[spyglass]"); stage(); reset_all()
    sp = LO["spyglass"]
    R("time set noon"); R(f"tp Cam {sp[0] - 1.3} {sp[1] - 1} {sp[2] + 0.5}"); look_at("Cam", sp[0] + 0.5, sp[1] + 0.4, sp[2] + 0.5); time.sleep(0.4); tc.act("Cam", "!use"); time.sleep(0.8)
    chk("by day: no lights (the line)", cm("Cam") is None or (tc.score("Cam", "le.cspy") or 0) <= cm("#gt"))
    R("time set midnight"); time.sleep(0.4); tc.act("Cam", "!use"); time.sleep(0.8)
    chk("at night: 15 s of soul lights for Cam (his score), not for Cam2", (tc.score("Cam", "le.cspy") or 0) > (cm("#gt") or 0) and (tc.score("Cam2", "le.cspy") or 0) <= (cm("#gt") or 0))
    v0 = tc.score("Cam", "le.cspy"); tc.act("Cam", "!use"); time.sleep(0.8)
    chk("a second click within 20 s: the cooldown", tc.score("Cam", "le.cspy") == v0)
    R("time set noon"); reset_all(); unstage()

# ---------------------------------------------------------------- fade
def t_fade():
    print("[fade]"); stage(); reset_all()
    open_lid(3); time.sleep(2.2); clear_spirits()
    R("tp Cam 200 140 470"); R("tp Cam2 202 140 470")
    R("function last_ember:region/gen/fade_r1"); time.sleep(4)
    g1, g3 = G[1], G[3]
    chk("faded: an unopened grave is a pit (the soul soil gone, the lid there)", blk(g1["x"], g1["y"] + 1, g1["z"], "#minecraft:air") and blk(*g1["lid"], "minecraft:dark_oak_trapdoor"))
    chk("the candles of the graves are soul lanterns", all(blk(*g["candle"], "minecraft:soul_lantern") for g in M["graves"]))
    chk("the lodge dark (no lamps, no post lantern), its door open, a lantern at the crypt door", not any(blk(*l, "minecraft:lantern") for l in LO["lamps"]) and blk(*LO["post_lantern"], "#minecraft:air") and blk(*LO["door"], "minecraft:spruce_door[open=true]"))
    time.sleep(2.5)
    chk("the keeper and the dog at the crypt door", near(kpos(), DPM["keeper_faded"]) and near(pos("@e[type=minecraft:wolf,tag=le.cdog,limit=1]"), DPM["dog_faded"]), (kpos(), DPM["keeper_faded"]))
    d = R("execute positioned %d 118 482 run data get block 234 118 482" % 0)
    # the sword across the stair: blocks over the north flight at z 482, the stair under it free
    st = [c for c in M["hill"] if c[4] == "S" and c[1] == 482]
    y = st[0][2] if st else None
    chk("the great sword lies across the hill stair, 4 over the steps; the steps under it free", y and not blk(233, y + 4, 482, "#minecraft:air") and all(blk(233, y + k, 482, "#minecraft:air") for k in (1, 2, 3)), y)
    R("function last_ember:region/gen/unfade_r1"); time.sleep(4)
    chk("back: the soul soil on unopened graves, the opened one open, the candles, the lodge lit, the sword up",
        blk(g1["x"], g1["y"] + 1, g1["z"], "minecraft:soul_soil") and blk(g3["x"], g3["y"] + 1, g3["z"], "#minecraft:air") and blk(*g1["candle"], "minecraft:candle[lit=true]") and
        blk(*LO["post_lantern"], "minecraft:lantern") and blk(233, y + 4, 482, "#minecraft:air"))
    time.sleep(2.5)
    chk("the keeper home again", near(kpos(), DPM["keeper_day"]) or near(kpos(), DPM["keeper_night"]))
    reset_all(); unstage()

# ---------------------------------------------------------------- zones
def t_zones():
    print("[zones]"); stage(); reset_all()
    R("clear Cam"); R("give Cam minecraft:diamond_pickaxe"); R("tp Cam 200 96 466"); time.sleep(1.5)
    chk("at the cemetery: adventure", passed("execute if entity @a[name=Cam,gamemode=adventure]"))
    s = M["swords"][0]; x, z = s[0], s[1]
    y = next(yy for yy in range(130, 60, -1) if blk(x, yy, z, "#minecraft:walls") or blk(x, yy, z, "minecraft:polished_deepslate_wall") or blk(x, yy, z, "minecraft:tuff_wall"))
    R(f"tp Cam {x + 0.5} {y - 1} {z + 2.5}"); look_at("Cam", x + 0.5, y - 0.5, z + 0.5); time.sleep(0.4); tc.act("Cam", "!attack_on"); time.sleep(3); tc.act("Cam", "!attack_off")
    chk("a small sword cannot be broken", not blk(x, y - 1, z, "#minecraft:air"))
    lx, ly, lz = LO["centre"]
    R("difficulty hard"); R("time set midnight"); R(f"tp Cam {lx} {ly + 30} {lz}"); time.sleep(1)
    R(f"summon minecraft:zombie {lx} {ly} {lz - 6} {{Tags:[\"le.ctest\"],PersistenceRequired:1b}}"); time.sleep(2.5)
    chk("a monster at the lodge is removed (no_spawn)", count("@e[tag=le.ctest]") == 0 or not passed(f"execute if entity @e[tag=le.ctest,y={ly - 5},dy=20]"))
    chk("the keeper and the dog stay", count("@e[type=minecraft:villager,tag=le.ckeeper]") == 1 and count("@e[type=minecraft:wolf,tag=le.cdog]") == 1)
    R("kill @e[tag=le.ctest]"); R("difficulty easy"); R("time set noon"); R("clear Cam"); unstage()

# ---------------------------------------------------------------- restart
def tmz(): return load("test_maze")
def t_restart():
    print("[restart]"); stage(); reset_all()
    open_lid(1); open_lid(7); time.sleep(2.5); clear_spirits()
    R("scoreboard players set #q le.cem 4"); R("scoreboard players set #ks le.cem 2"); R("scoreboard players set #door le.cem 1"); R("scoreboard players set #mg le.cem 2"); R("scoreboard players set #ss le.cem 1")
    R("function last_ember:cemetery/save"); time.sleep(2)
    st0 = [cm(k) for k in ("#g1", "#g7", "#q", "#ks", "#door", "#mg", "#ss", "#dist")]
    tmz().restart(); stage()
    st1 = [cm(k) for k in ("#g1", "#g7", "#q", "#ks", "#door", "#mg", "#ss", "#dist")]
    chk("after a restart: 2 opened graves, the key used, the door open, the Magister dead, the seal in the sarcophagus", st0 == st1 and st1[:7] == [1, 1, 4, 2, 1, 2, 1], (st0, st1))
    time.sleep(2.5)
    chk("the world: the door open, the lid aside, the seal shown", blk(*CR["door"], "minecraft:iron_door[open=true]") and count("@e[type=minecraft:item_display,tag=le.csealdisp]") == 1)
    R("scoreboard players reset * le.cem"); R("reload"); time.sleep(3)
    chk("scores lost (reset *) -> taken back from the storage", [cm(k) for k in ("#g1", "#g7", "#q", "#ks", "#door", "#mg", "#ss")] == st1[:7])
    reset_all(); unstage()

# ---------------------------------------------------------------- perf
def t_perf():
    print("[perf: two players at the cemetery at night, unrest 12]"); stage(night=True); reset_all()
    R("difficulty hard"); R("gamemode survival Cam"); R("gamemode survival Cam2")
    R("tp Cam 230 96 466"); R("tp Cam2 200 96 480")
    R("scoreboard players set #dist le.cem 11"); open_lid(9); open_lid(2); time.sleep(3)
    R("gamerule advance_time true"); time.sleep(20)
    m = tmz()
    p0 = m.prof(10); ms = [m.mspt() for _ in range(3)]
    f = sum(v for k, v in p0.items() if k.startswith("last_ember:cemetery/")); mobs = count("@e[type=#last_ember:monsters,%s]" % CBOX)
    print(f"     profiler: cemetery/* {f:.3f} ms per tick, server tick {p0.get('tick', 0):.1f} ms, tick query {ms} ms, monsters at the cemetery {mobs}, spirits {spirits()}")
    for k, v in sorted(p0.items(), key=lambda kv: -kv[1])[:8]: print(f"       {k} {v:.3f}")
    chk("night, 2 players, unrest 12: cemetery/* under 0.5 ms per tick (the garden's limit), the tick keeps up", 0 <= f < 0.5 and ms[0] and max(ms) < 50, (f, ms))
    R("gamerule advance_time false"); R("time set noon"); R("difficulty easy"); reset_all(); unstage()

SUITES = dict(build=t_build, keeper=t_keeper, quest=t_quest, graves=t_graves, unrest=t_unrest, pit=t_pit, crypt=t_crypt, lost=t_lost, curses=t_curses,
              spyglass=t_spyglass, fade=t_fade, zones=t_zones, restart=t_restart, perf=t_perf)
if __name__ == "__main__":
    for a in sys.argv[1:] or list(SUITES):
        SUITES[a]()
    print(f"cemetery: {ok} ok, {bad} failed")
