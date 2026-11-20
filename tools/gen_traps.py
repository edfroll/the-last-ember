#!/usr/bin/env python3
"""T-016: traps/traps.txt (or a given file) -> datapack function/trap/gen/* (generated, do not edit): the cell index, per trap in_/tk_/hint_/fire_/build_/reset_/slow_ functions and the dispatchers.
Usage: python3 tools/gen_traps.py [traps_file]      (the test playground: traps/test_traps.txt; regenerate without it before a commit)"""
import os, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, "datapack/data/last_ember"); GEN = os.path.join(DP, "function/trap/gen")
shutil.rmtree(GEN, ignore_errors=True); os.makedirs(os.path.join(GEN, "p"), exist_ok=True)
import re
SUBS = {"positioned", "if", "unless", "as", "at", "store", "facing", "rotated", "align", "anchored", "in", "on", "run", "execute"}
def fix(l):
    """the dimension fragment 'in minecraft:X ' of the templates is made a valid command: at the start 'execute in X run <cmd>' (or merged into 'execute'), inside a chain 'in X' + 'run' when a plain command follows"""
    if l.startswith("in minecraft:"):
        d, rest = l.split(" ", 2)[1], l.split(" ", 2)[2] if l.count(" ") >= 2 else ""
        l = ("execute in %s %s" % (d, rest[8:]) if rest.startswith("execute ") else "execute in %s %s" % (d, rest) if rest.split(" ")[0] in SUBS else "execute in %s run %s" % (d, rest))
    def mid(m):
        d, nxt = m.group(1), m.group(2)
        if nxt == "execute": return " run execute in %s " % d if m.group(0).startswith(" run") else " in %s " % d
        return (" in %s " % d + ("" if nxt in SUBS else "run ")) + nxt
    l = re.sub(r" run in (minecraft:\w+) (execute) ", lambda m: " run execute in %s " % m.group(1), l)
    l = re.sub(r" run in (minecraft:\w+) (?!execute)", lambda m: " run execute in %s run " % m.group(1), l)
    l = re.sub(r"(?<!run) in (minecraft:\w+) (\w+)", lambda m: " in %s %s%s" % (m.group(1), "" if m.group(2) in SUBS else "run ", m.group(2)) if not l.startswith("execute in " + m.group(1) + " " + m.group(2)) or True else m.group(0), l)
    return l
def w(name, lines, sub=""): open(os.path.join(GEN, sub, name + ".mcfunction"), "w", encoding="utf-8").write("\n".join(fix(l) if not l.startswith("#") else l for l in lines) + "\n")
DIMS = {"overworld": "o", "the_nether": "n", "the_end": "e"}
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "traps/traps.txt")
TYPES = ("pit", "arrows", "plate", "collapse", "gas", "lava", "cursed_chest", "false_treasure")
traps = []
for ln, l in enumerate(open(src, encoding="utf-8"), 1):
    l = l.split("#", 1)[0].strip()
    if not l: continue
    f = l.split(); tid, typ, dim = f[0], f[1], f[2]
    if typ not in TYPES or dim not in DIMS: raise SystemExit(f"{src}:{ln}: bad type or dimension")
    x1, y1, z1, x2, y2, z2 = map(int, f[3:9]); P = dict(p.split("=", 1) for p in f[9:])
    traps.append(dict(id=tid, type=typ, dim=dim, n=len(traps) + 1, x1=min(x1, x2), y1=min(y1, y2), z1=min(z1, z2), x2=max(x1, x2), y2=max(y1, y2), z2=max(z1, z2), P=P))
ids = {t["id"] for t in traps}
if len(ids) != len(traps): raise SystemExit("duplicate trap id")
def C(s): return [int(v) for v in s.split(",")]
def pts(s): return [tuple(C(p)) for p in s.split(";")]
def boxsel(a, b, c, d, e, f): return "x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d" % (a, b, c, d - a, e - b, f - c)
for t in traps:
    t["sel"] = boxsel(t["x1"], t["y1"], t["z1"], t["x2"], t["y2"], t["z2"]); t["cx"] = (t["x1"] + t["x2"]) // 2; t["cy"] = t["y1"]; t["cz"] = (t["z1"] + t["z2"]) // 2
    t["IN"] = "in minecraft:%s " % t["dim"]
def S(t, k): return "#%s_%s le.tr" % (t["id"], k)
init = ["# generated: state of every trap (kept over reloads), the cells of the index"]
cells = {}
for t in traps:
    for k in ("st", "t", "cd", "bl", "ow"): init.append("execute unless score %s matches -2147483648..2147483647 run scoreboard players set %s 0" % (S(t, k), S(t, k)))
    cx0, cx1 = (t["x1"] - 2 + 8192) // 64, (t["x2"] + 2 + 8192) // 64; cz0, cz1 = (t["z1"] - 2 + 8192) // 64, (t["z2"] + 2 + 8192) // 64
    for cx in range(cx0, cx1 + 1):
        for cz in range(cz0, cz1 + 1): cells.setdefault((DIMS[t["dim"]], cx, cz), []).append(t)
for (d, cx, cz), ts in cells.items():
    init.append("data modify storage last_ember:traps cells.%s%d_%d set value 1b" % (d, cx, cz))
    w("%s%d_%d" % (d, cx, cz), ["# generated: the traps whose area reaches this cell (as a player)"] + ["execute if entity @s[%s] run function last_ember:trap/gen/in_%s" % (t["sel"], t["id"]) for t in ts], "p")
w("init", init)
def plus(t, dx=0, dy=0, dz=0): return (t["x1"] + dx, t["y1"] + dy, t["z1"] + dz)
build_p = ["# generated: traps whose chunk is loaded are built once (every second)"]; slow = ["# generated: every second, per trap: the things that need no player"]; hints = ["# generated: every second: the hints of every trap that has a player within 24 blocks"]
tick = ["# generated: every tick: the traps that are running"]
for t in traps:
    i, n, T, IN = t["id"], t["n"], t["type"], t["IN"]; P = t["P"]
    st, tt, cd, bl, ow = (S(t, k) for k in ("st", "t", "cd", "bl", "ow"))
    inn = ["# generated: as a player in the area of %s (%s)" % (i, T)]; tk = ["# generated: one tick of %s"  % i]; hint = ["# generated: hints of %s (at the trap, a player is near)" % i]; fire = ["# generated: %s fired by a link or by the admin (any context)" % i]
    build = ["# generated: build %s" % i, "scoreboard players set %s 1" % bl]; reset = ["# generated: %s back to the start" % i, "scoreboard players set %s 0" % st, "scoreboard players set %s 0" % tt, "scoreboard players set %s 0" % cd]
    light = "execute if entity @s[tag=le.race.halfling] run return 0"
    cxyz = "%d %d %d" % (t["cx"], t["cy"], t["cz"])
    ONE = ["execute unless score %s matches 0 run return 0" % st]
    if T == "pit":
        cover = P.get("cover", "minecraft:moss_carpet"); depth = int(P.get("depth", 8)); A = (t["x1"], t["y1"], t["z1"], t["x2"], t["y1"], t["z2"])
        below = boxsel(t["x1"], t["y1"] - depth, t["z1"], t["x2"], t["y2"] + 3, t["z2"])
        inn += [light] + ONE + ["scoreboard players set %s 1" % st, "scoreboard players set %s 0" % tt, "function last_ember:trap/shield", "execute positioned %s run playsound minecraft:block.azalea_leaves.break block @a[distance=..12] ~ ~ ~ 1 0.7" % cxyz]
        tk += ["scoreboard players add %s 1" % tt, "execute if score %s matches 1 run %sparticle minecraft:block{block_state:\"%s\"} %d %d %d 1 0.2 1 0.05 20 force" % (tt, IN, cover, t["cx"] + 0.5, t["y1"] + 1, t["cz"] + 0.5) if False else
               "execute if score %s matches 1 %spositioned %s run particle minecraft:block{block_state:\"%s\"} ~ ~1 ~ 1 0.2 1 0.05 20 force" % (tt, IN, cxyz, cover),
               "execute if score %s matches 10 run %sfill %d %d %d %d %d %d minecraft:air replace %s" % ((tt, IN) + A + (cover,)),
               "execute if score %s matches 10 %spositioned %s run playsound minecraft:block.moss.break block @a[distance=..16] ~ ~ ~ 1.2 0.6" % (tt, IN, cxyz),
               "execute if score %s matches 10 if score %s matches 0 run function last_ember:trap/gen/owner_%s" % (tt, ow, i),
               "execute if score %s matches 10 run scoreboard players set %s 3" % (tt, st), "execute if score %s matches 10 run scoreboard players set %s 11" % (tt, tt),
               "execute if score %s matches 1210.. if score %s matches 3 %sunless entity @a[%s] run function last_ember:trap/gen/restore_%s" % (tt, st, IN, below, i)]
        # (st 3: tt counts from 11 up; 1200 ticks of waiting = 60 s)
        reset += ["%sfill %d %d %d %d %d %d %s replace minecraft:air" % ((IN,) + A + (cover,))]
        w("restore_" + i, ["%sfill %d %d %d %d %d %d %s replace minecraft:air" % ((IN,) + A + (cover,)), "scoreboard players set %s 0" % st, "scoreboard players set %s 0" % tt, "%spositioned %s run playsound minecraft:block.moss.place block @a[distance=..16] ~ ~ ~ 1 0.8" % (IN, cxyz)])
        if "owner" in P:
            ox, oy, oz = C(P["ownerpos"]); name = P.get("ownername", "Хозяин_логова").replace("_", " "); eq = P.get("equip", "")
            w("owner_" + i, ["# the master of the lair: once, on the first firing", "scoreboard players set %s 1" % ow,
                             "%ssummon %s %d.5 %d %d.5 {PersistenceRequired:1b,CustomName:'{\"text\":\"%s\",\"color\":\"dark_red\"}',CustomNameVisible:1b,Tags:[\"le.trap_owner\",\"le.noelite\",\"le.tnew\"]}" % (IN, P["owner"], ox, oy, oz, name),
                             "%sscoreboard players set @e[tag=le.tnew,limit=1] le.tid %d" % (IN, n)] + (["%sexecute as @e[tag=le.tnew,limit=1] at @s run function %s" % (IN, eq)] if eq else []) + ["%sexecute as @e[tag=le.tnew] run tag @s remove le.tnew" % IN])
        else: w("owner_" + i, ["scoreboard players set %s 2" % ow])
        if "chest" in P:
            kx, ky, kz = C(P["chest"]); lock = P.get("lock", "minecraft:iron_block")
            build += ["%ssetblock %d %d %d %s" % (IN, kx, ky + 1, kz, lock)]; reset += ["%ssetblock %d %d %d %s" % (IN, kx, ky + 1, kz, lock), "scoreboard players set %s 0" % ow, "%skill @e[tag=le.trap_owner,scores={le.tid=%d}]" % (IN, n)]
            slow += ["execute if score %s matches 1 %sif loaded %d %d %d unless entity @e[tag=le.trap_owner,scores={le.tid=%d}] run function last_ember:trap/gen/unlock_%s" % (ow, IN, kx, ky, kz, n, i)]
            w("unlock_" + i, ["scoreboard players set %s 2" % ow, "%ssetblock %d %d %d minecraft:air" % (IN, kx, ky + 1, kz), "%spositioned %d %d %d run playsound minecraft:block.iron_door.open block @a[distance=..24] ~ ~ ~ 1 0.8" % (IN, kx, ky, kz)])
        else: pass
        hint += ["execute if entity @a[%s] run playsound minecraft:block.azalea_leaves.step block @a[distance=..12] ~ ~ ~ 0.5 0.6" % boxsel(t["x1"] - 2, t["y1"] - 1, t["z1"] - 2, t["x2"] + 2, t["y2"] + 1, t["z2"] + 2) if False else
                 "execute positioned %s if entity @a[%s] unless entity @a[%s] run playsound minecraft:block.azalea_leaves.step block @a[distance=..14] ~ ~ ~ 0.6 0.6" % (cxyz, boxsel(t["x1"] - 2, t["y1"] - 1, t["z1"] - 2, t["x2"] + 2, t["y2"] + 2, t["z2"] + 2), t["sel"]),
                 "execute if score %s matches 0 if predicate last_ember:chance_30 %spositioned %s run particle minecraft:falling_dust{block_state:\"%s\"} ~ ~1.5 ~ 0.8 0 0.8 0 1 normal" % (st, IN, cxyz, cover)]
        fire += ["execute unless score %s matches 0 run return 0" % st, "scoreboard players set %s 1" % st, "scoreboard players set %s 0" % tt]
        tickc = "1.."
    elif T == "arrows":
        P_ = pts(P["pts"]); tgt = "@p[%s]" % t["sel"]
        start = ["execute unless score %s matches 0 run return 0" % st, "execute if score #gt le.e < %s run return 0" % cd, "scoreboard players set %s 1" % st, "scoreboard players set %s 0" % tt,
                 "scoreboard players operation %s = #gt le.e" % cd, "scoreboard players add %s 200" % cd,
                 "execute as @a[%s] run scoreboard players set @s le.tbud 0" % t["sel"], "execute as @a[%s] run function last_ember:trap/shield" % t["sel"],
                 "execute positioned %s run playsound minecraft:block.dispenser.fail block @a[distance=..16] ~ ~ ~ 0.8 1.4" % cxyz]
        inn += start; fire += start
        tk += ["scoreboard players add %s 1" % tt]
        for v in (10, 20, 30):
            for (px, py, pz) in P_: tk.append("execute if score %s matches %d %spositioned %d.5 %d.5 %d.5 if entity %s facing entity %s eyes run function last_ember:trap/arrow_fire" % (tt, v, IN, px, py, pz, tgt, tgt))
        tk += ["execute if score %s matches 38.. run scoreboard players set %s 0" % (tt, st)]
        reset += ["kill @e[tag=le.trap_arrow]"]
        hint += ["execute positioned %s if entity @a[%s] unless entity @a[%s] run playsound minecraft:block.piston.contract block @a[distance=..10] ~ ~ ~ 0.15 2.0" % (cxyz, boxsel(t["x1"] - 3, t["y1"], t["z1"] - 3, t["x2"] + 3, t["y2"] + 2, t["z2"] + 3), t["sel"]) if False else "# the holes in the wall are the hint (built by the map)"]
    elif T == "plate":
        link = P.get("link", "")
        inn += [light, "execute positioned %s run playsound minecraft:block.stone_pressure_plate.click_on block @a[distance=..14] ~ ~ ~ 0.8 0.9" % cxyz]
        inn += (["execute if score #%s_st le.tr matches 0 run function last_ember:trap/gen/fire_%s" % (link, link)] if link else ["function last_ember:trap/plate_fn"])
        fire += ["function last_ember:trap/gen/fire_%s" % link if link else "# nothing"]
        hint += ["# the plate of another material is the hint (built by the map)"]
    elif T == "collapse":
        fl = P.get("floor", "minecraft:cracked_stone_bricks"); A = (t["x1"], t["y1"], t["z1"], t["x2"], t["y1"], t["z2"])
        inn += [light] + ONE + ["scoreboard players set %s 1" % st, "scoreboard players set %s 0" % tt, "function last_ember:trap/shield"]
        fire += ["execute unless score %s matches 0 run return 0" % st, "scoreboard players set %s 1" % st, "scoreboard players set %s 0" % tt, "execute positioned %s run function last_ember:trap/shield_near" % cxyz]
        tk += ["scoreboard players add %s 1" % tt,
               "execute if score %s matches 1 %spositioned %s run playsound minecraft:block.gravel.break block @a[distance=..16] ~ ~ ~ 1.2 0.5" % (tt, IN, cxyz),
               ] + ["execute if score %s matches %d %spositioned %s run particle minecraft:block{block_state:\"%s\"} ~ ~1.1 ~ %.1f 0.1 %.1f 0.05 12 force" % (tt, v, IN, cxyz, fl, (t["x2"] - t["x1"] + 1) / 2, (t["z2"] - t["z1"] + 1) / 2) for v in (1, 5, 10, 15)] + [
               "execute if score %s matches 20 run function last_ember:trap/gen/drop_%s" % (tt, i),
               "execute if score %s matches 45 run %skill @e[type=minecraft:falling_block,tag=le.trap_fb]" % (tt, IN),
               "execute if score %s matches 46.. if score %s matches 1 run scoreboard players set %s 3" % (tt, st, st), "execute if score %s matches 46.. if score %s matches 3 run scoreboard players set %s 1000" % (tt, st, tt) if False else "# (the waiting state counts the ticks)",
               "execute if score %s matches 1250.. if score %s matches 3 %sunless entity @a[%s] run function last_ember:trap/gen/restore_%s" % (tt, st, IN, boxsel(t["x1"] - 1, t["y1"] - 1, t["z1"] - 1, t["x2"] + 1, t["y2"] + 2, t["z2"] + 1), i)]
        d = ["# the floor of %s falls" % i, "%splaysound minecraft:block.gravel.break block @a[x=%d,y=%d,z=%d,distance=..20] ~ ~ ~ 1.5 0.5" % (IN, t["cx"], t["cy"], t["cz"]) if False else "%spositioned %s run playsound minecraft:entity.generic.explode block @a[distance=..20] ~ ~ ~ 0.8 0.6" % (IN, cxyz)]
        for x in range(t["x1"], t["x2"] + 1):
            for z in range(t["z1"], t["z2"] + 1): d.append("%ssummon minecraft:falling_block %d.5 %d.5 %d.5 {BlockState:{Name:\"%s\"},Time:1,DropItem:0b,HurtEntities:0b,Tags:[\"le.trap_fb\"]}" % (IN, x, t["y1"], z, fl))
        d.append("%sfill %d %d %d %d %d %d minecraft:air replace %s" % ((IN,) + A + (fl,)))
        w("drop_" + i, d)
        w("restore_" + i, ["%sfill %d %d %d %d %d %d %s replace minecraft:air" % ((IN,) + A + (fl,)), "scoreboard players set %s 0" % st, "scoreboard players set %s 0" % tt, "%spositioned %s run playsound minecraft:block.stone.place block @a[distance=..16] ~ ~ ~ 1 0.8" % (IN, cxyz)])
        reset += ["%sfill %d %d %d %d %d %d %s replace minecraft:air" % ((IN,) + A + (fl,)), "%skill @e[type=minecraft:falling_block,tag=le.trap_fb]" % IN]
        hint += ["# the cracks are the hint (cracked blocks built by the map); the dust and the crunch come one second before the fall"]
    elif T == "gas":
        V = pts(P["vents"])
        start = ["execute unless score %s matches 0 run return 0" % st, "execute if score #gt le.e < %s run return 0" % cd, "scoreboard players set %s 1" % st, "scoreboard players set %s 0" % tt, "scoreboard players operation %s = #gt le.e" % cd, "scoreboard players add %s 400" % cd]
        inn += start + ["function last_ember:trap/shield"]; fire += start
        tk += ["scoreboard players add %s 1" % tt, "execute if score %s matches 1 %spositioned %s run playsound minecraft:block.fire.extinguish block @a[distance=..20] ~ ~ ~ 1.2 0.5" % (tt, IN, cxyz)]
        for (vx, vy, vz) in V:
            tk.append("execute if score %s matches 5 %ssummon minecraft:area_effect_cloud %d.5 %d.2 %d.5 {Radius:2.2f,RadiusPerTick:0.0f,RadiusOnUse:0.0f,Duration:160,WaitTime:0,ReapplicationDelay:20,custom_particle:{type:\"minecraft:happy_villager\"},potion_contents:{custom_color:3398744,custom_effects:[{id:\"minecraft:poison\",amplifier:0,duration:120,show_particles:0b}]}}" % (tt, IN, vx, vy, vz))
        tk += ["execute if score %s matches 170.. run scoreboard players set %s 0" % (tt, st)]
        for (vx, vy, vz) in V: hint.append("%sparticle minecraft:spore_blossom_air %d.5 %d.3 %d.5 0.2 0.1 0.2 0.0 2 normal" % (IN, vx, vy, vz))
        reset += ["%skill @e[type=minecraft:area_effect_cloud,%s]" % (IN, t["sel"].replace("dx", "dx"))]
    elif T == "lava":
        B = C(P["back"]); CH = [C(c) for c in P["chan"].split(";")]
        start = ["execute unless score %s matches 0 run return 0" % st, "execute if score #gt le.e < %s run return 0" % cd, "scoreboard players set %s 1" % st, "scoreboard players set %s 0" % tt, "scoreboard players operation %s = #gt le.e" % cd, "scoreboard players add %s 1200" % cd, "function last_ember:trap/shield"]
        inn += start; fire += start
        bsel = boxsel(*B)
        tk += ["scoreboard players add %s 1" % tt, "execute if score %s matches 1 %spositioned %s run playsound minecraft:block.lava.ambient block @a[distance=..20] ~ ~ ~ 1.4 0.5" % (tt, IN, cxyz),
               "execute if score %s matches 1..19 %spositioned %s run particle minecraft:smoke ~ ~1 ~ %.1f 0.5 %.1f 0.02 6 force" % (tt, IN, cxyz, (t["x2"] - t["x1"] + 1) / 2, (t["z2"] - t["z1"] + 1) / 2)]
        fl = ["%sfill %d %d %d %d %d %d minecraft:lava replace minecraft:air" % ((IN,) + tuple(c)) for c in CH]
        tk += ["execute if score %s matches 20 %sif entity @a[%s] unless score %s matches 120.. run scoreboard players set %s 19" % (tt, IN, bsel, tt, tt),
               "execute if score %s matches 20 %spositioned %s run playsound minecraft:block.lava.pop block @a[distance=..20] ~ ~ ~ 1.4 0.6" % (tt, IN, cxyz)]
        tk += ["execute if score %s matches 20 run function last_ember:trap/gen/rise_%s" % (tt, i)]
        w("rise_" + i, fl + ["%sfill %d %d %d %d %d %d minecraft:lava replace minecraft:air" % ((IN,) + tuple(B))])
        clear = ["%sfill %d %d %d %d %d %d minecraft:air replace minecraft:lava" % ((IN,) + tuple(c)) for c in CH + [B]]
        w("clear_" + i, clear)
        tk += ["execute if score %s matches 430 run function last_ember:trap/gen/clear_%s" % (tt, i), "execute if score %s matches 431.. run scoreboard players set %s 0" % (tt, st)]
        reset += clear
        hint += ["%sparticle minecraft:smoke %d %d %d 1 0.2 1 0.01 1 normal" % (IN, c[0], c[1] + 1, c[2]) for c in CH]
    elif T == "cursed_chest":
        kx, ky, kz = C(P["chest"]); mob = P.get("mob", "minecraft:zombie"); mob2 = P.get("mob2", mob)   # T-026: mob2 = every second mob
        build += ["%sexecute unless entity @e[type=minecraft:marker,tag=le.cc,scores={le.tid=%d}] run summon minecraft:marker %d.5 %d.5 %d.5 {Tags:[\"le.cc\"]}" % (IN, n, kx, ky, kz),
                  "%sscoreboard players set @e[type=minecraft:marker,tag=le.cc,distance=..0.1,x=%d,y=%d,z=%d,limit=1] le.tid %d" % (IN, kx, ky, kz, n) if False else
                  "%sexecute positioned %d %d %d as @e[type=minecraft:marker,tag=le.cc,distance=..2,limit=1] unless score @s le.tid matches 1.. run scoreboard players set @s le.tid %d" % (IN, kx, ky, kz, n)]
        w("open_" + i, ["# the first opening of the cursed chest: mobs 2 + 1 per player within 16", "execute unless score %s matches 0 run return 0" % st, "scoreboard players set %s 2" % st,
                        "%sexecute positioned %d %d %d store result score #cnt le.tr if entity @a[distance=..16]" % (IN, kx, ky, kz), "scoreboard players add #cnt le.tr 2",
                        "%sexecute positioned %d %d %d run function last_ember:trap/spawn_ring {mob:\"%s\",mob2:\"%s\"}" % (IN, kx, ky, kz, mob, mob2),
                        "%spositioned %d %d %d run playsound minecraft:entity.wither.ambient block @a[distance=..20] ~ ~ ~ 0.8 0.6" % (IN, kx, ky, kz),
                        "%spositioned %d %d %d run particle minecraft:soul ~ ~1 ~ 1 0.5 1 0.05 30 force" % (IN, kx, ky, kz)])
        fire += ["function last_ember:trap/gen/open_%s" % i]
        hint += ["%sexecute positioned %d %d %d as @a[distance=..4] if predicate last_ember:chance_30 at @s run function last_ember:halluc/whisper" % (IN, kx, ky, kz)]
        reset += ["scoreboard players set %s 0" % st]
        t["chest"] = (kx, ky, kz)
    elif T == "false_treasure":
        px, py, pz = C(P["pos"]); link = P.get("link", "")
        build += ["%sexecute unless entity @e[type=minecraft:interaction,tag=le.ft,scores={le.tid=%d}] run summon minecraft:interaction %d.5 %d %d.5 {width:0.8f,height:0.8f,response:1b,Tags:[\"le.ft\",\"le.ftnew\"]}" % (IN, n, px, py, pz),
                  "%sscoreboard players set @e[type=minecraft:interaction,tag=le.ftnew,limit=1] le.tid %d" % (IN, n), "%sexecute as @e[tag=le.ftnew] run tag @s remove le.ftnew" % IN,
                  "%sexecute unless entity @e[type=minecraft:item_display,tag=le.ftd,scores={le.tid=%d}] run summon minecraft:item_display %d.5 %d.5 %d.5 {Tags:[\"le.ftd\",\"le.ftnew\"],billboard:\"vertical\",brightness:{sky:15,block:15},item:{id:\"minecraft:gold_block\",count:1},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.6f,0.6f,0.6f]}}" % (IN, n, px, py, pz) if False else
                  "%sexecute unless entity @e[type=minecraft:item_display,tag=le.ftd,scores={le.tid=%d}] run summon minecraft:item_display %d.5 %d.5 %d.5 {Tags:[\"le.ftd\",\"le.ftnew\"],billboard:\"vertical\",brightness:{sky:15,block:15},item:{id:\"minecraft:gold_block\",count:1},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.6f,0.6f,0.6f]}}" % (IN, n, px, py + 0.2, pz),
                  "%sscoreboard players set @e[type=minecraft:item_display,tag=le.ftnew,limit=1] le.tid %d" % (IN, n), "%sexecute as @e[tag=le.ftnew] run tag @s remove le.ftnew" % IN]
        w("ftc_" + i, ["# as the treasure's interaction at itself, the player is @a[tag=le.clicker]", "execute unless score %s matches 0 run return 0" % st,
                       "execute if entity @a[tag=le.clicker,tag=le.race.halfling] run return run playsound minecraft:block.amethyst_block.chime block @a[distance=..8] ~ ~ ~ 0.6 1.8",
                       "scoreboard players set %s 2" % st, "particle minecraft:block{block_state:\"minecraft:gold_block\"} ~ ~0.3 ~ 0.3 0.3 0.3 0.1 30 force", "particle minecraft:poof ~ ~0.3 ~ 0.3 0.3 0.3 0.05 12 force",
                       "playsound minecraft:block.sand.break block @a[distance=..16] ~ ~ ~ 1 0.7",
                       "%skill @e[type=minecraft:item_display,tag=le.ftd,scores={le.tid=%d}]" % (IN, n), "kill @s"] + (["function last_ember:trap/gen/fire_%s" % link] if link else []))
        fire += ["function last_ember:trap/gen/fire_%s" % link if link else "# nothing"]
        reset += ["scoreboard players set %s 0" % st, "%skill @e[type=minecraft:interaction,tag=le.ft,scores={le.tid=%d}]" % (IN, n), "%skill @e[type=minecraft:item_display,tag=le.ftd,scores={le.tid=%d}]" % (IN, n), "scoreboard players set %s 0" % bl]
        hint += ["%sparticle minecraft:wax_off %d.5 %d.6 %d.5 0.12 0.1 0.12 0.0 1 normal" % (IN, px, py, pz)]
        t["ft"] = True
    w("in_" + i, inn); w("tk_" + i, tk); w("hint_" + i, hint); w("fire_" + i, fire if len(fire) > 1 else fire + ["# nothing"]); w("build_" + i, build); w("reset_" + i, reset)
    build_p.append("execute if score %s matches 0 %sif loaded %s run function last_ember:trap/gen/build_%s" % (bl, IN, cxyz, i))
    tick.append("execute if score %s matches 1.. run function last_ember:trap/gen/tk_%s" % (st, i) if T in ("pit", "collapse") else "execute if score %s matches 1 run function last_ember:trap/gen/tk_%s" % (st, i))
    hints.append("execute %spositioned %s if entity @a[distance=..24] run function last_ember:trap/gen/hint_%s" % (IN, cxyz, i))
w("build_pending", build_p); w("slow", slow); w("hints", hints); w("tick", tick)
# the cursed chests: who opened a chest (the statistic) and looks at it
scan = ["# generated: every 5 ticks: a player whose 'chests opened' grew and who looks at a cursed chest within 6 blocks opens its curse"]
for t in traps:
    if t["type"] == "cursed_chest":
        scan.append("execute %spositioned %d %d %d as @a[distance=..7] if score @s le.chop > @s le.chopl run function last_ember:trap/ray_chest {n:%d,i:\"%s\"}" % (t["IN"], *t["chest"], t["n"], t["id"]))
w("chest_scan", scan)
# firing by id (admin / links) and reset by id
w("fire", ["# macro id"]); open(os.path.join(GEN, "fire.mcfunction"), "w").write("# generated\n$function last_ember:trap/gen/fire_$(id)\n")
open(os.path.join(GEN, "reset.mcfunction"), "w").write("# generated\n$function last_ember:trap/gen/reset_$(id)\n")
w("reset_all", ["# generated"] + ["function last_ember:trap/gen/reset_%s" % t["id"] for t in traps])
w("ftc", ["# generated: as the interaction of a false treasure (n in le.tid), the player is @a[tag=le.clicker]"] + ["execute if score @s le.tid matches %d run function last_ember:trap/gen/ftc_%s" % (t["n"], t["id"]) for t in traps if t["type"] == "false_treasure"])
print("traps:", len(traps), "cells:", len(cells))
