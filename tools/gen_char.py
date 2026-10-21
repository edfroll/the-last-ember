#!/usr/bin/env python3
"""T-009: races, classes, kits, pads and altars of the Hall of Awakening -> datapack functions (generated, do not edit):
  datapack/data/last_ember/function/char/gen/*.mcfunction
Numbers: docs/tasks/T-009-awakening-races-classes.md (framework «Народы и классы»). Points: docs/reports/T-008-markers.txt.
Usage: python3 tools/gen_char.py"""
import os, re, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "datapack/data/last_ember/function/char/gen")
os.makedirs(OUT, exist_ok=True)
def w(name, lines):
    open(os.path.join(OUT, name + ".mcfunction"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
mk = {}
for line in open(os.path.join(ROOT, "docs/reports/T-008-markers.txt"), encoding="utf-8"):
    m = re.match(r"(\S+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)", line)
    if m and not line.startswith("#"): mk[m.group(1)] = tuple(int(m.group(i)) for i in (2, 3, 4))

# ---------------------------------------------------------------------------------------------- races
RACES = [  # slug, number, title, pad marker, statue angle, attributes [(attr, value, op)], description lines
 ("human", 1, "Люди Долин", "people_pad_humans", 45, [("scale", 0.0, "add_value"), ("luck", 1, "add_value")],
  ["Ростом обычные.", "Второе дыхание: на краю смерти — короткая регенерация и сила (откат 3 мин).", "Торговцы уступают в цене. Чуть больше удачи в сундуках.", "Без боевых бонусов."]),
 ("elf", 2, "Эльфы", "people_pad_elves", 90, [("scale", 0.1, "add_value"), ("max_health", -4, "add_value"), ("movement_speed", 0.10, "add_multiplied_base"),
   ("jump_strength", 0.15, "add_multiplied_base"), ("safe_fall_distance", 3, "add_value"), ("attack_damage", -1, "add_value")],
  ["Выше и быстрее, прыгают выше, дольше не разбиваются при падении.", "Стрелы бьют сильнее.", "Но 8 сердец и слабее в ближнем бою."]),
 ("dwarf", 3, "Гномы", "people_pad_dwarves", 270, [("scale", -0.2, "add_value"), ("max_health", 4, "add_value"), ("attack_damage", 1, "add_value"),
   ("block_break_speed", 0.3, "add_multiplied_base"), ("knockback_resistance", 0.5, "add_value"), ("movement_speed", -0.10, "add_multiplied_base"),
   ("jump_strength", -0.08, "add_multiplied_base"), ("block_interaction_range", -0.5, "add_value"), ("entity_interaction_range", -0.5, "add_value")],
  ["Ниже, 12 сердец, бьют сильнее, копают быстрее, их трудно сдвинуть.", "Но медленнее и тянутся не так далеко."]),
 ("halfling", 4, "Полурослики", "people_pad_halflings", 135, [("scale", -0.35, "add_value"), ("max_health", -6, "add_value"), ("sneaking_speed", 0.5, "add_multiplied_base"),
   ("fall_damage_multiplier", -0.5, "add_multiplied_base"), ("safe_fall_distance", 6, "add_value"), ("luck", 1, "add_value"), ("attack_damage", -1, "add_value"),
   ("block_interaction_range", -0.75, "add_value"), ("entity_interaction_range", -0.75, "add_value")],
  ["Самые маленькие. Быстро крадутся, падение почти не страшно,", "ловушки под ними часто не срабатывают, удача выше. Носят Кольцо.", "Но 7 сердец, короткие руки и слабый удар."]),
 ("ashborn", 5, "Пеплорождённые", "people_pad_ashborn", 315, [("scale", 0.0, "add_value"), ("max_health", 2, "add_value"), ("burning_time", -0.8, "add_multiplied_base")],
  ["11 сердец, огонь на них быстро гаснет, иссушение не берёт.", "Но вода — их враг: под водой задыхаются втрое быстрее."]),
]
NAME_STONE = {"human": "name_stone_humans", "elf": "name_stone_elves", "dwarf": "name_stone_dwarves", "halfling": "name_stone_halflings", "ashborn": "name_stone_ashborn"}
CLASSES = [  # slug, number, title, altar marker, symbol item, attributes, description
 ("knight", 1, "Рыцарь", "altar_shield", "minecraft:shield", [("attack_speed", 0.2, "add_multiplied_base"), ("entity_interaction_range", 0.5, "add_value")],
  ["Щит и меч. Получает меньше урона, бьёт чаще и чуть дальше.", "У костра может благословить отряд."]),
 ("ranger", 2, "Следопыт", "altar_horn", "minecraft:goat_horn", [],
  ["Лук и рог. Его стрелы летят вдвое дальше.", "Рог подсвечивает врагов всему отряду."]),
 ("seer", 3, "Ворожей", "altar_staff", "minecraft:stick", [],
  ["Посох с двумя заклинаниями, кинжал и книга.", "Читает гримуары, получает вдвое больше опыта."]),
 ("healer", 4, "Знахарь", "altar_phial", "minecraft:glass_bottle", [],
  ["Склянки, котёл и нож. Его зелья сильнее, варит в котле над костром,", "мажет клинки ядом и огнём, бережёт напарников."]),
]
def mod(prefix, attr, val, op): return f"attribute @s minecraft:{attr} modifier add last_ember:{prefix}_{attr} {val} {op}"
def rm(prefix, attr): return f"attribute @s minecraft:{attr} modifier remove last_ember:{prefix}_{attr}"
race_attrs = sorted({a for r in RACES for a, _, _ in r[5]}); class_attrs = sorted({a for c in CLASSES for a, _, _ in c[5]} | {"luck"})
w("race_strip", ["# as a player: removes every race modifier"] + [rm("race", a) for a in race_attrs])
w("class_strip", ["# as a player: removes every class modifier"] + [rm("class", a) for a in class_attrs])
for slug, n, title, pad, ang, attrs, desc in RACES:
    w(f"race_apply_{n}", [f"# as a player: {title} -- modifiers (idempotent)", "function last_ember:char/gen/race_strip"] + [mod("race", a, v, op) for a, v, op in attrs])
for slug, n, title, altar, sym, attrs, desc in CLASSES:
    w(f"class_apply_{n}", [f"# as a player: {title} -- modifiers (idempotent)", "function last_ember:char/gen/class_strip", "attribute @s minecraft:luck modifier add last_ember:class_mark 0 add_value"]
      + [mod("class", a, v, op) for a, v, op in attrs])
# dispatchers by tag (race_apply / class_apply for the current tag)
w("race_apply", ["# as a player: applies the modifiers of the race by tag"] + [f"execute if entity @s[tag=le.race.{r[0]}] run function last_ember:char/gen/race_apply_{r[1]}" for r in RACES])
w("class_apply", ["# as a player: applies the modifiers of the class by tag"] + [f"execute if entity @s[tag=le.class.{c[0]}] run function last_ember:char/gen/class_apply_{c[1]}" for c in CLASSES])
w("race_untag", ["# as a player: removes race tags"] + [f"tag @s remove le.race.{r[0]}" for r in RACES])
w("class_untag", ["# as a player: removes class tags"] + [f"tag @s remove le.class.{c[0]}" for c in CLASSES])
# descriptions and choices
def pos(m, d=0.5): x, y, z = mk[m]; return x + d, y, z + d
for slug, n, title, pad, ang, attrs, desc in RACES:
    t = [f'tellraw @s {{"text":"— {title} —","color":"gold","bold":true}}'] + [f'tellraw @s {{"text":"{l}","color":"gray"}}' for l in desc]
    w(f"race_desc_{n}", ["# as a player: description of the race"] + t + ['tellraw @s {"text":"ПКМ ещё раз в течение 10 секунд — выбрать.","color":"yellow"}'])
    x, y, z = pos(pad); a = math.radians(ang); sx, sz = 12.0 + 0, 0
    sx = x + math.sin(a) * 7; sz = z - math.cos(a) * 7
    w(f"race_choose_{n}", [f"# as a player: picks {title}", f"scoreboard players set @s le.race {n}", "function last_ember:char/gen/race_untag", f"tag @s add le.race.{slug}"]
      + (["tag @s add le.race.halfling"] if False else []) + [f"function last_ember:char/gen/race_apply_{n}", "effect give @s minecraft:instant_health 1 10 true",
      f"particle minecraft:totem_of_undying {sx:.1f} {y + 4} {sz:.1f} 0.6 2 0.6 0.1 40", f"playsound minecraft:block.beacon.activate player @s {x} {y} {z} 1 1.3",
      f'tellraw @s {{"text":"Ты — {title}.","color":"gold"}}', "function last_ember:char/effects", "function last_ember:char/open_hall"])
for slug, n, title, altar, sym, attrs, desc in CLASSES:
    t = [f'tellraw @s {{"text":"— {title} —","color":"gold","bold":true}}'] + [f'tellraw @s {{"text":"{l}","color":"gray"}}' for l in desc]
    w(f"class_desc_{n}", ["# as a player: description of the class"] + t + ['tellraw @s {"text":"ПКМ ещё раз в течение 10 секунд — выбрать.","color":"yellow"}'])
    x, y, z = pos(altar); sy = mk["altar_symbol_" + altar.split("_")[1]][1]
    w(f"class_choose_{n}", [f"# as a player: picks {title}", f"scoreboard players set @s le.class {n}", "function last_ember:char/gen/class_untag", f"tag @s add le.class.{slug}", f"function last_ember:char/gen/class_apply_{n}",
      f"particle minecraft:end_rod {x} {sy + 1.2} {z} 0.3 0.3 0.3 0.05 40", f"playsound minecraft:block.enchantment_table.use player @s {x} {y} {z} 1 1", f'tellraw @s {{"text":"Ты — {title}.","color":"gold"}}',
      "function last_ember:char/gen/light_stone", "function last_ember:char/give_kit", "function last_ember:char/effects", "function last_ember:char/open_font", "function last_ember:char/finish"])
w("light_stone", ["# as a player: the stone of his people on the bottom of the Font lights up"] +
  [f"execute if entity @s[tag=le.race.{r[0]}] run setblock {mk[NAME_STONE[r[0]]][0]} {mk[NAME_STONE[r[0]]][1]} {mk[NAME_STONE[r[0]]][2]} minecraft:sea_lantern" for r in RACES])
# dispatchers
w("race_desc", ["# as a player; #id le.e = 1..5"] + [f"execute if score #id le.e matches {r[1]} run function last_ember:char/gen/race_desc_{r[1]}" for r in RACES])
w("race_choose", ["# as a player; #id le.e = 1..5"] + [f"execute if score #id le.e matches {r[1]} run function last_ember:char/gen/race_choose_{r[1]}" for r in RACES])
w("class_desc", ["# as a player; #id le.e = 11..14"] + [f"execute if score #id le.e matches {10 + c[1]} run function last_ember:char/gen/class_desc_{c[1]}" for c in CLASSES])
w("class_choose", ["# as a player; #id le.e = 11..14"] + [f"execute if score #id le.e matches {10 + c[1]} run function last_ember:char/gen/class_choose_{c[1]}" for c in CLASSES])

# ---------------------------------------------------------------------------------------------- points (pads, altars, symbols)
def cname(t, color="gold"): return '{"text":"%s","color":"%s","italic":false}' % (t, color)
pts = ["# generated: interaction points of the Hall (built once their chunk is loaded)"]
def once(key, x, y, z, cmds):
    pts.append(f"execute unless data storage last_ember:char built.{key} if loaded {int(x)} {int(y)} {int(z)} in minecraft:overworld run function last_ember:char/gen/build_{key}")
    w(f"build_{key}", [f"data modify storage last_ember:char built.{key} set value 1b"] + cmds)
for slug, n, title, pad, ang, attrs, desc in RACES:
    x, y, z = mk[pad]
    once(f"pad{n}", x, y, z, [f"summon minecraft:interaction {x + 0.5} {y} {z + 0.5} {{width:3.0f,height:2.2f,response:1b,Tags:[\"le.cpad\",\"le.cnew\"]}}",
        f"execute positioned {x + 0.5} {y} {z + 0.5} run scoreboard players set @e[type=minecraft:interaction,tag=le.cnew,distance=..1] le.pid {n}",
        f"execute positioned {x + 0.5} {y} {z + 0.5} run tag @e[type=minecraft:interaction,tag=le.cnew,distance=..1] remove le.cnew"])
for slug, n, title, altar, sym, attrs, desc in CLASSES:
    x, y, z = mk[altar]; sx, sy, sz = mk["altar_symbol_" + altar.split("_")[1]]
    once(f"altar{n}", x, y, z, [f"summon minecraft:interaction {x + 0.5} {y - 0.5} {z + 0.5} {{width:5.0f,height:4.0f,response:1b,Tags:[\"le.cpad\",\"le.cnew\"]}}",
        f"execute positioned {x + 0.5} {y - 0.5} {z + 0.5} run scoreboard players set @e[type=minecraft:interaction,tag=le.cnew,distance=..1] le.pid {10 + n}",
        f"execute positioned {x + 0.5} {y - 0.5} {z + 0.5} run tag @e[type=minecraft:interaction,tag=le.cnew,distance=..1] remove le.cnew",
        f'summon minecraft:item_display {sx + 0.5} {sy + 0.1} {sz + 0.5} {{Tags:["le.csym"],billboard:"vertical",item:{{id:"{sym}",count:1}},transformation:{{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.9f,0.9f,0.9f]}}}}'])
w("build_points", pts)

# ---------------------------------------------------------------------------------------------- kits
def give(item, comps="", count=1): return f"give @s {item}{('[' + comps + ']') if comps else ''} {count}"
def keep(extra=""): return "minecraft:custom_data={le_keep:1b%s}" % extra
def nm(t, color="white"): return 'minecraft:custom_name={"text":"%s","color":"%s","italic":false}' % (t, color)
def lore(*ls): return "minecraft:lore=[" + ",".join('{"text":"%s","color":"gray","italic":false}' % l for l in ls) + "]"
blade = lambda n, extra: give("minecraft:stone_sword", ",".join([nm(n, "gray"), keep(extra), lore("Короткий клинок: бьёт быстро и слабо."),
    'minecraft:attribute_modifiers=[{type:"minecraft:attack_damage",id:"last_ember:dagger_damage",amount:2,operation:"add_value",slot:"mainhand"},{type:"minecraft:attack_speed",id:"last_ember:dagger_speed",amount:-2,operation:"add_value",slot:"mainhand"}]']))
w("kit_all", ["# as a player: the common start kit", give("minecraft:bread", count=6), give("minecraft:torch", count=8), give("minecraft:wooden_pickaxe"), give("minecraft:wooden_axe")])
w("kit_knight", ["# as a player", give("minecraft:stone_sword"), "item replace entity @s weapon.offhand with minecraft:shield", "item replace entity @s armor.chest with minecraft:chainmail_chestplate"])
w("kit_ranger", ["# as a player", give("minecraft:bow"), give("minecraft:arrow", count=32),
    give("minecraft:goat_horn", ",".join([nm("Рог следопыта", "gold"), keep(",le_horn:1b"), lore("Пока молчит.")]))])
STAFFS = [("blink", "Посох Мгновения"), ("frost", "Посох Хладной Длани"), ("flame", "Посох Пламенной Жатвы"), ("levity", "Посох Отринутой Тяжести"), ("exile", "Посох Изгнания")]
for i, (sid, sname) in enumerate(STAFFS, 1):
    w(f"staff_{i}", ["# as a player: a staff (stub item: name, description; the spells come in T-011)", give("minecraft:stick", ",".join([nm(sname, "light_purple"), keep(f',le_staff:"{sid}"'), lore("Заклинания посоха — позже.", "Пепельный Покров есть на любом посохе.")]))])
w("kit_seer", ["# as a player: a random staff of five (no Wrath of the Dead Sky), a dagger, the book", "execute store result score #rnd le.e run random value 1..5"] +
  [f"execute if score #rnd le.e matches {i} run function last_ember:char/gen/staff_{i}" for i in range(1, 6)] + [blade("Кинжал ворожея", ""),
  'give @s minecraft:written_book[minecraft:custom_data={le_keep:1b,le_book:1b},minecraft:written_book_content={title:"Книга ворожея",author:"Несущие",pages:["ПКМ — заклинание посоха.\\nShift + ПКМ — сменить заклинание.\\nУ каждого заклинания свой откат.\\nПосохи бывают разные: ищи их в сокровищницах.","Пепельный Покров есть на любом посохе: жёлтые сердца тебе и тем, кто рядом."]}] 1'])
w("kit_healer", ["# as a player", "function last_ember:bonfire/give_cauldron", blade("Нож знахаря", ""), give("minecraft:glass_bottle", count=3),
    give("minecraft:potion", "minecraft:potion_contents={potion:\"minecraft:healing\"}", 2), give("minecraft:brown_mushroom", count=4), give("minecraft:sugar", count=2)])
w("kit", ["# as a player: the kit of the class by tag (once: tag le.kit)", "execute if entity @s[tag=le.kit] run return 0", "tag @s add le.kit", "function last_ember:char/gen/kit_all"] +
  [f"execute if entity @s[tag=le.class.{c[0]}] run function last_ember:char/gen/kit_{c[0]}" for c in CLASSES])
print("char/gen written:", len(os.listdir(OUT)), "files")
