"""T-031: the datapack part of the Village of Heather, written by tools/build/r1_heather.py: function/heather/gen/*, dialog/heather/*,
function/heather/hook/hunter_saved (a stub, written only when the file is missing: the task of the Spider Thicket writes it).
Generated, do not edit. The hand-written logic: function/heather/*.mcfunction.

Scores (objective le.hv, fake players): #near players near the village (the loop works only then), #t the loop counter, #sec seconds,
#df the difficulty (0 peaceful), #dt / #pdt the day time now / a second ago, #frz seconds of the midnight freeze left, #ms the step of the
sails (0..7), #met the generation of the acquaintances (heather/reset: +1), #rgen the generation of the ringer's entities, #rmiss
seconds he was missing, and per point N of the dead villagers: #gN the generation of its zombie, #sN 1 = spawned (alive or unloaded),
#dN 1 = killed (comes back at the next dawn: #day > #kN, the day it was killed), #mN seconds it was missing at a loaded point. Entities: the dead villagers (zombie_villager
le.hz + le.hz_N, le.hn = N, le.hgen = #gN, le.hyaw = the base yaw; le.hzr resting (NoAI), le.hza awake, le.hfrz frozen by the bell);
the ringer (villager le.ringer + interaction le.htalk, both le.hrent with le.hrg = #rgen); the sails (block_display le.hblade + le.hbl_K,
le.hrent); the scarecrows (armor_stand le.hscare + le.hsc_K, le.hrent). Players: le.htrig (trigger: 1 who are you, 2 the village,
3 «Найдём», 4 the menu, 5 the grandson), tag le.hmet + le.hmetg = #met, le.hwin the last window shown (1 intro, 2 about, 3 village,
4 menu, 5 grandson: quest taken, 6 grandson: not taken). The quest: storage last_ember:heather q (0 not taken, 1 taken, 2 the hunter
saved - the Spider Thicket, 3 rewarded)."""
import json, math, os

def tx(t, color="white", italic=False): return {"text": t, "color": color, "italic": italic}
NAME = "Звонарь"
DLG = {   # HQ T-031, 4: word for word
    "intro": "Живые? Поднимайтесь, не бойтесь. Внизу все свои, только давно себя не помнят. Я звоню им в полночь. Колокол им напоминает, и они на миг вспоминают.",
    "about": "Звонарь. Был ещё внук, Тойво, охотник. Ушёл в белый лес на юго-востоке и не вернулся. Лук у него приметный, тетива зелёная. Найдёте его — буду звонить и за вас.",
    "village": "Огонь ушёл, и всё стало немного не так. Сначала двери. Потом лестницы. Потом люди. Мы не замечали. А когда заметили, сказать было уже некому.",
    "menu": "Колокол ещё цел. И я пока цел.",
    "grandson": "Белый лес за ручьём, на юго-востоке. Там всё белое, не ошибётесь. Тойво не трус. Если он там, значит, его там держат.",
}
NOTES = {   # HQ T-031, 5: (author, title, text)
    1: ("Марта", "Записка", "Сегодня замуровали дверь, чтобы дом не ушёл. Окно оставили. Надо же как-то входить."),
    2: ("Ян", "Записка", "Лестницу сделали честную, до самого верха. Верх просто стал ниже. Спим теперь на стене: там никто не ходит."),
    3: ("Хозяйка", "Записка", "Ужинаем на крыше. Внизу за нашим столом всё время кто-то сидит. Мы не мешаем."),
    4: ("Отец", "Записка", "Под домом нашли дом. В нём тоже горит свет. Не спускаемся: там, наверное, ужинают."),
    5: ("Бран, ученик", "Записка", "Мастер Хальвард велел без железа не возвращаться. Говорят, к востоку от Приюта есть старые шахты. Ночую на колокольне: звонарь пускает. Ночью все внизу стоят и слушают. Утром ухожу."),
    6: ("Тойво", "Записка", "Дед, я в белый лес. Там пауки таскают дичь, а может, и не только дичь. К ночи вернусь. P.S. У дороги к Броду кости лежат цепочкой. Посмотрю потом, куда ведут."),
}
YAW = {"south": 0.0, "west": 90.0, "north": 180.0, "east": -90.0}
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}
HAT = '{id:"minecraft:stick",count:1,components:{"minecraft:item_model":"last_ember:heather_none","minecraft:custom_data":{le_hat:1b}}}'

def pages(text, n=200):
    """split a note into pages of <= n characters at word boundaries"""
    out = []; cur = ""
    for w in text.split(" "):
        if len(cur) + len(w) + 1 > n and cur: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    if cur: out.append(cur)
    return out

def zombie_points(meta, pl):
    """10..12 points «at work» (HQ T-031, 3): (x, y, z, yaw, profession, where); y = the feet level"""
    P = []
    g = meta["gardens"]
    for k, face in (("garden1", "north"), ("garden2", "north"), ("garden3", "south")):
        r = g[k]["r"]; L = g[k]["L"]
        z = r[3] if face == "north" else r[1]
        P.append((r[0] + 3, L + 1, z, YAW[face], "farmer", k))
    m = meta["mill"]; d = m["door"]
    P.append((d[0] - 1, d[1], d[2], YAW["east"], "mason", "mill"))
    wx, wy, wz = meta["well"]
    P.append((wx + 3, wy - 0, wz + 1, YAW["west"], "nitwit", "well"))
    ch = meta["church"]
    bs = sorted(ch["benches"], key=lambda q: (q[0], q[2]))
    for q in (bs[1], bs[len(bs) // 2 + 2]):
        P.append((q[0], q[1] + 0.5, q[2], YAW["north"], "cleric", "bench"))
    pa = meta["pasture"]; sc = meta.get("scarecrows", [])
    if sc:
        x, y, z = sc[0]; P.append((x + 2, y, z, YAW["west"], "shepherd", "scarecrow"))
    for h in meta["houses"]:
        if h["kind"] == "ladder" and "threshold" not in [p[5] for p in P]:
            fx, fz = h["front"]; P.append((fx, h["L"] + 1, fz, YAW[h["face"]], "librarian", "threshold"))
        if h["kind"] == "roof" and "roof" not in [p[5] for p in P]:
            x, y, z = h["roof_chair"]; t = h["roof_table"]
            P.append((x, y + 0.5, z, math.degrees(math.atan2(-(t[0] - x), t[2] - z)), "butcher", "roof"))
        if h["kind"] == "deep" and "ledge" not in [p[5] for p in P]:
            x, y, z = h["lectern"]; P.append((x, y, z, YAW[OPP[h["face"]]], "armorer", "ledge"))
        if h["kind"] == "reversed" and "hearth" not in [p[5] for p in P]:
            x, y, z = h["inside"]; P.append((x, y, z, YAW[OPP[h["face"]]], "toolsmith", "hearth"))
    return [(x, y, z, round(yaw, 1), prof, where) for (x, y, z, yaw, prof, where) in P][:12]

def scarecrow_points(meta, ground):
    pa = meta["pasture"]["r"]; px1, pz1, px2, pz2 = meta["pasture"]["pen"]
    pts = []
    cand = [(pa[0] + 3, pa[1] + 3), (pa[0] + 6, pa[3] - 3), (pa[0] + 3, pa[3] - 6), (pa[0] + 8, pa[1] + 4)]
    for (x, z) in cand:
        if px1 - 1 <= x <= px2 + 1 and pz1 - 1 <= z <= pz2 + 1: continue
        pts.append((x, ground(x, z) + 1, z))
    return pts[:4]

def run(meta):
    import r1_heather as R
    ROOT, DP = R.ROOT, R.DP
    GEN = os.path.join(DP, "function/heather/gen"); os.makedirs(GEN, exist_ok=True)
    for f in os.listdir(GEN):
        if f.endswith(".mcfunction"): os.remove(os.path.join(GEN, f))
    hdr = "# generated by tools/build/r1_heather.py (heather_dp.py): "
    def w(name, lines): open(os.path.join(GEN, name + ".mcfunction"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    ch = meta["church"]; bell = ch["bell"]; rx, ry, rz = ch["ringer"]
    vx1, vz1, vx2, vz2 = 20, -515, 120, -425
    zlo, zhi = meta["zone"]
    VBOX = "x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d" % (vx1, zlo, vz1, vx2 - vx1 + 1, zhi - zlo + 1, vz2 - vz1 + 1)
    meta["vbox"] = VBOX
    pts = meta["zombies_pts"]
    meta["zombies"] = [dict(n=k + 1, pos=[p[0] + 0.5, p[1], p[2] + 0.5], yaw=p[3], prof=p[4], where=p[5]) for k, p in enumerate(pts)]
    # ---- the dead villagers: one function per point (the arguments of a macro would be re-parsed for > 8 points, CLAUDE.md: Нагрузка)
    for z in meta["zombies"]:
        n = z["n"]; x, y, zz = z["pos"]; yaw = z["yaw"]
        w("spawn_%d" % n, [hdr + "the dead villager %d (%s) on his point: resting (NoAI), the hat against the sun, no drop of it" % (n, z["where"]),
                           "scoreboard players add #g%d le.hv 1" % n,
                           "kill @e[type=minecraft:zombie_villager,tag=le.hz_%d]" % n,
                           'summon minecraft:zombie_villager %.1f %.2f %.1f {Tags:["le.hz","le.hz_%d","le.hzr","le.noelite","le.eq_done","le.rolled","le.hznew"],NoAI:1b,PersistenceRequired:1b,CanPickUpLoot:0b,IsBaby:0b,CanBreakDoors:0b,Rotation:[%.1ff,0f],VillagerData:{type:"minecraft:plains",profession:"minecraft:%s",level:1},equipment:{head:%s},drop_chances:{head:0.0f}}' % (x, y, zz, n, yaw, z["prof"], HAT),
                           "scoreboard players set @e[type=minecraft:zombie_villager,tag=le.hznew] le.hn %d" % n,
                           "scoreboard players set @e[type=minecraft:zombie_villager,tag=le.hznew] le.hyaw %d" % int(round(yaw)),
                           "scoreboard players operation @e[type=minecraft:zombie_villager,tag=le.hznew] le.hgen = #g%d le.hv" % n,
                           "tag @e[type=minecraft:zombie_villager,tag=le.hznew] remove le.hznew",
                           "scoreboard players set #s%d le.hv 1" % n, "scoreboard players set #d%d le.hv 0" % n, "scoreboard players set #m%d le.hv 0" % n])
        w("pt_%d" % n, [hdr + "every second: point %d - alive, missing (3 s at a loaded point: killed), killed (back at the next dawn, nobody within 48)" % n,
                        "execute unless loaded %d %d %d run return 0" % (int(x // 1), int(y), int(zz // 1)),
                        "execute store result score #c le.hv if entity @e[type=minecraft:zombie_villager,tag=le.hz_%d]" % n,
                        "execute if score #c le.hv matches 1.. run return run scoreboard players set #m%d le.hv 0" % n,
                        "execute if score #df le.hv matches 0 run return 0",
                        "execute if score #s%d le.hv matches 0 if score #d%d le.hv matches 0 run return run function last_ember:heather/gen/spawn_%d" % (n, n, n),
                        "execute if score #s%d le.hv matches 1 run scoreboard players add #m%d le.hv 1" % (n, n),
                        "execute if score #s%d le.hv matches 1 if score #m%d le.hv matches 3.. run scoreboard players operation #k%d le.hv = #day le.hv" % (n, n, n),
                        "execute if score #s%d le.hv matches 1 if score #m%d le.hv matches 3.. run scoreboard players set #d%d le.hv 1" % (n, n, n),
                        "execute if score #s%d le.hv matches 1 if score #m%d le.hv matches 3.. run scoreboard players set #s%d le.hv 0" % (n, n, n),
                        "execute if score #d%d le.hv matches 1 if score #dt le.hv matches 0..1000 if score #day le.hv > #k%d le.hv unless entity @a[gamemode=!spectator,x=%.1f,y=%.1f,z=%.1f,distance=..48] run function last_ember:heather/gen/spawn_%d" % (n, n, x, y, zz, n)])
        w("home_%d" % n, [hdr + "the dead villager %d back on his point, healed, resting" % n,
                          "tp @s %.2f %.2f %.2f %.1f 0" % (x, y, zz, yaw)])
    I = [hdr + "the scores of the points (load: only those not set yet)"]
    for z in meta["zombies"]:
        for k in ("g", "s", "d", "m", "k"): I.append("execute unless score #%s%d le.hv = #%s%d le.hv run scoreboard players set #%s%d le.hv 0" % (k, z["n"], k, z["n"], k, z["n"]))
    w("init", I)
    w("points", [hdr + "every second (players near): the points of the dead villagers"] + ["function last_ember:heather/gen/pt_%d" % z["n"] for z in meta["zombies"]])
    w("home", [hdr + "as a dead villager: to his point (by le.hn)"] +
      ["execute if score @s le.hn matches %d run function last_ember:heather/gen/home_%d" % (z["n"], z["n"]) for z in meta["zombies"]])
    w("dawn_all", [hdr + "admin (heather/reset): every point spawns now"] + ["function last_ember:heather/gen/spawn_%d" % z["n"] for z in meta["zombies"]])
    w("forget", [hdr + "peaceful: the dead villagers vanish (monsters); not killed - they come back at once on easy+"] +
      ["scoreboard players set #s%d le.hv 0" % z["n"] for z in meta["zombies"]])
    # ---- the near test, the zone box, the bell
    cx, cz = (vx1 + vx2) // 2, (vz1 + vz2) // 2
    w("near", [hdr + "#near = players near the village (box + 40), #nb = players within 96 of the bell",
               "execute store result score #near le.hv if entity @a[x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d]" % (vx1 - 40, zlo - 30, vz1 - 70, vx2 - vx1 + 80, zhi - zlo + 80, vz2 - vz1 + 110),
               "execute store result score #nb le.hv if entity @a[x=%.1f,y=%.1f,z=%.1f,distance=..96]" % (bell[0] + 0.5, bell[1] + 0.5, bell[2] + 0.5)])
    w("hats", [hdr + "every second: zombies and zombie villagers in the zone heather get the hat (nothing on the head: no burning in the sun, fire of the players still burns); out of the zone ours is taken back",
               "execute as @e[type=#last_ember:heather_sunburn,%s] unless items entity @s armor.head * run function last_ember:heather/hat_on" % VBOX,
               "execute as @e[type=#last_ember:heather_sunburn,tag=le.hhat] unless entity @s[%s] run function last_ember:heather/hat_off" % VBOX])
    w("bell_sound", [hdr + "one stroke of the bell from the belfry (heard ~96 blocks: volume 6, T-018)",
                     "playsound minecraft:block.bell.use block @a %.1f %.1f %.1f 6 0.7" % (bell[0] + 0.5, bell[1] + 0.5, bell[2] + 0.5),
                     "playsound minecraft:block.bell.resonate block @a %.1f %.1f %.1f 3 0.8" % (bell[0] + 0.5, bell[1] + 0.5, bell[2] + 0.5)])
    w("freeze", [hdr + "after the first stroke: every dead thing of the zone (ours resting or awake, vanilla zombies and zombie villagers) stops 10 s facing the belfry",
                 "execute as @e[type=#last_ember:heather_sunburn,%s,tag=!le.hfrz] run function last_ember:heather/freeze_one" % VBOX,
                 "execute as @e[type=#last_ember:heather_sunburn,tag=le.hfrz] at @s run rotate @s facing %.1f %.1f %.1f" % (bell[0] + 0.5, bell[1] + 0.5, bell[2] + 0.5),
                 "scoreboard players set #frz le.hv 10"])
    w("face_bell", [hdr + "while frozen: still facing the belfry",
                    "execute as @e[type=#last_ember:heather_sunburn,tag=le.hfrz] at @s run rotate @s facing %.1f %.1f %.1f" % (bell[0] + 0.5, bell[1] + 0.5, bell[2] + 0.5)])
    # ---- the ringer
    MAN = ('{Tags:["le.npc","le.keep","le.noelite","le.ringer","le.hrent","le.hrnew"],NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,CanPickUpLoot:0b,'
           'Rotation:[%.1ff,0f],CustomName:{text:"%s",color:"gold"},CustomNameVisible:1b,VillagerData:{profession:"minecraft:nitwit",level:1,type:"minecraft:plains"},Offers:{Recipes:[]}}')
    yaw_r = math.degrees(math.atan2(-(bell[0] + 0.5 - rx), (bell[2] + 0.5 - rz)))
    meta["ringer"] = [rx, ry, rz, round(yaw_r, 1)]
    w("ringer_put", [hdr + "the ringer at the bell (a new generation: the old entities go wherever they are, now or when their chunk loads)",
                     "scoreboard players add #rgen le.hv 1", "kill @e[type=minecraft:villager,tag=le.ringer]", "kill @e[type=minecraft:interaction,tag=le.htalk]",
                     "summon minecraft:villager %.2f %.2f %.2f %s" % (rx, ry, rz, MAN % (yaw_r, NAME)),
                     'summon minecraft:interaction %.2f %.2f %.2f {Tags:["le.htalk","le.hrent","le.hrnew"],width:0.9f,height:2.0f,response:1b}' % (rx, ry, rz),
                     "scoreboard players operation @e[tag=le.hrnew] le.hrg = #rgen le.hv", "tag @e[tag=le.hrnew] remove le.hrnew",
                     "scoreboard players set #rmiss le.hv 0"])
    w("ringer_check", [hdr + "every second (the belfry loaded): the ringer of this generation at his place (else, after 2 s, a new one)",
                       "execute unless loaded %d %d %d run return 0" % (int(rx // 1), int(ry), int(rz // 1)),
                       "scoreboard players set #here le.hv 1",
                       "execute unless entity @e[type=minecraft:villager,tag=le.ringer,x=%.2f,y=%.2f,z=%.2f,distance=..1.5] run scoreboard players set #here le.hv 0" % (rx, ry + 0.5, rz),
                       "execute unless entity @e[type=minecraft:interaction,tag=le.htalk,x=%.2f,y=%.2f,z=%.2f,distance=..1.5] run scoreboard players set #here le.hv 0" % (rx, ry + 0.5, rz),
                       "execute if score #here le.hv matches 1 run scoreboard players set #rmiss le.hv 0",
                       "execute if score #here le.hv matches 0 run scoreboard players add #rmiss le.hv 1",
                       "execute if score #rmiss le.hv matches 2.. run function last_ember:heather/gen/ringer_put",
                       "execute as @e[type=minecraft:villager,tag=le.ringer,limit=1] run rotate @s %.1f 0" % yaw_r])
    w("ringer_near", [hdr + "@s within 6 of the ringer: #ok 1", "scoreboard players set #ok le.hv 0",
                      "execute if entity @e[type=minecraft:villager,tag=le.ringer,distance=..6] run scoreboard players set #ok le.hv 1"])
    # ---- the sails of the mill: 4 block displays on the hub, turned by interpolation (8 states of 90°, quaternions continuous: the
    # slerp always goes the short way forwards), counter-clockwise seen from the south (outside): + about +z
    ax, ay, az = meta["mill"]["axle"]
    Q = [(0.0, 0.0, round(math.sin(math.radians(45 * k)), 4), round(math.cos(math.radians(45 * k)), 4)) for k in range(8)]
    meta["mill"]["quats"] = Q
    for s in range(8):
        L = [hdr + "the sails, step %d of 8 (2 s each: a turn in 8 s)" % s]
        for n in range(4):
            q = Q[(s + n) % 8]
            L.append("data merge entity @e[type=minecraft:block_display,tag=le.hbl_%d,limit=1] {start_interpolation:0,interpolation_duration:40,transformation:{left_rotation:[%.4ff,%.4ff,%.4ff,%.4ff]}}" % ((n,) + q))
        w("mill_%d" % s, L)
    w("mill", [hdr + "every 2 s with a player within 64 of the hub: the next step of the sails (the sails stand when nobody is near)",
               "execute unless entity @a[x=%.2f,y=%.2f,z=%.2f,distance=..64] run return 0" % (ax, ay, az),
               "scoreboard players add #ms le.hv 1", "execute if score #ms le.hv matches 8.. run scoreboard players set #ms le.hv 0"] +
      ["execute if score #ms le.hv matches %d run function last_ember:heather/gen/mill_%d" % (s, s) for s in range(8)])
    SAIL = '{Tags:["le.hblade","le.hbl_%d","le.hrent"],block_state:"minecraft:spruce_planks",view_range:2.0f,transformation:{left_rotation:[%.4ff,%.4ff,%.4ff,%.4ff],right_rotation:[0f,0f,0f,1f],translation:[-0.65f,0.25f,0f],scale:[1.3f,6.5f,0.06f]},interpolation_duration:40}'
    w("sails_put", [hdr + "the 4 sails on the hub (missing / doubled: all again)", "kill @e[type=minecraft:block_display,tag=le.hblade]", "scoreboard players set #ms le.hv 0"] +
      ["summon minecraft:block_display %.2f %.2f %.2f %s" % (ax, ay, az, SAIL % ((n,) + Q[n % 8])) for n in range(4)])
    w("sails_check", [hdr + "every second (the hub loaded): 4 sails",
                      "execute unless loaded %d %d %d run return 0" % (int(ax // 1), int(ay), int(az // 1)),
                      "execute store result score #c le.hv if entity @e[type=minecraft:block_display,tag=le.hblade,x=%.2f,y=%.2f,z=%.2f,distance=..2]" % (ax, ay, az),
                      "execute unless score #c le.hv matches 4 run function last_ember:heather/gen/sails_put"])
    # ---- the scarecrows: armor stands with a pumpkin head and old dyed leather (no drop: invulnerable, slots disabled)
    sc = meta.get("scarecrows", [])
    cols = [7491371, 5658198, 8421422, 6045505]
    for k, (x, y, z) in enumerate(sc):
        w("scare_%d" % k, [hdr + "scarecrow %d" % k, "kill @e[type=minecraft:armor_stand,tag=le.hsc_%d]" % k,
                           'summon minecraft:armor_stand %.1f %d %.1f {Tags:["le.hscare","le.hsc_%d","le.hrent"],Invulnerable:1b,NoBasePlate:1b,ShowArms:1b,DisabledSlots:4144959,PersistenceRequired:1b,Rotation:[%.1ff,0f],Pose:{LeftArm:[0f,0f,-85f],RightArm:[0f,0f,85f],Head:[8f,12f,0f]},equipment:{head:{id:"minecraft:carved_pumpkin",count:1},chest:{id:"minecraft:leather_chestplate",count:1,components:{"minecraft:dyed_color":%d}},legs:{id:"minecraft:leather_leggings",count:1,components:{"minecraft:dyed_color":%d}}},drop_chances:{head:0.0f,chest:0.0f,legs:0.0f}}' % (x + 0.5, y, z + 0.5, k, 160.0 + 25 * k, cols[k % 4], cols[(k + 2) % 4])])
    L = [hdr + "every second: the scarecrows (one each: missing or doubled - again)"]
    for k, (x, y, z) in enumerate(sc):
        L.append("execute if loaded %d %d %d store result score #c le.hv if entity @e[type=minecraft:armor_stand,tag=le.hsc_%d]" % (x, y, z, k))
        L.append("execute if loaded %d %d %d unless score #c le.hv matches 1 run function last_ember:heather/gen/scare_%d" % (x, y, z, k))
    w("scare_check", L)
    w("genchk", [hdr + "as a dead villager: one of an old generation (a double from a chunk loaded late) goes"] +
      ["execute if score @s le.hn matches %d unless score @s le.hgen = #g%d le.hv run return run function last_ember:heather/vanish" % (z["n"], z["n"]) for z in meta["zombies"]])
    # ---- the tp points for the shots and the tests
    tps = {"bridge": (70.5, meta["bridge"]["south_y"] + 1, meta["bridge"]["z"][1] + 0.5), "square": (meta["well"][0] + 3.5, meta["well"][1], meta["well"][2] + 3.5),
           "church": (ch["door"][0] + 0.5, ch["door"][1], ch["door"][2] + 1.5), "belfry": (ch["ringer"][0] + 2.0, ch["ringer"][1], ch["ringer"][2]),
           "mouth": ((meta["mouth"][0] + meta["mouth"][2]) / 2 + 0.5, meta["mouth_y"], (meta["mouth"][1] + meta["mouth"][3]) / 2 + 0.5),
           "mill": (meta["mill"]["door"][0] - 2.5, meta["mill"]["door"][1], meta["mill"]["door"][2] + 0.5)}
    for k, (x, y, z) in tps.items():
        w("tp_%s" % k, [hdr + "admin: @s to %s" % k, "tp @s %.1f %.1f %.1f" % (x, y, z)])
    meta["tp"] = {k: list(v) for k, v in tps.items()}
    # ---- the notes on the lecterns: their blocks are written by the build; the sacristy's lectern too (heather_build writes
    # the books from NOTES through r1_heather: meta["lecterns"])
    # ---- dialogs (read at the server start only)
    DD = os.path.join(DP, "dialog/heather"); os.makedirs(DD, exist_ok=True)
    for f in os.listdir(DD): os.remove(os.path.join(DD, f))
    def dump(name, o): json.dump(o, open(os.path.join(DD, name + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    def msg(t): return {"type": "minecraft:plain_message", "contents": tx(t), "width": 300}
    def btn(label, n, color="green"): return {"label": tx(label, color), "width": 200, "action": {"type": "minecraft:run_command", "command": "trigger le.htrig set %d" % n}}
    title = tx(NAME, "gold"); leave = {"label": tx("Пойдём", "gray"), "width": 150}
    def multi(name, text, buttons, exit_=True):
        o = {"type": "minecraft:multi_action", "title": title, "body": [msg(text)], "can_close_with_escape": True, "pause": False,
             "after_action": "close", "columns": 1, "actions": buttons}
        if exit_: o["exit_action"] = leave
        dump(name, o)
    multi("intro", DLG["intro"], [btn("Кто ты?", 1), btn("Что с деревней?", 2)])
    multi("about", DLG["about"], [btn("Найдём", 3)])
    multi("village", DLG["village"], [btn("Ещё", 4)], exit_=False)
    multi("menu", DLG["menu"], [btn("Что с деревней?", 2), btn("О внуке", 5)])
    multi("grandson", DLG["grandson"], [btn("Ещё", 4)], exit_=False)
    meta["dialogs"] = sorted(os.listdir(DD))
    # ---- the hook for the Spider Thicket (a stub: never overwritten)
    HK = os.path.join(DP, "function/heather/hook"); os.makedirs(HK, exist_ok=True)
    hp = os.path.join(HK, "hunter_saved.mcfunction")
    if not os.path.exists(hp):
        open(hp, "w", encoding="utf-8").write("# T-031: the hook of the quest «Внук звонаря»: the task of the Spider Thicket calls it when the hunter Toivo is saved (q 2)\n"
                                              "# and writes the reward here (q 3). A stub until then: only the state.\n"
                                              "execute if data storage last_ember:heather {q:1} run data modify storage last_ember:heather q set value 2\n")
