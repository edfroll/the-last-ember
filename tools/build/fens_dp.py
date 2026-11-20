"""T-026: the datapack part of the Crooked Fens, written by tools/build/r1_fens.py: function/fens/gen/*, dialog/fens/*, the traders
of the witches (traders/fens.gen.txt, read by tools/gen_traders.py), the ambush trap line (traps/traps.txt), the quest items
(contracts/contracts.txt `item` lines). Generated, do not edit. The hand-written logic is function/fens/*.mcfunction.

Scores (objective le.fn): #choice 0 none / 1 Mother / 2 Maiden / 3 Crone (storage last_ember:choices fens, one per game);
the vial #vs 0 to be put in the chest / 1 in the chest / 2 carried / 3 given, #vg its generation; the sedge #sg 0 not given / 1 given;
pools #p<k> 0 under / 1 rising / 2 up / 4 sinking / 5 closing / 3 closed for good, #p<k>n not-watched ticks, #p<k>w watched ticks,
#p<k>t ticks up, #p<k>c gametime of the end of its cooldown, #closed; the Master #ms 0 in the gap / 1 risen / 2 killed (skull) /
3 away (back at #mt), the skull #sk 0 none / 1 carried / 2 given, #kg its generation. Storage last_ember:fens mirrors them.
Players: tags le.fh1..3 (heard the witch's intro), trigger le.fgive (the give button), le.fcl (gametime the Clairvoyance ends)."""
import json, math, os

NAMES = {1: "Мать Ряска", 2: "Дева Осока", 3: "Старуха Кость"}
KEYS = {1: "mother", 2: "maiden", 3: "crone"}
CROWN = "Венец у нас один на троих. Отдаст та, кому поможете."
TEXT = {
    1: dict(intro="А, гости. Котлы не трогайте, они помнят руки. Мне нужна моя склянка: чёрное стекло, пробка из кости. Она утонула вместе с деревней на сваях, в доме, где до сих пор кто-то сидит.",
            healer="Знахарь? Брось в свой котёл кувшинку, паучий глаз и комок слизи. Выпьешь — увидишь, кто на вас смотрит.",
            wait="Склянка сама не всплывёт.",
            thanks="Моя склянка… Держи Венец. Сёстры теперь на вас обижены. Это ненадолго, лет на сто.",
            offended="К ней пошли, к ней и ходите. Торговать — торгую. Дороже."),
    2: dict(intro="Тише. Слышишь? Они опять смотрят из воды. Пять голов, пять заводей. Возьми осоку и брось каждой в воду, когда она поднимется. Только не смотри ей в глаза дольше вдоха.",
            wait="Они ещё смотрят. Я чувствую.",
            thanks="Тихо стало. Впервые за… неважно. Возьми Венец. Сёстры обидятся, а я нет.",
            offended="Ты выбрал другую. Зеркало помнит, и цены тоже."),
    3: dict(intro="Кости, кости… Под гатью живёт Хозяин. Он сожрал моего ворона и троих до вас. Принеси мне его череп. Целым.",
            wait="Черепа не вижу. Иди.",
            thanks="Целый. Хорош. Вот тебе Венец. Сёстрам не говори, сами узнают.",
            offended="Подачек твоих не надо. А продать — продам. За двойную кость."),
}
# the quest items (T-020 `item` lines: custom_data le_citem + le_keep; the generation `gen` makes old copies invalid)
ITEMS = {   # key -> the item stack in the give syntax ($(gen): the generation from the macro)
    "fens_vial": 'minecraft:potion[minecraft:potion_contents={custom_color:1315860},minecraft:custom_data={le_citem:"fens_vial",le_keep:1b,le_boost:1b,gen:$(gen)},!minecraft:consumable,'
                 'minecraft:item_name={"text":"Склянка Матери","color":"gold","italic":false},minecraft:lore=[{"text":"Чёрное стекло, пробка из кости.","color":"gray","italic":false}],minecraft:max_stack_size=1]',
    "fens_sedge": 'minecraft:stick[minecraft:item_model="minecraft:short_grass",minecraft:custom_data={le_citem:"fens_sedge",le_keep:1b},'
                  'minecraft:item_name={"text":"Пучок осоки","color":"gold","italic":false},minecraft:lore=[{"text":"Бросить в заводь, когда голова поднимется.","color":"gray","italic":false}],minecraft:max_stack_size=16]',
    "fens_skull": 'minecraft:stick[minecraft:item_model="minecraft:skeleton_skull",minecraft:custom_data={le_citem:"fens_skull",le_keep:1b,gen:$(gen)},'
                  'minecraft:item_name={"text":"Череп Хозяина Гати","color":"gold","italic":false},minecraft:lore=[{"text":"Целый.","color":"gray","italic":false}],minecraft:max_stack_size=1]',
}
# the deals (HQ T-026, 3): (price 1, price 2 or None, the goods, uses); prices x1.5 rounded up for the offended
DEALS = {
    1: [(("trophy:r1", 1), ("minecraft:spider_eye", 4), ("@potion_healing2", 1), 4),
        (("trophy:r1", 2), ("minecraft:spider_eye", 6), ("@potion_strength", 1), 2),
        (("trophy:r1", 1), ("minecraft:spider_eye", 2), ("@antidote", 1), 4)],
    2: [(("trophy:r1", 1), ("minecraft:feather", 4), ("minecraft:lapis_lazuli", 4), 3),
        (("trophy:r1", 1), ("minecraft:feather", 4), ("@stew_night_vision", 1), 4),
        (("trophy:r1", 3), ("minecraft:feather", 8), ("@book_protection1", 1), 1),
        (("trophy:r1", 4), ("minecraft:feather", 8), ("@book_sharpness2", 1), 1)],
    3: [(("trophy:r1", 1), ("minecraft:bone", 16), ("@arrows_poison", 8), 3),
        (("trophy:r1", 2), ("minecraft:bone", 24), ("@book_bane2", 1), 1),
        (("trophy:r1", 3), None, ("@book_unbreaking1", 1), 1)],
}
PRESETS = [
    'potion_healing2 minecraft:potion {"minecraft:potion_contents":{potion:"minecraft:strong_healing"}}',
    'potion_strength minecraft:potion {"minecraft:potion_contents":{potion:"minecraft:strength"}}',
    'antidote minecraft:potion {"minecraft:custom_data":{le_antidote:1b},"minecraft:custom_name":{text:"Противоядие",italic:false,color:"green"},"minecraft:potion_contents":{custom_color:11141120},"minecraft:lore":[{text:"Снимает отравление и иссушение.",color:"gray",italic:false},{text:"60 секунд невосприимчивости к ним.",color:"gray",italic:false}]}',
    'stew_night_vision minecraft:suspicious_stew {"minecraft:suspicious_stew_effects":[{id:"minecraft:night_vision",duration:100}]}',
    'book_protection1 minecraft:enchanted_book {"minecraft:stored_enchantments":{"minecraft:protection":1}}',
    'book_sharpness2 minecraft:enchanted_book {"minecraft:stored_enchantments":{"minecraft:sharpness":2}}',
    'arrows_poison minecraft:tipped_arrow {"minecraft:potion_contents":{potion:"minecraft:poison"}}',
    'book_bane2 minecraft:enchanted_book {"minecraft:stored_enchantments":{"minecraft:bane_of_arthropods":2}}',
    'book_unbreaking1 minecraft:enchanted_book {"minecraft:stored_enchantments":{"minecraft:unbreaking":1}}',
]
GROVE = (-420, 60)          # the Mushroom grove: the trails of the Clairvoyance point there

def tx(t, color="white", italic=False): return {"text": t, "color": color, "italic": italic}
def J(o): return json.dumps(o, ensure_ascii=False)

def run(R, meta):
    ROOT, DP = R.ROOT, R.DP
    GEN = os.path.join(DP, "function/fens/gen"); os.makedirs(GEN, exist_ok=True)
    for f in os.listdir(GEN):
        if f.endswith(".mcfunction"): os.remove(os.path.join(GEN, f))
    hdr = "# generated by tools/build/r1_fens.py (fens_dp.py): "
    def w(name, lines): open(os.path.join(GEN, name + ".mcfunction"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    W = meta["W"]; hut = meta["hut"]; FL = meta["floor"]
    HX, HZ = meta["hut_centre"]
    x1, z1, x2, z2 = R.PLACE
    AREA = "x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d" % (x1 - 32, W - 40, z1 - 32, x2 - x1 + 64, 120, z2 - z1 + 64)
    # ------------------------------------------------------------------ the witches (NPC), their talk interactions
    witch = {1: hut["mother"], 2: hut["maiden"], 3: hut["crone"]}
    item = {1: hut["mother_item"], 2: hut["maiden_item"], 3: hut["crone_item"]}
    talk_box = {1: (item[1][0] + 0.5, item[1][1], item[1][2] + 0.5, 1.05, 1.05),        # the Mother's cauldron
                2: (item[2][0] + 0.5, item[2][1], item[2][2] - 0.5, 1.1, 2.1),           # the Maiden's mirror (in the wall north of the point)
                3: (item[3][0] + 0.5, item[3][1], item[3][2] + 0.5, 1.1, 2.1)}           # the Crone's cage
    L = [hdr + "every second: the witches and the talk boxes stand (built when their chunk is loaded, rebuilt when missing)"]
    for k in (1, 2, 3):
        x, y, z, yaw = witch[k]
        nbt = ('{NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,CustomNameVisible:1b,CustomName:{"text":"%s","color":"dark_green"},'
               'Rotation:[%.1ff,0f],Tags:["le.npc","le.keep","le.noelite","le.fw","le.fw%d"],CanPickUpLoot:0b,'
               'active_effects:[{id:"minecraft:water_breathing",amplifier:0b,duration:-1,show_particles:0b,show_icon:0b},{id:"minecraft:fire_resistance",amplifier:0b,duration:-1,show_particles:0b,show_icon:0b}]}') % (NAMES[k], yaw, k)
        w("witch_%d" % k, [hdr + "the witch %d (%s)" % (k, NAMES[k]), "kill @e[type=minecraft:witch,tag=le.fw%d]" % k,
                           "summon minecraft:witch %.1f %d %.1f %s" % (x + 0.5, y, z + 0.5, nbt)])
        L.append("execute if loaded %d %d %d unless entity @e[type=minecraft:witch,tag=le.fw%d,x=%.1f,y=%d,z=%.1f,distance=..3] run function last_ember:fens/gen/witch_%d" % (x, y, z, k, x + 0.5, y, z + 0.5, k))
        L.append("execute as @e[type=minecraft:witch,tag=le.fw%d] unless entity @s[x=%.1f,y=%d,z=%.1f,distance=..0.3] run tp @s %.1f %d %.1f %.1f 0" % (k, x + 0.5, y, z + 0.5, x + 0.5, y, z + 0.5, yaw))
        bx, by, bz, bw_, bh = talk_box[k]
        w("talkbox_%d" % k, [hdr + "the talk box of the witch %d" % k, "kill @e[type=minecraft:interaction,tag=le.ft%d]" % k,
                             'summon minecraft:interaction %.2f %d %.2f {Tags:["le.ftalk","le.ft%d"],width:%.2ff,height:%.2ff,response:1b}' % (bx, by, bz, k, bw_, bh)])
        L.append("execute if loaded %d %d %d unless entity @e[type=minecraft:interaction,tag=le.ft%d] run function last_ember:fens/gen/talkbox_%d" % (item[k][0], item[k][1], item[k][2], k, k))
    # the entities of a chunk load a little after its blocks: a witch / talk box summoned before the old one came in is one too many
    for k in (1, 2, 3):
        for typ, tag in (("witch", "le.fw%d" % k), ("interaction", "le.ft%d" % k)):
            L.append("execute store result score #c le.fn if entity @e[type=minecraft:%s,tag=%s]" % (typ, tag))
            L.append("execute if score #c le.fn matches 2.. as @e[type=minecraft:%s,tag=%s,limit=1] run tag @s add le.fone" % (typ, tag))
            L.append("execute if score #c le.fn matches 2.. run kill @e[type=minecraft:%s,tag=%s,tag=!le.fone]" % (typ, tag))
            L.append("tag @e[type=minecraft:%s,tag=le.fone] remove le.fone" % typ)
    # NoAI does not stop a witch from drinking (vanilla Witch.aiStep): she drinks healing when her health is below the maximum, fire
    # resistance when burning, water breathing under water. Invulnerable + the two endless effects keep her from all three; on top of
    # that a potion she took into her hand is taken away (her drink ends with nothing in it) and her health is kept full
    L.append("execute as @e[type=minecraft:witch,tag=le.fw] if items entity @s weapon.mainhand * run item replace entity @s weapon.mainhand with minecraft:air")
    L.append("execute as @e[type=minecraft:witch,tag=le.fw] run data modify entity @s Health set value 26.0f")
    w("npcs", L)
    # which talk box was clicked: as the player, the nearest box within 6
    w("talk_which", [hdr + "as the player who clicked a talk box: #k = its witch (0 none)", "scoreboard players set #k le.fn 0"] +
      ["execute if entity @e[type=minecraft:interaction,tag=le.ft%d,distance=..6] run scoreboard players set #k le.fn %d" % (k, k) for k in (1, 2, 3)])
    w("near_witch", [hdr + "as the player who pressed a give button (#k): 1 when he stands within 8 of that witch's talk box"] +
      ["execute if score #k le.fn matches %d if entity @e[type=minecraft:interaction,tag=le.ft%d,distance=..8] run return 1" % (k, k) for k in (1, 2, 3)] + ["return 0"])
    # ------------------------------------------------------------------ dialogs
    DLG = os.path.join(DP, "dialog/fens"); os.makedirs(DLG, exist_ok=True)
    for f in os.listdir(DLG): os.remove(os.path.join(DLG, f))
    def dump(name, o): json.dump(o, open(os.path.join(DLG, name + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    def msg(t, c="white", it=False): return {"type": "minecraft:plain_message", "contents": tx(t, c, it), "width": 300}
    def notice(name, k, lines):
        dump(name, {"type": "minecraft:notice", "title": tx(NAMES[k], "dark_green"), "body": lines, "can_close_with_escape": True, "pause": False,
                    "action": {"label": tx("Уйти", "gray"), "width": 150}})
    for k in (1, 2, 3):
        t = TEXT[k]
        notice("intro_%d" % k, k, [msg(t["intro"]), msg(CROWN, "gold")])
        if k == 1: notice("intro_1h", 1, [msg(t["intro"]), msg(t["healer"], "green"), msg(CROWN, "gold")])
        notice("wait_%d" % k, k, [msg(t["wait"])])
        dump("give_%d" % k, {"type": "minecraft:multi_action", "title": tx(NAMES[k], "dark_green"), "body": [msg(t["wait"] if k != 2 else "Тихо стало? Я слушаю."), msg(CROWN, "gold")],
                             "can_close_with_escape": True, "pause": False, "after_action": "close", "columns": 1,
                             "actions": [{"label": tx("Отдать", "green"), "width": 150, "action": {"type": "minecraft:run_command", "command": "trigger le.fgive set %d" % k}}],
                             "exit_action": {"label": tx("Уйти", "gray"), "width": 150}})
        notice("thanks_%d" % k, k, [msg(t["thanks"])])
        notice("offended_%d" % k, k, [msg(t["offended"])])
    # ------------------------------------------------------------------ the quest items: give with the current generation (macro gen)
    for key, stack in ITEMS.items():
        w("give_" + key, [hdr + "give the quest item %s to @s (macro: gen%s)" % (key, ", n" if key == "fens_sedge" else ""),
                          "$give @s %s %s" % (stack, "$(n)" if key == "fens_sedge" else "1")])
    w("chest_fens_vial", [hdr + "the vial into the ambush chest (slot 13; the chest's loot is made first by vanilla), macro: gen",
                          "$item replace block %d %d %d container.13 with %s 1" % (tuple(meta["chest"]) + (ITEMS["fens_vial"],))])
    # ------------------------------------------------------------------ the vial: the chest of the ambush
    cx, cy, cz = meta["chest"]
    w("vial", [hdr + "every second: the vial of the Mother (0 put it into the chest / 1 in it / 2 carried / 3 given)",
               "execute if score #vs le.fn matches 0 if loaded %d %d %d run function last_ember:fens/vial_fill" % (cx, cy, cz),
               "execute if score #vs le.fn matches 1 if loaded %d %d %d unless items block %d %d %d container.* *[minecraft:custom_data~{le_citem:\"fens_vial\"}] run scoreboard players set #vs le.fn 2" % (cx, cy, cz, cx, cy, cz),
               "execute if score #vs le.fn matches 2 run function last_ember:fens/vial_lost"])
    w("vial_chest", [hdr + "the chest of the ambush stands (it is not protected: a broken one comes back empty of loot, the vial goes in)",
                     "execute unless block %d %d %d minecraft:chest run setblock %d %d %d minecraft:chest[facing=%s,type=single,waterlogged=false]" % (cx, cy, cz, cx, cy, cz, meta["chest_facing"]),
                     "function last_ember:fens/gen/chest_fens_vial with storage last_ember:fens vial"])
    w("vial_unchest", [hdr + "the vial out of the ambush chest (any slot), when its chunk is loaded", "execute unless loaded %d %d %d run return 0" % (cx, cy, cz)] +
      ["execute if items block %d %d %d container.%d *[minecraft:custom_data~{le_citem:\"fens_vial\"}] run item replace block %d %d %d container.%d with minecraft:air" % (cx, cy, cz, n, cx, cy, cz, n) for n in range(27)])
    w("vial_in_chest", [hdr + "#c = 1 when the vial lies in the ambush chest", "scoreboard players set #c le.fn 0",
                        "execute if loaded %d %d %d if items block %d %d %d container.* *[minecraft:custom_data~{le_citem:\"fens_vial\"}] run scoreboard players set #c le.fn 1" % (cx, cy, cz, cx, cy, cz)])
    # ------------------------------------------------------------------ the pools and the heads
    pools = meta["pools"]
    L = [hdr + "every 5 ticks: the heads of the 5 pools (only a pool with a player within 32)"]
    for p in pools:
        k = p["id"]; x, z, r = p["x"], p["z"], p["r"]
        L.append("execute positioned %.1f %d %.1f if entity @a[distance=..32,gamemode=!spectator] run function last_ember:fens/gen/pool_%d" % (x + 0.5, W, z + 0.5, k))
        c3 = "%.1f %.1f %.1f" % (x + 0.5, W + 1.0, z + 0.5)
        box = "x=%d,y=%d,z=%d,dx=%d,dy=4,dz=%d" % (x - r - 1, W - 3, z - r - 1, 2 * r + 2, 2 * r + 2)
        P = "#p%d" % k
        w("pool_%d" % k, [hdr + "pool %d at %d %d (r %d): 0 under, 1 rising, 2 up, 4 sinking, 5 closing, 3 closed for good" % (k, x, z, r),
                          "execute if score %s le.fn matches 3 run return 0" % P,
                          "execute if score %s le.fn matches 1 run return run function last_ember:fens/gen/up_%d" % (P, k),
                          "execute if score %s le.fn matches 4 run return run function last_ember:fens/gen/gone_%d" % (P, k),
                          "execute if score %s le.fn matches 5 run return run function last_ember:fens/gen/shut_%d" % (P, k),
                          "execute if score %s le.fn matches 2 run return run function last_ember:fens/gen/head_%d" % (P, k),
                          "# under: rises when somebody is within 20 and nobody within 24 looks at the pool (60 degrees) for 2 s; the cooldown 20 s",
                          "execute if score #gt le.fn < %sc le.fn run return 0" % P,
                          "execute positioned %s unless entity @a[distance=..20,gamemode=!spectator] run return run scoreboard players set %sn le.fn 0" % (c3, P),
                          "execute positioned %s as @a[distance=..24,gamemode=!spectator] at @s anchored eyes facing %s anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..1.0] run return run scoreboard players set %sn le.fn 0" % (c3, c3, P),
                          "scoreboard players add %sn le.fn 5" % P,
                          "execute if score %sn le.fn matches 40.. run function last_ember:fens/gen/rise_%d" % (P, k)])
        w("rise_%d" % k, [hdr + "the head of pool %d rises (it comes up from under the water in 0.5 s, facing the nearest player)" % k,
                          "kill @e[type=minecraft:item_display,tag=le.fh%d]" % k,
                          'summon minecraft:item_display %.1f %.2f %.1f {Tags:["le.fhead","le.fh%d"],teleport_duration:10,item_display:"head",brightness:{sky:6,block:15},item:{id:"minecraft:stick",count:1,components:{"minecraft:item_model":"last_ember:fens/head_open"}},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[1.2f,1.2f,1.2f]}}' % (x + 0.5, W - 0.6, z + 0.5, k),
                          "execute as @e[type=minecraft:item_display,tag=le.fh%d] at @s facing entity @p[gamemode=!spectator] eyes run tp @s ~ ~ ~ ~ 0" % k,
                          "scoreboard players set %s le.fn 1" % P, "scoreboard players set %st le.fn 0" % P, "scoreboard players set %sw le.fn 0" % P,
                          "particle minecraft:bubble_column_up %s %.1f 0.2 %.1f 0.05 30 force" % (c3, r * 0.6, r * 0.6),
                          "particle minecraft:splash %s %.1f 0.1 %.1f 0.1 25 force" % (c3, r * 0.5, r * 0.5),
                          "playsound minecraft:entity.player.splash ambient @a[distance=..24] %s 0.25 0.6" % c3,
                          "playsound minecraft:block.bubble_column.upwards_ambient ambient @a[distance=..24] %s 0.6 0.7" % c3])
        w("up_%d" % k, [hdr + "the head of pool %d comes up (0.5 s after the rise)" % k,
                        "execute as @e[type=minecraft:item_display,tag=le.fh%d] at @s run tp @s ~ %.2f ~" % (k, W + 1.0),     # on the surface: seen over the banks
                        "scoreboard players set %s le.fn 2" % P])
        w("head_%d" % k, [hdr + "the head of pool %d is up: a sedge bundle thrown into the pool closes it; looked at (30 degrees, seen) for 1.5 s after the first 3 s -> sinks; 8 s at most" % k,
                          "scoreboard players add %st le.fn 5" % P,
                          "execute as @e[type=minecraft:item,%s] if items entity @s contents *[minecraft:custom_data~{le_citem:\"fens_sedge\"}] run return run function last_ember:fens/gen/close_%d" % (box, k),
                          "scoreboard players set #seen le.fn 0",
                          "tag @e[type=minecraft:item_display,tag=le.fh%d] add le.fhtg" % k,
                          "execute positioned %s as @a[distance=..24,gamemode=!spectator] at @s anchored eyes facing %s anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.5176] at @s anchored eyes facing entity @e[type=minecraft:item_display,tag=le.fhtg,limit=1] feet positioned ^ ^ ^ anchored feet run function last_ember:fens/look" % (c3, c3),
                          "tag @e[type=minecraft:item_display,tag=le.fh%d] remove le.fhtg" % k,
                          "execute if score #seen le.fn matches 1 run scoreboard players add %sw le.fn 5" % P,
                          "execute if score #seen le.fn matches 0 run scoreboard players set %sw le.fn 0" % P,
                          "execute if score %st le.fn matches 60.. if score %sw le.fn matches 30.. run return run function last_ember:fens/gen/sink_%d" % (P, P, k),
                          "execute if score %st le.fn matches 160.. run function last_ember:fens/gen/sink_%d" % (P, k)])
        w("sink_%d" % k, [hdr + "the head of pool %d sinks; the pool rests 20 s" % k,
                          "execute as @e[type=minecraft:item_display,tag=le.fh%d] at @s run tp @s ~ %.2f ~" % (k, W - 0.7),
                          "scoreboard players set %s le.fn 4" % P, "scoreboard players set %sn le.fn 0" % P,
                          "scoreboard players operation %sc le.fn = #gt le.fn" % P, "scoreboard players add %sc le.fn 400" % P,
                          "particle minecraft:bubble %s %.1f 0.1 %.1f 0.02 12 force" % (c3, r * 0.5, r * 0.5),
                          "playsound minecraft:entity.generic.swim ambient @a[distance=..20] %s 0.3 0.5" % c3])
        w("gone_%d" % k, [hdr + "the head of pool %d is under again" % k, "kill @e[type=minecraft:item_display,tag=le.fh%d]" % k,
                          "scoreboard players set %s le.fn 0" % P, "function last_ember:fens/save"])
        lily = [(x + a, z + b_) for a in range(-r, r + 1) for b_ in range(-r, r + 1) if (a * 7 + b_ * 3 + k) % 3 != 0]
        w("close_%d" % k, [hdr + "a sedge bundle in pool %d while its head is up: the bundle goes, the head closes its eyes" % k,
                           "kill @s", "scoreboard players set %s le.fn 5" % P, "scoreboard players set %st le.fn 0" % P,
                           "execute as @e[type=minecraft:item_display,tag=le.fh%d] run data modify entity @s item.components.\"minecraft:item_model\" set value \"last_ember:fens/head_closed\"" % k,
                           "particle minecraft:bubble_pop %s %.1f 0.2 %.1f 0.02 20 force" % (c3, r * 0.5, r * 0.5),
                           "playsound minecraft:entity.drowned.ambient_water ambient @a[distance=..24] %s 0.6 0.5" % c3])
        w("shut_%d" % k, [hdr + "the closed head of pool %d sinks for good after 2 s; the pool clears: lily pads" % k,
                          "scoreboard players add %st le.fn 5" % P,
                          "execute if score %st le.fn matches 40 as @e[type=minecraft:item_display,tag=le.fh%d] at @s run tp @s ~ %.2f ~" % (P, k, W - 0.8),
                          "execute if score %st le.fn matches ..49 run return 0" % P,
                          "kill @e[type=minecraft:item_display,tag=le.fh%d]" % k, "scoreboard players set %s le.fn 3" % P,
                          "function last_ember:fens/gen/lily_%d" % k, "function last_ember:fens/gen/count", "function last_ember:fens/save",
                          "playsound minecraft:block.amethyst_block.chime ambient @a[distance=..24] %s 0.6 0.6" % c3])
        w("lily_%d" % k, [hdr + "pool %d cleared: lily pads on it" % k] + ["execute if block %d %d %d minecraft:water if block %d %d %d minecraft:air run setblock %d %d %d minecraft:lily_pad" % (a, W, b_, a, W + 1, b_, a, W + 1, b_) for (a, b_) in lily])
        w("unlily_%d" % k, [hdr + "TEST/ADMIN: pool %d dark again" % k] + ["execute if block %d %d %d minecraft:lily_pad run setblock %d %d %d minecraft:air" % (a, W + 1, b_, a, W + 1, b_) for (a, b_) in lily])
    w("pools", L)
    w("count", [hdr + "#closed = closed pools", "scoreboard players set #closed le.fn 0"] + ["execute if score #p%d le.fn matches 3 run scoreboard players add #closed le.fn 1" % p["id"] for p in pools])
    w("open_pools", [hdr + "#c = pools not closed for good", "function last_ember:fens/gen/count", "scoreboard players set #c le.fn %d" % len(pools), "scoreboard players operation #c le.fn -= #closed le.fn"])
    w("heads_kill", [hdr + "TEST/ADMIN: every head under, every pool open again"] + ["kill @e[type=minecraft:item_display,tag=le.fhead]"] +
      ["scoreboard players set #p%d%s le.fn 0" % (p["id"], s) for p in pools for s in ("", "n", "w", "t", "c")] + ["function last_ember:fens/gen/unlily_%d" % p["id"] for p in pools])
    w("pools_save", [hdr + "the states of the pools -> storage"] + ["execute store result storage last_ember:fens pools.p%d int 1 run scoreboard players get #p%d le.fn" % (p["id"], p["id"]) for p in pools])
    w("pools_load", [hdr + "the states of the pools <- storage (a closed pool stays closed; any other starts under)"] +
      ["execute store result score #p%d le.fn run data get storage last_ember:fens pools.p%d" % (p["id"], p["id"]) for p in pools] +
      ["execute unless score #p%d le.fn matches 3 run scoreboard players set #p%d le.fn 0" % (p["id"], p["id"]) for p in pools] +
      ["scoreboard players set #p%d%s le.fn 0" % (p["id"], s) for p in pools for s in ("n", "w", "t", "c")] + ["kill @e[type=minecraft:item_display,tag=le.fhead]"])
    # the Clairvoyance: the trail of every pool not closed (8 blocks towards the Mushroom grove), only for the drinker
    L = [hdr + "as a player who drank the Clairvoyance: a thin trail from every pool still open, 8 blocks towards the Mushroom grove (only he sees it)"]
    for p in pools:
        k = p["id"]; dx, dz = GROVE[0] - p["x"], GROVE[1] - p["z"]; d = math.hypot(dx, dz); ux, uz = dx / d, dz / d
        pts = ["%.2f %.2f %.2f" % (p["x"] + 0.5 + ux * s, W + 0.7 + s * 0.08, p["z"] + 0.5 + uz * s) for s in [i * 0.5 for i in range(1, 17)]]
        L.append("execute unless score #p%d le.fn matches 3 if entity @s[x=%d,y=%d,z=%d,distance=..64] run function last_ember:fens/gen/trail_%d" % (k, p["x"], W, p["z"], k))
        w("trail_%d" % k, [hdr + "the trail of pool %d" % k] + ["particle minecraft:dust{color:[0.6,1.0,0.45],scale:0.9} %s 0.03 0.03 0.03 0 1 force @s" % q for q in pts])
    w("trails", L)
    # ------------------------------------------------------------------ the Master of the Causeway: the dark gap
    dk = meta["dark"]; mx, mz = dk["x"], dk["z"]
    MC = "%.1f %d %.1f" % (mx + 0.5, W - 4, mz + 0.5)
    w("master_check", [hdr + "every 5 ticks: the Master of the Causeway (0 in the dark gap / 1 risen / 2 killed (skull) / 3 away until #mt)",
                       "execute if score #ms le.fn matches 3 if score #gt le.fn >= #mt le.fn run scoreboard players set #ms le.fn 0",
                       "execute if score #ms le.fn matches 0 positioned %.1f %d %.1f if entity @a[distance=..6,gamemode=!spectator,gamemode=!creative] run return run function last_ember:fens/master_rise" % (mx + 0.5, W + 1, mz + 0.5),
                       "execute if score #ms le.fn matches 0 positioned %.1f %d %.1f as @a[distance=..10,gamemode=!spectator,gamemode=!creative] at @s if block ~ ~ ~ minecraft:water run return run function last_ember:fens/master_rise" % (mx + 0.5, W, mz + 0.5),
                       "execute if score #ms le.fn matches 1 run function last_ember:fens/master_tick"])
    w("master_spawn", [hdr + "the Master rises from the bottom of the dark gap",
                       'summon minecraft:drowned %s {Tags:["le.fmaster","le.fmnew","le.noelite"],PersistenceRequired:1b,CanPickUpLoot:0b,equipment:{mainhand:{id:"minecraft:air"}}}' % MC,
                       "execute as @e[type=minecraft:drowned,tag=le.fmnew,limit=1] run function last_ember:elite/make",
                       'execute as @e[type=minecraft:drowned,tag=le.fmnew,limit=1] run data merge entity @s {CustomName:{"text":"Хозяин Гати","color":"dark_red"},CustomNameVisible:1b}',
                       "tag @e[type=minecraft:drowned,tag=le.fmnew] remove le.fmnew",
                       "particle minecraft:bubble_column_up %.1f %d %.1f 0.6 0.5 0.6 0.1 60 force" % (mx + 0.5, W, mz + 0.5),
                       "particle minecraft:splash %.1f %d %.1f 0.8 0.2 0.8 0.2 40 force" % (mx + 0.5, W + 1, mz + 0.5),
                       "playsound minecraft:entity.drowned.ambient_water hostile @a[distance=..32] %.1f %d %.1f 1.6 0.5" % (mx + 0.5, W, mz + 0.5),
                       "playsound minecraft:entity.player.splash.high_speed hostile @a[distance=..32] %.1f %d %.1f 1 0.6" % (mx + 0.5, W, mz + 0.5)])
    w("master_leash", [hdr + "as the Master: further than 12 from the gap -> back into it",
                       "execute unless entity @s[x=%.1f,y=%d,z=%.1f,distance=..12] run tp @s %s" % (mx + 0.5, W, mz + 0.5, MC)])
    w("master_far", [hdr + "1 when no player is within 48 of the gap", "execute positioned %.1f %d %.1f if entity @a[distance=..48,gamemode=!spectator] run return 0" % (mx + 0.5, W, mz + 0.5), "return 1"])
    w("master_loaded", [hdr + "1 when the gap's chunk is loaded", "execute if loaded %d %d %d run return 1" % (mx, W, mz), "return 0"])
    w("markers", [hdr + "mechanic points of the fens (storage only; tests and other systems read them)",
                  "data modify storage last_ember:r1 m.fens_master set value [%d,%d,%d]" % (mx, W, mz),
                  "data modify storage last_ember:r1 m.fens_table set value %s" % json.dumps(hut["table"]),
                  "data modify storage last_ember:r1 m.fens_chest set value %s" % json.dumps(meta["chest"]),
                  "data modify storage last_ember:r1 m.fens_enchant set value %s" % json.dumps(hut["enchant"])])
    # ------------------------------------------------------------------ boats: 4 places (2 at the outer pier, 2 at the hut's)
    L = [hdr + "every second: a boat that is not at its place while nobody is within 32 of the place comes back (the old one goes when nobody rides it); 4 at most",
         "# (a boat left in a chunk that was not loaded comes in later: then the one nearest its place stays, an unridden other goes)"]
    for k, (bx, by, bz) in enumerate(meta["boats"], 1):
        L.append("execute if loaded %d %d %d positioned %.1f %d %.1f unless entity @e[type=minecraft:mangrove_boat,tag=le.fb%d,distance=..4] unless entity @a[distance=..32,gamemode=!spectator] run function last_ember:fens/gen/boat_%d" % (bx, by, bz, bx + 0.5, by, bz + 0.5, k, k))
        L.append("execute store result score #c le.fn if entity @e[type=minecraft:mangrove_boat,tag=le.fb%d]" % k)
        L.append("execute if score #c le.fn matches 2.. positioned %.1f %d %.1f as @e[type=minecraft:mangrove_boat,tag=le.fb%d,sort=nearest,limit=1] run tag @s add le.fone" % (bx + 0.5, by, bz + 0.5, k))
        L.append("execute if score #c le.fn matches 2.. as @e[type=minecraft:mangrove_boat,tag=le.fb%d,tag=!le.fone] at @s unless entity @a[distance=..3] run kill @s" % k)
        L.append("tag @e[type=minecraft:mangrove_boat,tag=le.fone] remove le.fone")
        w("boat_%d" % k, [hdr + "the boat %d back at its place" % k,
                          "execute as @e[type=minecraft:mangrove_boat,tag=le.fb%d] at @s unless entity @a[distance=..3] run kill @s" % k,
                          "execute if entity @e[type=minecraft:mangrove_boat,tag=le.fb%d] run return 0" % k,
                          'summon minecraft:mangrove_boat %.1f %.1f %.1f {Tags:["le.fboat","le.fb%d"],Rotation:[%df,0f]}' % (bx + 0.5, by + 0.6, bz + 0.5, k, 90 if k > 2 else -90)])
    w("boats", L)
    # ------------------------------------------------------------------ the traders of the witches (tools/gen_traders.py reads traders/fens.gen.txt)
    tl = ["# generated by tools/build/r1_fens.py (fens_dp.py): the trade windows of the three witches (invisible villagers in the witches,",
          "# a bit bigger, so that a click on the witch opens the trade). Prices x1.5 for the offended witches: function last_ember:fens/gen/prices_<k>."]
    for k in (1, 2, 3):
        x, y, z, yaw = witch[k]
        tl.append('trader witch_%s overworld %d %d %d %d type=villager prof=cleric vtype=swamp name="%s" hello="" invisible=1 scale=1.15' % (KEYS[k], x, y, z, int(yaw), NAMES[k]))
        for (p1, p2, sell, uses) in DEALS[k]:
            tl.append("  buy %s %d%s -> %s %d uses=%d" % (p1[0], p1[1], (" + %s %d" % p2) if p2 else "", sell[0], sell[1], uses))
    open(os.path.join(ROOT, "traders/fens.gen.txt"), "w", encoding="utf-8").write("\n".join(tl) + "\n")
    import re
    ip = os.path.join(ROOT, "traders/items.txt"); itxt = open(ip, encoding="utf-8").read().split("\n")
    itxt = [l for l in itxt if not any(l.startswith(p.split(" ")[0] + " ") for p in PRESETS)]
    while itxt and itxt[-1] == "": itxt.pop()
    open(ip, "w", encoding="utf-8").write("\n".join(itxt + PRESETS) + "\n")
    for k in (1, 2, 3):
        L = [hdr + "the prices of %s x1.5 rounded up (she is offended); the uses stay" % NAMES[k]]
        for i, (p1, p2, sell, uses) in enumerate(DEALS[k]):
            L.append("execute as @e[type=minecraft:villager,tag=le.tr_witch_%s] run data modify entity @s Offers.Recipes[%d].buy.count set value %d" % (KEYS[k], i, -(-p1[1] * 3 // 2)))
            if p2: L.append("execute as @e[type=minecraft:villager,tag=le.tr_witch_%s] run data modify entity @s Offers.Recipes[%d].buyB.count set value %d" % (KEYS[k], i, -(-p2[1] * 3 // 2)))
        w("prices_%d" % k, L)
        L = [hdr + "TEST/ADMIN: the base prices of %s" % NAMES[k]]
        for i, (p1, p2, sell, uses) in enumerate(DEALS[k]):
            L.append("execute as @e[type=minecraft:villager,tag=le.tr_witch_%s] run data modify entity @s Offers.Recipes[%d].buy.count set value %d" % (KEYS[k], i, p1[1]))
            if p2: L.append("execute as @e[type=minecraft:villager,tag=le.tr_witch_%s] run data modify entity @s Offers.Recipes[%d].buyB.count set value %d" % (KEYS[k], i, p2[1]))
        w("prices_base_%d" % k, L)
    w("prices", [hdr + "every second (after the choice): the offended witches keep their higher prices (also for a trader rebuilt later)"] +
      ["execute unless score #choice le.fn matches %d run function last_ember:fens/gen/prices_%d" % (k, k) for k in (1, 2, 3)])
    # ------------------------------------------------------------------ the ambush trap and the quest items (lines of other generators)
    from r1 import replace_lines
    ax, ay, az = meta["chest"]
    replace_lines(os.path.join(ROOT, "traps/traps.txt"), ["fens_ambush "], ["fens_ambush cursed_chest overworld %d %d %d %d %d %d chest=%d,%d,%d mob=minecraft:drowned mob2=minecraft:bogged   # T-026: the house of the ambush in the ruins of the fens" %
                  (ax - 4, ay - 1, az - 4, ax + 4, ay + 3, az + 4, ax, ay, az)])
    replace_lines(os.path.join(ROOT, "contracts/contracts.txt"), ["item fens_vial ", "item fens_sedge ", "item fens_skull "],
                  ['item fens_vial minecraft:potion "Склянка Матери" "Чёрное стекло, пробка из кости."',
                   'item fens_sedge minecraft:stick "Пучок осоки" "Бросить в заводь, когда голова поднимется."',
                   'item fens_skull minecraft:stick "Череп Хозяина Гати" "Целый."'])
    # the area of the fens (the loop runs only while somebody is in it)
    w("near", [hdr + "#near = players (not spectators) in the fens or within 32 of the place", "execute store result score #near le.fn if entity @a[%s,gamemode=!spectator]" % AREA])
    w("in_area", [hdr + "as an entity: 1 in the fens area", "execute if entity @s[%s] run return 1" % AREA, "return 0"])
