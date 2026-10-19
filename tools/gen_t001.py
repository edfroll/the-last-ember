#!/usr/bin/env python3
"""T-001 generator: (1) strip ore/precious items from vanilla loot tables, (2) strip zombie food/iron drops,
(3) disable natural generation of all Overworld/Nether structures (structure_set -> empty).
Reads vanilla data from server/generated/data; writes overrides into datapack/. Idempotent. Run: python3 tools/gen_t001.py
Not touched on purpose: blocks/* loot (redstone_wire must keep dropping dust), gameplay/piglin_bartering (economy task), End structures.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "server/generated/data/minecraft")
OUT = os.path.join(ROOT, "datapack/data/minecraft")
MANIFEST = os.path.join(ROOT, "tools/.t001-manifest")

BANNED = re.compile(r"^minecraft:(raw_(iron|gold|copper)(_block)?|(iron|gold|copper)_(ingot|nugget|block)|diamond(_block)?|"
                    r"emerald(_block)?|lapis_lazuli|lapis_block|redstone(_block)?|netherite_scrap|ancient_debris|\w+_ore)$")
ZOMBIE_EXTRA = {"minecraft:carrot", "minecraft:potato"}
ZOMBIES = {"zombie", "husk", "zombie_villager", "drowned"}
LOOT_DIRS = ["chests", "archaeology", "pots", "entities", "gameplay/hero_of_the_village"]
KEEP_STRUCTURE_SETS = {"end_cities"}  # End is out of scope

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
        if "children" in e:
            e["children"] = strip_entries(e["children"], banned, removed)
            if not e["children"]: continue
        out.append(e)
    return out

def process_table(t, extra):
    removed = set()
    banned = set(extra)
    pools = []
    for p in t.get("pools", []):
        before = len(p.get("entries", []))
        p["entries"] = strip_entries(p.get("entries", []), banned, removed)
        if p["entries"] or before == 0:
            pools.append(p)
    t["pools"] = pools
    return removed

def main():
    if os.path.exists(MANIFEST):
        for rel in open(MANIFEST).read().split():
            p = os.path.join(OUT, rel)
            if os.path.exists(p): os.remove(p)
    written, report = [], []
    for d in LOOT_DIRS:
        base = os.path.join(GEN, "loot_table", d)
        for dp, _, fns in os.walk(base):
            for fn in sorted(fns):
                if not fn.endswith(".json"): continue
                path = os.path.join(dp, fn)
                t = load(path)
                name = os.path.relpath(path, os.path.join(GEN, "loot_table"))[:-5]
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
    with open(MANIFEST, "w") as f: f.write("\n".join(written) + "\n")
    print("\n".join(report)); print(f"{len(written)} files written")

if __name__ == "__main__":
    main()
