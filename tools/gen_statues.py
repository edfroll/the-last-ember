#!/usr/bin/env python3
"""T-016: statues/statues.txt (or a given file) -> datapack function/statue/gen/* (generated, do not edit).
Usage: python3 tools/gen_statues.py [statues_file]     (the test statues: statues/test_statues.txt; regenerate without them before a commit)"""
import os, re, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, "datapack/data/last_ember"); GEN = os.path.join(DP, "function/statue/gen")
shutil.rmtree(GEN, ignore_errors=True); os.makedirs(GEN, exist_ok=True)
def w(name, lines): open(os.path.join(GEN, name + ".mcfunction"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "statues/statues.txt")
DIMS = ("overworld", "the_nether", "the_end")
sts = []
for ln, l in enumerate(open(src, encoding="utf-8"), 1):
    l = l.split("#", 1)[0].strip()
    if not l: continue
    f = l.split(); P = dict(p.split("=", 1) for p in f[8:])
    if f[1] not in DIMS or f[7] not in ("item", "random", "event"): raise SystemExit(f"{src}:{ln}: bad dimension or mode")
    s = dict(id=f[0], dim=f[1], x=int(f[2]), y=int(f[3]), z=int(f[4]), mob=f[5], yaw=float(f[6]), mode=f[7], P=P, n=len(sts) + 1)
    s["group"] = P.get("group", ""); s["name"] = P.get("name", "Каменный страж").replace("_", " "); s["radius"] = int(P.get("radius", 6)); s["stats"] = P.get("stats", "elite"); s["respawn"] = P.get("respawn", "0")
    if s["mode"] in ("random", "event") and not s["group"]: raise SystemExit(f"{src}:{ln}: mode {s['mode']} needs group=")
    sts.append(s)
if len({s["id"] for s in sts}) != len(sts): raise SystemExit("duplicate statue id")
groups = {}
for s in sts:
    if s["group"]: groups.setdefault(s["group"], []).append(s)
def IN(s): return "in minecraft:%s " % s["dim"]
def S(s, k): return "#%s_%s le.st" % (s["id"], k)
COLOR = 9079434
init = ["# generated: the state of every statue (kept over reloads)"]
for s in sts:
    for k in ("st", "t", "bl"): init.append("execute unless score %s matches -2147483648..2147483647 run scoreboard players set %s 0" % (S(s, k), S(s, k)))
for g in groups: init.append("execute unless score #%s_cd le.st matches -2147483648..2147483647 run scoreboard players set #%s_cd le.st 0" % (g, g))
w("init", init)
items = sorted({s["P"]["item"] for s in sts if s["mode"] == "item"})
build_p = ["# generated: statues whose chunk is loaded are put on their pedestals once (every second)"]; tick = ["# generated: every tick: the statues that are waking up"]; slow = ["# generated: every second: awake statues go home when nobody is near; the killed ones are noticed"]
check = ["# generated: every 5 ticks: the protection of the carriers of every statue item, then the statues of the item mode and the groups of the random mode"]
for k, it in enumerate(items): check.append("function last_ember:statue/gen/prot_%d" % k); w("prot_%d" % k, ["# players within 10 blocks of a carrier of %s are protected (tag le.prot%d)" % (it, k), "tag @a remove le.prot%d" % k,
                                                                                         "execute as @a if items entity @s container.* *[minecraft:custom_data~{%s}] at @s run tag @a[distance=..10] add le.prot%d" % (it, k),
                                                                                         "execute as @a if items entity @s weapon.offhand *[minecraft:custom_data~{%s}] at @s run tag @a[distance=..10] add le.prot%d" % (it, k)])
for s in sts:
    i, X, Y, Z = s["id"], s["x"], s["y"], s["z"]; pos = "%d %d %d" % (X, Y, Z); IN_ = IN(s)
    arm = "".join('%s:{id:"minecraft:leather_%s",count:1,components:{"minecraft:dyed_color":%d}},' % (slot, piece, COLOR) for slot, piece in (("head", "helmet"), ("chest", "chestplate"), ("legs", "leggings"), ("feet", "boots")))[:-1]
    build = ["# generated: the statue %s on its pedestal" % i, "scoreboard players set %s 1" % S(s, "bl"),
             "execute %sunless entity @e[tag=le.st_%s] run summon %s %d.5 %d %d.5 {NoAI:1b,Silent:1b,Invulnerable:1b,PersistenceRequired:1b,Rotation:[%.1ff,0.0f],CanPickUpLoot:0b,Tags:[\"le.statue\",\"le.noelite\",\"le.st_%s\"],equipment:{%s},drop_chances:{head:0.0f,chest:0.0f,legs:0.0f,feet:0.0f,mainhand:0.0f,offhand:0.0f}}" % (IN_, i, s["mob"], X, Y, Z, s["yaw"], i, arm),
             "execute %sas @e[tag=le.st_%s,limit=1] run scoreboard players set @s le.sid %d" % (IN_, i, s["n"]), "scoreboard players set %s 0" % S(s, "st")]
    w("build_" + i, build)
    build_p.append("execute if score %s matches 0 %sif loaded %s run function last_ember:statue/gen/build_%s" % (S(s, "bl"), IN_, pos, i))
    wake = ["# generated: wake the statue %s (stone dust and a scrape, 1 s later it lives)" % i, "execute unless score %s matches 0 run return 0" % S(s, "st"), "scoreboard players set %s 3" % S(s, "st"), "scoreboard players set %s 0" % S(s, "t"),
            "execute %spositioned %s run particle minecraft:block{block_state:\"minecraft:stone\"} ~ ~1 ~ 0.4 0.7 0.4 0.05 40 force" % (IN_, pos),
            "execute %spositioned %s run playsound minecraft:block.grindstone.use block @a[distance=..24] ~ ~ ~ 1.4 0.5" % (IN_, pos)]
    w("wake_" + i, wake)
    tk = ["# generated: one tick of the waking of %s" % i, "scoreboard players add %s 1" % S(s, "t"),
          "execute if score %s matches 10 %spositioned %s run particle minecraft:block{block_state:\"minecraft:stone\"} ~ ~1 ~ 0.4 0.7 0.4 0.05 30 force" % (S(s, "t"), IN_, pos),
          "execute if score %s matches 20.. run function last_ember:statue/gen/live_%s" % (S(s, "t"), i)]
    w("tk_" + i, tk)
    live = ["# generated: the statue %s lives" % i, "scoreboard players set %s 1" % S(s, "st"),
            "execute %sas @e[tag=le.st_%s,limit=1] run function last_ember:statue/live" % (IN_, i)]
    if s["stats"] == "elite": live.append("execute %sas @e[tag=le.st_%s,limit=1] at @s run function last_ember:statue/make_elite" % (IN_, i))
    live.append("execute %sas @e[tag=le.st_%s,limit=1] run data modify entity @s CustomName set value '{\"text\":\"%s\",\"color\":\"dark_red\"}'" % (IN_, i, s["name"]))
    live.append("execute %sas @e[tag=le.st_%s,limit=1] run data modify entity @s CustomNameVisible set value 1b" % (IN_, i))
    w("live_" + i, live)
    ret = ["# generated: nobody within 32 blocks: the statue %s goes back to its pedestal, stone again, with full health" % i, "scoreboard players set %s 0" % S(s, "st"),
           "execute %sas @e[tag=le.st_%s,limit=1] run function last_ember:statue/stone" % (IN_, i),
           "execute %sas @e[tag=le.st_%s,limit=1] run tp @s %d.5 %d %d.5 %.1f 0" % (IN_, i, X, Y, Z, s["yaw"])]
    w("return_" + i, ret)
    rst = ["# generated: statue %s back to the start (a new one on the pedestal)" % i, "execute %srun kill @e[tag=le.st_%s]" % (IN_, i) if False else "execute %sas @e[tag=le.st_%s] run kill @s" % (IN_, i), "scoreboard players set %s 0" % S(s, "bl"), "scoreboard players set %s 0" % S(s, "st"), "scoreboard players set %s 0" % S(s, "t")]
    w("reset_" + i, rst)
    tick.append("execute if score %s matches 3 run function last_ember:statue/gen/tk_%s" % (S(s, "st"), i))
    slow.append("execute if score %s matches 1 %sif loaded %s unless entity @a[distance=..32,x=%d,y=%d,z=%d] run function last_ember:statue/gen/return_%s" % (S(s, "st"), IN_, pos, X, Y, Z, i) if False else
                "execute if score %s matches 1 %sif loaded %s positioned %s unless entity @a[distance=..32] run function last_ember:statue/gen/return_%s" % (S(s, "st"), IN_, pos, pos, i))
    slow.append("execute if score %s matches 1 %sif loaded %s unless entity @e[tag=le.st_%s] run scoreboard players set %s 2" % (S(s, "st"), IN_, pos, i, S(s, "st")))
    if s["mode"] == "item":
        k = items.index(s["P"]["item"])
        check.append("execute if score %s matches 0 %spositioned %s if entity @a[distance=..%d,tag=!le.prot%d,gamemode=!creative,gamemode=!spectator] run function last_ember:statue/gen/wake_%s" % (S(s, "st"), IN_, pos, s["radius"], k, i))
for g, ss in groups.items():
    w("wake_g_" + g, ["# generated: the whole group %s wakes" % g] + ["function last_ember:statue/gen/wake_%s" % s["id"] for s in ss])
    w("reset_g_" + g, ["# generated: the group %s starts over" % g] + ["function last_ember:statue/gen/reset_%s" % s["id"] for s in ss] + ["scoreboard players set #%s_cd le.st 0" % g])
    rs = [s for s in ss if s["mode"] == "random"]
    if rs:
        x1, x2 = min(s["x"] for s in rs) - 4, max(s["x"] for s in rs) + 4; y1, y2 = min(s["y"] for s in rs) - 2, max(s["y"] for s in rs) + 4; z1, z2 = min(s["z"] for s in rs) - 4, max(s["z"] for s in rs) + 4
        dim = rs[0]["dim"]
        check.append("execute if score #%s_cd le.st matches ..0 in minecraft:%s as @a[gamemode=!creative,gamemode=!spectator,x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d] at @s run function last_ember:statue/gen/pass_%s" % (g, dim, x1, y1, z1, x2 - x1, y2 - y1, z2 - z1, g))
        P_ = ["# generated: a player is in the area of the group %s: one random statue behind him (more than 120 degrees from his view) wakes" % g, "scoreboard players set #pick le.st 0", "scoreboard players set #cnt le.st 0"]
        for s in rs:
            P_ += ["scoreboard players set #bh le.st 0", "execute if score %s matches 0 run function last_ember:statue/behind {id:\"%s\"}" % (S(s, "st"), s["id"]),
                   "execute if score #bh le.st matches 1 run scoreboard players add #cnt le.st 1", "execute if score #bh le.st matches 1 run scoreboard players set %s 4" % S(s, "st")]
        # the candidates are marked with st = 4; one of them is picked by chance
        P_ += ["execute if score #cnt le.st matches 0 run return 0", "execute store result score #r le.st run random value 1..%d" % len(rs), "scoreboard players operation #r le.st %= #cnt le.st", "scoreboard players add #r le.st 1", "scoreboard players set #k le.st 0", "scoreboard players set #pk le.st 0"]
        for s in rs:
            P_ += ["execute if score %s matches 4 run scoreboard players add #k le.st 1" % S(s, "st"),
                   "execute if score %s matches 4 if score #k le.st = #r le.st if score #pk le.st matches 0 run function last_ember:statue/gen/pick_%s" % (S(s, "st"), s["id"])]
            w("pick_" + s["id"], ["# the chosen one of the random group", "scoreboard players set %s 0" % S(s, "st"), "scoreboard players set #pk le.st 1", "function last_ember:statue/gen/wake_%s" % s["id"]])
        for s in rs: P_.append("execute if score %s matches 4 run scoreboard players set %s 0" % (S(s, "st"), S(s, "st")))
        P_ += ["scoreboard players set #%s_cd le.st 2400" % g]
        w("pass_" + g, P_)
w("build_pending", build_p); w("tick", tick); w("slow", slow); w("check", check)
w("wake_dispatch", ["# macro group"]); open(os.path.join(GEN, "wake_dispatch.mcfunction"), "w").write("# generated\n$function last_ember:statue/gen/wake_g_$(group)\n")
open(os.path.join(GEN, "reset_dispatch.mcfunction"), "w").write("# generated\n$function last_ember:statue/gen/reset_g_$(group)\n")
w("cooldowns", ["# generated: every second: the cooldown of every random group runs down"] + ["execute if score #%s_cd le.st matches 1.. run scoreboard players remove #%s_cd le.st 20" % (g, g) for g in groups if any(s["mode"] == "random" for s in groups[g])])
print("statues:", len(sts), "groups:", list(groups), "item protections:", len(items))
