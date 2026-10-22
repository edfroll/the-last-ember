#!/usr/bin/env python3
"""T-010 part B (Healer): potion tables -> datapack functions (generated, do not edit):
  datapack/.../function/potion/gen/*.mcfunction, tags/item/potions.json, item_modifier/oil/*.json
Recipes (the table is here, one file, change without touching the code): docs/tasks/T-010-class-abilities.md, «Рецепты»."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, "datapack/data/last_ember")
GEN = os.path.join(DP, "function/potion/gen"); os.makedirs(GEN, exist_ok=True)
def w(name, lines, d=GEN): open(os.path.join(d, name + ".mcfunction"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
# ---------------------------------------------------------------- vanilla potions: id -> (colour, [(effect, duration ticks, amplifier)])
P = {
 "night_vision": (0x1F1FA1, [("night_vision", 3600, 0)]), "long_night_vision": (0x1F1FA1, [("night_vision", 9600, 0)]),
 "invisibility": (0x7F8392, [("invisibility", 3600, 0)]), "long_invisibility": (0x7F8392, [("invisibility", 9600, 0)]),
 "leaping": (0x22FF4C, [("jump_boost", 3600, 0)]), "long_leaping": (0x22FF4C, [("jump_boost", 9600, 0)]), "strong_leaping": (0x22FF4C, [("jump_boost", 1800, 1)]),
 "fire_resistance": (0xE49A3A, [("fire_resistance", 3600, 0)]), "long_fire_resistance": (0xE49A3A, [("fire_resistance", 9600, 0)]),
 "swiftness": (0x7CAFC6, [("speed", 3600, 0)]), "long_swiftness": (0x7CAFC6, [("speed", 9600, 0)]), "strong_swiftness": (0x7CAFC6, [("speed", 1800, 1)]),
 "slowness": (0x5A6C81, [("slowness", 1800, 0)]), "long_slowness": (0x5A6C81, [("slowness", 4800, 0)]), "strong_slowness": (0x5A6C81, [("slowness", 400, 3)]),
 "turtle_master": (0x6D5E32, [("slowness", 400, 3), ("resistance", 400, 2)]), "long_turtle_master": (0x6D5E32, [("slowness", 800, 3), ("resistance", 800, 2)]),
 "strong_turtle_master": (0x6D5E32, [("slowness", 400, 5), ("resistance", 400, 3)]),
 "water_breathing": (0x2E5299, [("water_breathing", 3600, 0)]), "long_water_breathing": (0x2E5299, [("water_breathing", 9600, 0)]),
 "healing": (0xF82423, [("instant_health", 1, 0)]), "strong_healing": (0xF82423, [("instant_health", 1, 1)]),
 "harming": (0xA9656A, [("instant_damage", 1, 0)]), "strong_harming": (0xA9656A, [("instant_damage", 1, 1)]),
 "poison": (0x87A363, [("poison", 900, 0)]), "long_poison": (0x87A363, [("poison", 1800, 0)]), "strong_poison": (0x87A363, [("poison", 432, 1)]),
 "regeneration": (0xCD5CAB, [("regeneration", 900, 0)]), "long_regeneration": (0xCD5CAB, [("regeneration", 1800, 0)]), "strong_regeneration": (0xCD5CAB, [("regeneration", 450, 1)]),
 "strength": (0x932423, [("strength", 3600, 0)]), "long_strength": (0x932423, [("strength", 9600, 0)]), "strong_strength": (0x932423, [("strength", 1800, 1)]),
 "weakness": (0x484D48, [("weakness", 1800, 0)]), "long_weakness": (0x484D48, [("weakness", 4800, 0)]),
 "luck": (0x59C106, [("luck", 6000, 0)]), "slow_falling": (0xF3CFB9, [("slow_falling", 1800, 0)]), "long_slow_falling": (0xF3CFB9, [("slow_falling", 4800, 0)]),
}
EFFECT_COLOR = {"night_vision": 0x1F1FA1, "invisibility": 0x7F8392, "jump_boost": 0x22FF4C, "fire_resistance": 0xE49A3A, "speed": 0x7CAFC6, "slowness": 0x5A6C81, "resistance": 0x6D5E32,
                "water_breathing": 0x2E5299, "instant_health": 0xF82423, "instant_damage": 0xA9656A, "poison": 0x87A363, "regeneration": 0xCD5CAB, "strength": 0x932423, "weakness": 0x484D48,
                "luck": 0x59C106, "slow_falling": 0xF3CFB9, "nausea": 0x551D4A, "wither": 0x352A27, "hunger": 0x587653, "blindness": 0x1F1F23}
def eff(e, d, a): return '{id:"minecraft:%s",duration:%d,amplifier:%db}' % (e, d, a)
def instant(e): return e in ("instant_health", "instant_damage")
# boosted variants of the base potions: duration x1.5, "u" = amplifier +1 (not above II)
for pid, (col, effs) in P.items():
    for mode in ("n", "u", "b"):          # n: boosted, u: boosted and +1 level, b: plain (modifier input, no boost)
        out = []
        for e, d, a in effs:
            if mode == "b": out.append(eff(e, d, a)); continue
            d2 = d if instant(e) else int(d * 1.5); a2 = min(a + 1, 1) if mode == "u" and a < 1 else a
            out.append(eff(e, d2, a2))
        w(f"b_{pid}_{mode}", [f"data modify storage last_ember:pt pc set value {{custom_effects:[{','.join(out)}],custom_color:{col}}}"])
# dispatchers are macros ($function ...b_$(pid)_$(m))
# ---------------------------------------------------------------- item tag
os.makedirs(os.path.join(DP, "tags/item"), exist_ok=True)
json.dump({"values": ["minecraft:potion", "minecraft:splash_potion", "minecraft:lingering_potion"]}, open(os.path.join(DP, "tags/item/potions.json"), "w"))
# ---------------------------------------------------------------- inventory scan: 36 slots
scan = ["# as a healer, every second: potions without le_boost are boosted, murky vials are identified"]
for n in range(36):
    scan.append(f"execute if items entity @s container.{n} #last_ember:potions unless items entity @s container.{n} *[minecraft:custom_data~{{le_boost:1b}}] unless items entity @s container.{n} *[minecraft:custom_data~{{le_murky:1b}}] unless items entity @s container.{n} *[minecraft:custom_data~{{le_oilitem:1b}}] unless items entity @s container.{n} *[minecraft:custom_data~{{le_antidote:1b}}] run function last_ember:potion/boost_slot {{slot:{n}}}")
    scan.append(f"execute if items entity @s container.{n} minecraft:potion[minecraft:custom_data~{{le_murky:1b}}] run function last_ember:potion/identify_slot {{slot:{n}}}")
w("scan", scan, os.path.join(DP, "function/potion"))
print("potion/gen:", len(os.listdir(GEN)), "functions")

# ================================================================== the cauldron: ingredients, recipes (ONE table), masks
ING = {  # bit -> (label, [item ids], returned bucket/bottle)
 0: ("mushroom", ["brown_mushroom", "red_mushroom"], None), 1: ("cooked meat", ["cooked_beef", "cooked_porkchop", "cooked_chicken", "cooked_mutton", "cooked_rabbit", "cooked_cod", "cooked_salmon"], None),
 2: ("sugar", ["sugar"], None), 3: ("bone", ["bone"], None), 4: ("gunpowder", ["gunpowder"], None), 5: ("rabbit foot", ["rabbit_foot"], None), 6: ("pumpkin", ["pumpkin"], None),
 7: ("glow berries", ["glow_berries"], None), 8: ("spider eye", ["spider_eye"], None), 9: ("rotten flesh", ["rotten_flesh"], None), 10: ("lava", ["lava_bucket"], "bucket"),
 11: ("honey", ["honey_bottle"], "glass_bottle"), 12: ("raw fish", ["cod", "salmon", "tropical_fish", "pufferfish"], None), 13: ("kelp", ["kelp"], None), 14: ("milk", ["milk_bucket"], "bucket"),
 15: ("slime", ["slime_ball"], None), 16: ("charcoal", ["charcoal"], None), 17: ("bone meal", ["bone_meal"], None), 18: ("cobweb", ["cobweb"], None),
}
POT = 20
RECIPES = {  # name -> (ingredient bits, output)   output: ("potion", potion id, item type) | ("item", template)
 "healing": ([0, 1, 2], ("potion", "healing", "potion")), "strength": ([0, 3, 4], ("potion", "strength", "potion")), "speed": ([0, 5], ("potion", "swiftness", "potion")),
 "night_vision": ([0, 6, 7], ("potion", "night_vision", "potion")), "poison": ([0, 8, 9], ("potion", "poison", "splash_potion")),
 "fire_resistance": ([0, 10, 11], ("potion", "fire_resistance", "potion")), "water_breathing": ([0, 12, 13], ("potion", "water_breathing", "potion")),
 "antidote": ([0, 11, 7, 14], ("item", "antidote")), "oil_poison": ([0, 8, 15], ("item", "oil_poison")), "oil_fire": ([0, 16, 4], ("item", "oil_fire")),
}
MODS = {"longer": ([11, 2], "дольше"), "stronger": ([17], "сильнее"), "splash": ([4], "взрывное"), "lingering": ([18], "туманное")}   # modifier -> (alternative bits, label)
def mask(bits): return sum(1 << b for b in bits)
# item templates (storage form of an item stack) for the ground output
def comp_lore(*ls): return "[" + ",".join('{text:"%s",color:"gray",italic:false}' % l for l in ls) + "]"
TEMPLATES = {
 "antidote": '{id:"minecraft:potion",count:1,components:{"minecraft:custom_data":{le_antidote:1b},"minecraft:custom_name":{text:"Противоядие",italic:false,color:"green"},"minecraft:potion_contents":{custom_color:11141120},"minecraft:lore":%s}}' % comp_lore("Снимает отравление и иссушение.", "60 секунд невосприимчивости к ним.", "Усилено знахарем"),
 "oil_poison": '{id:"minecraft:potion",count:1,components:{"minecraft:custom_data":{le_oilitem:1b,le_oiltype:"poison",le_boost:1b},"minecraft:custom_name":{text:"Масло яда",italic:false,color:"green"},"minecraft:potion_contents":{custom_color:8890211},"minecraft:consumable":{consume_seconds:1.0f,animation:"drink",has_consume_particles:false},"minecraft:lore":%s}}' % comp_lore("Возьми клинок в основную руку, масло в левую, ПКМ."),
 "oil_fire": '{id:"minecraft:potion",count:1,components:{"minecraft:custom_data":{le_oilitem:1b,le_oiltype:"fire",le_boost:1b},"minecraft:custom_name":{text:"Масло огня",italic:false,color:"gold"},"minecraft:potion_contents":{custom_color:16737792},"minecraft:consumable":{consume_seconds:1.0f,animation:"drink",has_consume_particles:false},"minecraft:lore":%s}}' % comp_lore("Возьми клинок в основную руку, масло в левую, ПКМ."),
}
CF = os.path.join(DP, "function/potion")
# ingredient detection (as an item entity): sets #bit to 2^bit (0 = not an ingredient); potion items set 2^POT
ing = ["# as an item entity: #bit le.e = its ingredient value (0 = not an ingredient, 2^20 = a potion for modifying)", "scoreboard players set #bit le.e 0"]
for b, (lab, items, ret) in ING.items():
    for it in items: ing.append(f"execute if items entity @s contents minecraft:{it} run scoreboard players set #bit le.e {1 << b}")
for it in ("potion", "splash_potion", "lingering_potion"): ing.append(f"execute if items entity @s contents minecraft:{it} run scoreboard players set #bit le.e {1 << POT}")
w("ingredient", ing, CF)
# valid masks: every subset of every recipe (also POT alone and POT + modifier)
valid = set()
for name, (bits, out) in RECIPES.items():
    for k in range(1 << len(bits)): valid.add(sum(1 << bits[i] for i in range(len(bits)) if k >> i & 1))
valid.add(1 << POT)
for m, (alts, lab) in MODS.items():
    for b in alts: valid.add((1 << POT) + (1 << b))
w("valid", ["# as the cauldron: #ok le.e = 1 when the mask le.cmask can still become a recipe (prefix of some recipe)", "scoreboard players set #ok le.e 0"] +
  [f"execute if score @s le.cmask matches {v} run scoreboard players set #ok le.e 1" for v in sorted(valid) if v], CF)
# match: which recipe is complete? (stores le.crec 1..N for recipes, 101.. for modifiers) -- base ready is checked by the caller
names = list(RECIPES)
m = ["# as the cauldron: the mask equals a whole recipe -> le.crec (1..), modifiers 101.."] + ["scoreboard players set @s le.crec 0"]
for i, name in enumerate(names, 1): m.append(f"execute if score @s le.cmask matches {mask(RECIPES[name][0])} run scoreboard players set @s le.crec {i}")
mods = []
for j, (mn, (alts, lab)) in enumerate(MODS.items(), 1):
    for b in alts: m.append(f"execute if score @s le.cmask matches {(1 << POT) + (1 << b)} run scoreboard players set @s le.crec {100 + j}")
w("match", m, CF)
# result: per recipe a function that fills storage last_ember:pt it and (pid, ty) for potions
for i, name in enumerate(names, 1):
    bits, out = RECIPES[name]
    if out[0] == "potion":
        _, pid, ty = out
        w(f"res_{i}", [f"# recipe {name}", f'data modify storage last_ember:pt it set value {{id:"minecraft:{ty}",count:1,components:{{"minecraft:potion_contents":{{potion:"minecraft:{pid}"}}}}}}',
                       f'data modify storage last_ember:pt pid set value "{pid}"', f'data modify storage last_ember:pt ty set value "{ty}"', "function last_ember:potion/boost_it"], CF)
    else:
        w(f"res_{i}", [f"# recipe {name}", f"data modify storage last_ember:pt it set value {TEMPLATES[out[1]]}"], CF)
w("result", ["# as the cauldron: storage last_ember:pt it = one result item of recipe le.crec"] + [f"execute if score @s le.crec matches {i} run function last_ember:potion/res_{i}" for i in range(1, len(names) + 1)], CF)
rets = ["# as the cauldron: returned empty buckets / bottles for the used ingredients"]
for b, (lab, items, ret) in ING.items():
    if ret:
        rets.append(f"execute store result score #t le.e run scoreboard players get @s le.cmask")
        rets.append(f"scoreboard players operation #t le.e /= #{1 << b} le.e")
        rets.append("scoreboard players operation #t le.e %= #2 le.e")
        rets.append(f'execute if score #t le.e matches 1 run summon minecraft:item ~ ~0.6 ~ {{Item:{{id:"minecraft:{ret}",count:1}},Motion:[0.0d,0.2d,0.2d]}}')
w("returns", rets, CF)
w("consts", ["# generated constants (powers of two for the mask arithmetic)"] + [f"scoreboard players set #{1 << b} le.e {1 << b}" for b in ING] + [f"scoreboard players set #{1 << POT} le.e {1 << POT}", "scoreboard players set #2 le.e 2"], CF)
print("brew tables:", len(valid), "valid masks,", len(names), "recipes")
