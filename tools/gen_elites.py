#!/usr/bin/env python3
"""T-014: elite mobs -> datapack (generated, do not edit): function/elite/gen/{region,name,dungeon,loot,helmet,stats_one}.mcfunction, loot_table/elite/<region>/<type>.json,
advancement/elite/xp_*.json + tags, trophy textures. Sources: death/regions.txt (regions), mobs/elite_names.txt, zones/zones.txt (zones with the flag `dungeon`).
Usage: python3 tools/gen_elites.py [zones_file]"""
import json, os, struct, sys, zlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, "datapack/data/last_ember"); GEN = os.path.join(DP, "function/elite/gen"); RP = os.path.join(ROOT, "resourcepack/assets/last_ember")
import shutil
shutil.rmtree(GEN, ignore_errors=True); shutil.rmtree(os.path.join(DP, "loot_table/elite"), ignore_errors=True)
for d in (GEN, os.path.join(DP, "tags/entity_type"), os.path.join(DP, "advancement/elite"), os.path.join(RP, "textures/item"), os.path.join(RP, "models/item"), os.path.join(RP, "items")): os.makedirs(d, exist_ok=True)
def w(name, lines): open(os.path.join(GEN, name + ".mcfunction"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
TYPES = ["zombie", "husk", "drowned", "zombie_villager", "skeleton", "stray", "bogged", "wither_skeleton", "spider", "cave_spider", "witch", "enderman", "blaze", "magma_cube", "slime", "piglin_brute", "zombified_piglin", "phantom"]
XP = {5: ["zombie", "husk", "drowned", "zombie_villager", "skeleton", "stray", "bogged", "wither_skeleton", "spider", "cave_spider", "witch", "enderman", "zombified_piglin", "phantom"], 10: ["blaze"], 20: ["piglin_brute"], 4: ["slime", "magma_cube"]}
def tag(name, vals): json.dump({"values": ["minecraft:" + v for v in vals]}, open(os.path.join(DP, "tags/entity_type/%s.json" % name), "w"), indent=1)
tag("elite_types", TYPES); tag("cube_mobs", ["slime", "magma_cube"])
for base, vals in XP.items():
    tag("elite_xp%d" % base, vals)
    json.dump({"criteria": {"c": {"trigger": "minecraft:player_killed_entity", "conditions": {"entity": {"type": "minecraft:entity_properties", "entity": "this", "predicate": {"minecraft:entity_type": "#last_ember:elite_xp%d" % base, "minecraft:nbt": "{Tags:[\"le.elite\"]}"}}}}}, "rewards": {"function": "last_ember:elite/xp_%d" % base}}, open(os.path.join(DP, "advancement/elite/xp_%d.json" % base), "w"))
    open(os.path.join(DP, "function/elite/xp_%d.mcfunction" % base), "w").write("# the experience of an elite is x3: the vanilla orbs are 1x, here is the other 2x (the base %d)\nadvancement revoke @s only last_ember:elite/xp_%d\nxp add @s %d points\n" % (base, base, base * 2))
# ------------------------------------------------------------------ regions
def rows(path):
    for l in open(path, encoding="utf-8"):
        l = l.split("#", 1)[0].strip()
        if l: yield l.split()
regions = []; names_seen = []
rg = ["# generated from death/regions.txt: #rg le.el = the region of this mob (0..6, 7 = Nether, -1 = none); the first matching line wins", "scoreboard players set #rg le.el -1"]
for r, urn, dim, x1, y1, z1, x2, y2, z2 in rows(os.path.join(ROOT, "death/regions.txt")):
    n = 7 if r == "nether" else int(r[1:])
    if r not in names_seen: names_seen.append(r)
    ax, bx = sorted((int(x1), int(x2))); ay, by = sorted((int(y1), int(y2))); az, bz = sorted((int(z1), int(z2)))
    rg.append("execute if score #rg le.el matches -1 if dimension minecraft:%s if entity @s[x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d] run scoreboard players set #rg le.el %d" % (dim, ax, ay, az, bx - ax, by - ay, bz - az, n))
w("region", rg)
RN = {r: (7 if r == "nether" else int(r[1:])) for r in names_seen}
# ------------------------------------------------------------------ dungeon zones
zf = os.path.join(ROOT, "zones/zones.txt") if len(sys.argv) < 2 else sys.argv[1]
dz = ["# generated from %s: #dg le.el = 1 when the mob is in a zone with the flag `dungeon`" % os.path.relpath(zf, ROOT), "scoreboard players set #dg le.el 0"]
for r in rows(zf):
    flags = set(",".join(r[3:]).replace(",", " ").split())
    if len(r) < 4 or "dungeon" not in flags: continue
    if r[2] == "box":
        x1, y1, z1, x2, y2, z2 = map(int, r[3:9]); dz.append("execute if dimension minecraft:%s if entity @s[x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d] run scoreboard players set #dg le.el 1" % (r[1], min(x1, x2), min(y1, y2), min(z1, z2), abs(x2 - x1), abs(y2 - y1), abs(z2 - z1)))
    elif r[2] == "cyl":
        cx, cz, rr, y1, y2 = map(int, r[3:8]); dz.append("execute if dimension minecraft:%s if entity @s[x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d] run scoreboard players set #dg le.el 1" % (r[1], cx - rr, y1, cz - rr, 2 * rr, y2 - y1, 2 * rr))
w("dungeon", dz)
# ------------------------------------------------------------------ names
names = {(r[0], r[1]): " ".join(r[2:]) for r in rows(os.path.join(ROOT, "mobs/elite_names.txt"))}
nm = ["# generated: storage last_ember:elite name = the name (a text component) of this mob in the region #rg le.el"]
for t in TYPES: nm.append('execute if entity @s[type=minecraft:%s] run data modify storage last_ember:elite name set value [{"translate":"entity.minecraft.%s","color":"dark_red"},{"text":" — элита","color":"dark_red"}]' % (t, t))
for (r, t), n in names.items(): nm.append('execute if score #rg le.el matches %d if entity @s[type=minecraft:%s] run data modify storage last_ember:elite name set value {"text":"%s","color":"dark_red"}' % (RN[r], t, n))
w("name", nm)
# ------------------------------------------------------------------ helmets, loot tables
COL = {0: 0x888888, 1: 0x4f7a3a, 2: 0x3a5f9a, 3: 0xdde6ee, 4: 0xc9b06a, 5: 0x333333, 6: 0x992222, 7: 0x771111}
w("helmet", ["# generated: a placeholder helmet of the colour of the region on a mob without a helmet (never dropped)"] + ["execute if score #rg le.el matches %d unless items entity @s armor.head * run item replace entity @s armor.head with minecraft:leather_helmet[minecraft:dyed_color=%d,minecraft:attribute_modifiers=[]]" % (n, c) for n, c in COL.items()])
loot = ["# generated: the loot table of the elite = the vanilla one + the trophy of the region (+ a small thing) when a player killed it"]
for r in names_seen:
    for t in TYPES:
        d = os.path.join(DP, "loot_table/elite", r); os.makedirs(d, exist_ok=True)
        trophy = {"type": "minecraft:item", "name": "minecraft:nautilus_shell", "modifier": [
            {"type": "minecraft:set_components", "components": {"minecraft:custom_data": {"le_trophy": r}, "minecraft:item_model": "last_ember:trophy_" + r, "minecraft:max_stack_size": 16, "minecraft:rarity": "rare",
                                                                 "minecraft:lore": [{"text": "Знак убитой элиты. Его ценят торговцы.", "color": "gray", "italic": False}]}},
            {"type": "minecraft:set_name", "entity": "this", "target": "custom_name", "name": {"text": "Трофей: ", "color": "gold", "italic": False, "extra": [{"selector": "@s", "color": "gold", "italic": False}]}}]}
        bits = [{"type": "minecraft:item", "name": "minecraft:glass_bottle"}, {"type": "minecraft:item", "name": "minecraft:arrow", "modifier": [{"type": "minecraft:set_count", "count": 4}]},
                {"type": "minecraft:item", "name": "minecraft:bread"}, {"type": "minecraft:item", "name": "minecraft:bone"}]
        json.dump({"type": "minecraft:entity", "pools": [
            {"rolls": 1, "entries": [{"type": "minecraft:loot_table", "value": "minecraft:entities/" + t}]},
            {"rolls": 1, "condition": {"type": "minecraft:killed_by_player"}, "entries": [trophy]},
            {"rolls": 1, "condition": {"type": "minecraft:all_of", "terms": [{"type": "minecraft:killed_by_player"}, {"type": "minecraft:random_chance", "chance": 0.25}]}, "entries": bits}]}, open(os.path.join(d, t + ".json"), "w"), ensure_ascii=False)
        loot.append('execute if score #rg le.el matches %d if entity @s[type=minecraft:%s] run data modify entity @s DeathLootTable set value "last_ember:elite/%s/%s"' % (RN[r], t, r, t))
w("loot", loot)
st = ["# generated: as an elite: count it into its region (#cnt_N le.el)"] + ["execute if score #rg le.el matches %d run scoreboard players add #cnt_%d le.el 1" % (n, n) for n in range(0, 8)]
w("stats_one", st)
# ------------------------------------------------------------------ trophy textures (placeholders: a skull-like mark of the region colour)
def png(path, px):
    raw = b"".join(b"\x00" + b"".join(bytes(p) for p in row) for row in px)
    def chunk(t, d): c = struct.pack(">I", len(d)) + t + d; return c + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 16, 16, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
for r in names_seen:
    c = COL[RN[r]]; col = ((c >> 16) & 255, (c >> 8) & 255, c & 255, 255); dark = tuple(int(v * 0.6) for v in col[:3]) + (255,)
    px = [[(0, 0, 0, 0)] * 16 for _ in range(16)]
    for y in range(3, 13):
        for x in range(3, 13):
            if (x - 7.5) ** 2 + (y - 7.5) ** 2 <= 22: px[y][x] = col
    for (x, y) in ((6, 6), (9, 6), (6, 7), (9, 7), (8, 10), (7, 10)): px[y][x] = dark
    png(os.path.join(RP, "textures/item/trophy_%s.png" % r), px)
    open(os.path.join(RP, "models/item/trophy_%s.json" % r), "w").write('{ "parent": "minecraft:item/generated", "textures": { "layer0": "last_ember:item/trophy_%s" } }\n' % r)
    open(os.path.join(RP, "items/trophy_%s.json" % r), "w").write('{ "model": { "type": "minecraft:model", "model": "last_ember:item/trophy_%s" } }\n' % r)
print("regions:", names_seen, "names:", len(names), "types:", len(TYPES))
