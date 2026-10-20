#!/usr/bin/env python3
"""T-001 generator: (1) strip ore/precious items from vanilla loot tables, (2) strip zombie food/iron drops,
(3) disable natural generation of all structures incl. end_city (structure_set -> empty), (4) monster_room dungeons off.
Reads vanilla data from server/generated/data; writes overrides into datapack/. Idempotent. Run: python3 tools/gen_t001.py
Not touched on purpose: blocks/* loot (redstone_wire must keep dropping dust), gameplay/piglin_bartering (economy task), End structures.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "server/generated/data/minecraft")
OUT = os.path.join(ROOT, "datapack/data/minecraft")
MANIFEST = os.path.join(ROOT, "tools/.t001-manifest")

GEAR = r"(iron|golden|diamond|chainmail|copper|netherite)_(sword|pickaxe|axe|shovel|hoe|helmet|chestplate|leggings|boots|spear|\w*horse_armor|\w*nautilus_armor)"
BANNED = re.compile(r"^minecraft:(" + GEAR + r"|raw_(iron|gold|copper)(_block)?|(iron|gold|copper)_(ingot|nugget|block)|diamond(_block)?|"
                    r"emerald(_block)?|lapis_lazuli|lapis_block|redstone(_block)?|netherite_scrap|ancient_debris|\w+_ore)$")
ZOMBIE_EXTRA = {"minecraft:carrot", "minecraft:potato"}
ZOMBIES = {"zombie", "husk", "zombie_villager", "drowned"}
LOOT_SKIP = ("blocks/", "gameplay/piglin_bartering")  # blocks keep dropping dust etc.; bartering is the economy task
KEEP_STRUCTURE_SETS = set()  # T-001b: end_city is disabled too

def load(p):
    with open(p) as f: return json.load(f)

def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False); f.write("\n")

def strip_entries(entries, banned, removed):
    out = []
    for e in entries:
        if e.get("type") == "minecraft:item" and (e.get("name") in banned or BANNED.match(e.get("name", ""))):
            removed.add(e["name"]); continue
        if e.get("type") == "minecraft:tag" and BANNED.match(e.get("name", "")):
            removed.add(e["name"]); continue
        if isinstance(e.get("value"), dict) and "pools" in e["value"]:  # inline nested loot table
            process_pools(e["value"], banned, removed)
            if not e["value"]["pools"]: continue
        if "children" in e:
            e["children"] = strip_entries(e["children"], banned, removed)
            if not e["children"]: continue
        out.append(e)
    return out

def process_pools(t, banned, removed):
    pools = []
    for p in t.get("pools", []):
        before = len(p.get("entries", []))
        p["entries"] = strip_entries(p.get("entries", []), banned, removed)
        if p["entries"] or before == 0:
            pools.append(p)
    t["pools"] = pools

def process_table(t, extra):
    removed = set()
    process_pools(t, set(extra), removed)
    return removed

def main():
    if os.path.exists(MANIFEST):
        for rel in open(MANIFEST).read().split():
            p = os.path.join(OUT, rel)
            if os.path.exists(p): os.remove(p)
    written, report = [], []
    base = os.path.join(GEN, "loot_table")
    for dp, _, fns in os.walk(base):
        for fn in sorted(fns):
            if not fn.endswith(".json"): continue
            path = os.path.join(dp, fn)
            name = os.path.relpath(path, base)[:-5]
            if name.startswith(LOOT_SKIP[0]) or name == LOOT_SKIP[1]: continue
            t = load(path)
            extra = ZOMBIE_EXTRA if name.startswith("entities/") and name.split("/")[1] in ZOMBIES else set()
            removed = process_table(t, extra)
            if removed:
                rel = f"loot_table/{name}.json"
                dump(os.path.join(OUT, rel), t); written.append(rel)
                report.append(f"loot {name}: -{sorted(x.replace('minecraft:', '') for x in removed)}")
    sdir = os.path.join(GEN, "worldgen/structure_set")
    for fn in sorted(os.listdir(sdir)):
        if fn[:-5] in KEEP_STRUCTURE_SETS: continue
        s = load(os.path.join(sdir, fn)); n = len(s["structures"]); s["structures"] = []
        rel = f"worldgen/structure_set/{fn}"
        dump(os.path.join(OUT, rel), s); written.append(rel)
        report.append(f"structure_set {fn[:-5]}: {n} structure(s) disabled")
    # item tag of metal/diamond/chainmail gear: used by last_ember:mob_eq to zero drop chances of natural mobs' gear
    reg = load(os.path.join(ROOT, "server/generated/reports/registries.json"))["minecraft:item"]["entries"]
    gear = sorted(i for i in reg if BANNED.match(i) and re.match(r"minecraft:" + GEAR + "$", i))
    rel = "../last_ember/tags/item/metal_gear.json"
    dump(os.path.join(OUT, rel), {"values": gear}); written.append(rel)
    report.append(f"item tag last_ember:metal_gear: {len(gear)} items")
    # dungeons with spawners (placed features monster_room, monster_room_deep both use this configured feature)
    rel = "worldgen/feature/monster_room.json"
    dump(os.path.join(OUT, rel), {"type": "minecraft:no_op", "config": {}}); written.append(rel)
    report.append("feature monster_room: disabled (dungeons)")
    with open(MANIFEST, "w") as f: f.write("\n".join(written) + "\n")
    print("\n".join(report)); print(f"{len(written)} files written")

if __name__ == "__main__":
    main()
