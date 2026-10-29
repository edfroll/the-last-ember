#!/usr/bin/env python3
"""T-011: the seer's staffs -> datapack functions (generated, do not edit): datapack/.../function/seer/gen/*.mcfunction, tags/block/blink_pass.json,
the zone check for fire (seer/gen/zone_fire). Spells themselves are hand-written in function/seer/*.mcfunction.
Usage: python3 tools/gen_seer.py"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, "datapack/data/last_ember"); GEN = os.path.join(DP, "function/seer/gen"); os.makedirs(GEN, exist_ok=True)
def w(name, lines, d=GEN): open(os.path.join(d, name + ".mcfunction"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
# id, spell number, name, colour, spell text
STAFFS = [("blink", 2, "Посох Мгновения", "light_purple", "Мгновенный перенос туда, куда смотрит ворожей."), ("frost", 3, "Посох Хладной Длани", "aqua", "Враги вокруг замедлены, ослаблены и в инее."),
          ("flame", 4, "Посох Пламенной Жатвы", "gold", "Враги вокруг загораются."), ("lift", 5, "Посох Отринутой Тяжести", "white", "Враги вокруг взлетают и падают."),
          ("banish", 6, "Посох Изгнания", "green", "Враги отлетают от ворожея."), ("wrath", 7, "Посох «Гнев Мёртвого Неба»", "dark_red", "Молния в точку взгляда; зажми ПКМ, чтобы копить заряд.")]
def comps(sid, name, color, text, remainder=True):
    anim = "bow" if sid == "wrath" else "none"
    c = [f'minecraft:item_model="last_ember:staff_{sid}"', f'minecraft:custom_data={{le_keep:1b,le_staff:"{sid}"}}', f'minecraft:custom_name={{"text":"{name}","color":"{color}","italic":false}}',
         f'minecraft:lore=[{{"text":"{text}","color":"gray","italic":false}},{{"text":"ПКМ — заклинание, Shift + ПКМ — сменить заклинание.","color":"dark_gray","italic":false}},{{"text":"Пепельный Покров есть на любом посохе.","color":"dark_gray","italic":false}}]',
         f'minecraft:consumable={{consume_seconds:10.0f,animation:"{anim}",sound:"minecraft:intentionally_empty",has_consume_particles:false}}', "minecraft:max_stack_size=1"]
    return c
def snbt(c):
    out = []; idx = [m.start() for m in re.finditer(r'(?:^|,)(minecraft:[a-z_]+)=', ",".join(c))]; s = ",".join(c)
    for i, st in enumerate(idx):
        seg = s[st + (1 if s[st] == "," else 0):(idx[i + 1] if i + 1 < len(idx) else len(s))]; k, v = seg.split("=", 1); out.append('"%s":%s' % (k, v))
    return ",".join(out)
for sid, n, name, color, text in STAFFS:
    c = comps(sid, name, color, text)
    w(f"give_{sid}", [f"# as a player: {name}", 'give @s minecraft:stick[%s,minecraft:use_remainder={id:"minecraft:stick",count:1,components:{%s}}] 1' % (",".join(c), snbt(c))])
# T-019: every staff as a loot table last_ember:item/staff_<id> (treasuries take them from there)
LT = os.path.join(DP, "loot_table/item"); os.makedirs(LT, exist_ok=True)
for sid, n, name, color, text in STAFFS:
    tx = lambda t, c: {"text": t, "color": c, "italic": False}
    c = {"minecraft:item_model": f"last_ember:staff_{sid}", "minecraft:custom_data": f'{{le_keep:1b,le_staff:"{sid}"}}', "minecraft:custom_name": tx(name, color),
         "minecraft:lore": [tx(text, "gray"), tx("ПКМ — заклинание, Shift + ПКМ — сменить заклинание.", "dark_gray"), tx("Пепельный Покров есть на любом посохе.", "dark_gray")],
         "minecraft:consumable": {"consume_seconds": 10.0, "animation": "bow" if sid == "wrath" else "none", "sound": "minecraft:intentionally_empty", "has_consume_particles": False},
         "minecraft:max_stack_size": 1}
    c2 = dict(c); c2["minecraft:use_remainder"] = {"id": "minecraft:stick", "count": 1, "components": c}
    json.dump({"type": "minecraft:generic", "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": "minecraft:stick", "modifier": {"type": "minecraft:set_components", "components": c2}}]}]},
              open(os.path.join(LT, f"staff_{sid}.json"), "w"), ensure_ascii=False, indent=1)
w("staff_cast", ["# as a seer holding a staff: the staff's own spell"] + [f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{le_staff:"{sid}"}}] run return run function last_ember:seer/cast_{n}' for sid, n, *_ in STAFFS])
w("staff_number", ["# as a seer: #sel le.e = the number of the selected spell (1 = the Ashen Cover, else the staff's own)", "scoreboard players set #sel le.e 1",
                   "execute if score @s le.spsel matches 1 run return 1"] + [f'execute if items entity @s weapon.mainhand *[minecraft:custom_data~{{le_staff:"{sid}"}}] run scoreboard players set #sel le.e {n}' for sid, n, *_ in STAFFS])
names = ["# as a seer: storage last_ember:seer h.name = the name of the selected spell"] + ['data modify storage last_ember:seer h.name set value "Пепельный Покров"']
for sid, n, name, *_ in STAFFS: names.append(f'execute unless score @s le.spsel matches 1 if items entity @s weapon.mainhand *[minecraft:custom_data~{{le_staff:"{sid}"}}] run data modify storage last_ember:seer h.name set value "{name}"')
w("spell_name", names)
w("cd_remaining", ["# as a seer: #r le.e = seconds left of the spell #sel (0 = ready)", "scoreboard players set #r le.e 0"] +
  [f"execute if score #sel le.e matches {k} run scoreboard players operation #r le.e = @s le.cd{k}" for k in range(1, 8)] +
  ["scoreboard players operation #r le.e -= #gt le.e", "execute if score #r le.e matches ..0 run return run scoreboard players set #r le.e 0", "scoreboard players add #r le.e 19", "scoreboard players operation #r le.e /= #20 le.e"])
# ---------------------------------------------------------------- the blink pass tag: blocks the ray passes through
json.dump({"values": ["minecraft:air", "minecraft:cave_air", "minecraft:void_air", "minecraft:short_grass", "minecraft:tall_grass", "minecraft:fern", "minecraft:large_fern", "minecraft:dead_bush", "minecraft:vine",
                       "minecraft:snow", "minecraft:glow_lichen", "minecraft:light", "minecraft:sugar_cane", "minecraft:sweet_berry_bush", "minecraft:moss_carpet", "minecraft:short_dry_grass", "minecraft:tall_dry_grass",
                       "#minecraft:flowers", "#minecraft:small_flowers", "#minecraft:saplings", "#minecraft:buttons", "#minecraft:signs", "#minecraft:wall_signs", "#minecraft:rails", "#minecraft:wool_carpets", "minecraft:moss_carpet", "#minecraft:crops"]},
          open(os.path.join(DP, "tags/block/blink_pass.json"), "w"), indent=1)
# ---------------------------------------------------------------- zones for the fire: a point inside any zone (box / cylinder with the 5 block margin) -> no fire
def rows(p):
    for l in open(p, encoding="utf-8"):
        l = l.split("#", 1)[0].strip()
        if l: yield l.split()
zl = ["# generated by tools/gen_seer.py from zones/zones.txt and zones/bonfires.gen.txt: fire may not be placed inside the indestructible zones (5 blocks of margin)", "scoreboard players set #inz le.e 0"]
for p in ("zones/zones.txt", "zones/bonfires.gen.txt"):
    for r in rows(os.path.join(ROOT, p)):
        if len(r) < 4 or r[1] != "overworld": continue
        if r[2] == "box":
            x1, y1, z1, x2, y2, z2 = map(int, r[3:9]); zl.append(f"execute if entity @s[x={min(x1, x2) - 5},y={min(y1, y2) - 5},z={min(z1, z2) - 5},dx={abs(x2 - x1) + 10},dy={abs(y2 - y1) + 10},dz={abs(z2 - z1) + 10}] run scoreboard players set #inz le.e 1")
        elif r[2] == "cyl":
            cx, cz, rr, y1, y2 = map(int, r[3:8]); m = rr + 5
            zl.append(f"execute if entity @s[x={cx - m},y={y1 - 5},z={cz - m},dx={2 * m},dy={y2 - y1 + 10},dz={2 * m}] run scoreboard players set #inz le.e 1")
w("zone_fire", zl)
print("seer/gen:", len(os.listdir(GEN)), "functions")

# ---------------------------------------------------------------- the cast wrappers: cooldown check -> do_N (returns 1 = success) -> cooldown set
CD = {1: 40, 2: 8, 3: 20, 4: 25, 5: 20, 6: 12, 7: 15}
for n, cd in CD.items():
    if n == 7: continue
    w(f"cast_{n}", [f"# as a seer: the spell {n} (cooldown {cd} s, kept on the player)", f"execute if score #gt le.e < @s le.cd{n} run return run function last_ember:seer/cd_msg {{n:{n}}}",
                    f"execute store result score #ok le.e run function last_ember:seer/do_{n}", "execute unless score #ok le.e matches 1 run return 0",
                    f"scoreboard players operation @s le.cd{n} = #gt le.e", f"scoreboard players add @s le.cd{n} {cd * 20}", "function last_ember:seer/hint"], os.path.join(DP, "function/seer"))
print("cast wrappers:", [n for n in CD if n != 7])

# ---------------------------------------------------------------- Lift: the upward speed that makes a mob rise H blocks (vanilla mob gravity 0.08, drag 0.98), H = 6 + tier
def rise(v):
    y = 0.0; vy = v
    for _ in range(400):
        y += vy
        if vy <= 0: break
        vy = (vy - 0.08) * 0.98
    return y
def speed_for(H):
    lo, hi = 0.3, 3.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if rise(mid) < H: lo = mid
        else: hi = mid
    return round((lo + hi) / 2, 3)
lv = ["# generated: the upward speed for the lift height H = 6 (tier 0) .. 12 (tier 6) blocks -> storage last_ember:seer c.v"]
for t in range(7): lv.append(f"execute if score @s le.tier matches {t} run data modify storage last_ember:seer c.v set value {speed_for(6 + t):.3f}d")
w("lift_speed", lv)
# ---------------------------------------------------------------- Flame: flammable blocks within 2 blocks of the fire point (trees, leaves, wool, hay and wooden things)
near = ["# generated: #nf le.e = 1 when a flammable block (logs, planks, leaves, wool, hay) is within 2 blocks of ~ ~ ~", "scoreboard players set #nf le.e 0"]
for dx in range(-2, 3):
    for dy in range(-1, 3):
        for dz in range(-2, 3):
            near.append(f"execute if block ~{dx} ~{dy} ~{dz} #last_ember:flammable run scoreboard players set #nf le.e 1")
w("fire_near", near)
json.dump({"values": ["#minecraft:logs_that_burn", "#minecraft:planks", "#minecraft:leaves", "#minecraft:wool", "minecraft:hay_block", "#minecraft:wooden_fences", "#minecraft:wooden_doors", "#minecraft:wooden_slabs", "#minecraft:wooden_stairs",
                       "minecraft:bookshelf", "#minecraft:wool_carpets", "#minecraft:banners", "minecraft:scaffolding", "#minecraft:fence_gates", "minecraft:composter", "#minecraft:flowers", "minecraft:tall_grass", "minecraft:short_grass", "minecraft:vine", "minecraft:dried_kelp_block"]},
          open(os.path.join(DP, "tags/block/flammable.json"), "w"), indent=1)
json.dump({"values": ["#minecraft:base_stone_overworld", "#minecraft:dirt", "#minecraft:sand", "minecraft:gravel", "minecraft:grass_block", "#minecraft:terracotta", "#minecraft:stone_bricks", "minecraft:cobblestone", "minecraft:mossy_cobblestone",
                       "minecraft:deepslate", "minecraft:cobbled_deepslate", "#minecraft:snow", "minecraft:netherrack", "minecraft:mud", "minecraft:clay", "minecraft:coarse_dirt", "minecraft:podzol"]},
          open(os.path.join(DP, "tags/block/fire_floor.json"), "w"), indent=1)
print("lift speeds:", [speed_for(6 + t) for t in range(7)])

# ---------------------------------------------------------------- Wrath: the charge bar over the hotbar (0..10 segments of 20 ticks = 10 s)
for n in range(11):
    col = "red" if n >= 10 else "gold"
    w(f"bar_{n}", [f"# generated: the charge {n}/10", 'title @s actionbar [{"text":"Заряд ","color":"gray"},{"text":"%s","color":"%s"},{"text":"%s","color":"dark_gray"}]' % ("\u2588" * n, col, "\u2588" * (10 - n))])
