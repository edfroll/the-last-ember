#!/usr/bin/env python3
"""Generate datapack overrides that remove all natural ore generation (task: world without ore).

Reads vanilla data from server/generated/data (data generator output) and writes overrides into datapack/.
Idempotent: removes previously generated files first. Run: python3 tools/gen_no_ore.py
"""
import json, os, re, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "server/generated/data/minecraft")
OUT = os.path.join(ROOT, "datapack/data")
MARK = os.path.join(ROOT, "tools/.no-ore-manifest")  # list of generated files, for cleanup

ORE = re.compile(r"minecraft:(\w+_ore|ancient_debris)$")
STRIP_TO = {  # decorative ore blocks in structures -> harmless replacement
    "coal_ore": "cobblestone", "iron_ore": "cobblestone", "gold_ore": "cobblestone",
}

def load(p):
    with open(p) as f:
        return json.load(f)

def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")

def ore_blocks(node, acc):
    if isinstance(node, dict):
        for v in node.values():
            ore_blocks(v, acc)
    elif isinstance(node, list):
        for v in node:
            ore_blocks(v, acc)
    elif isinstance(node, str) and ORE.match(node):
        acc.add(node)

def main():
    if os.path.exists(MARK):
        for rel in open(MARK).read().split():
            p = os.path.join(OUT, rel)
            if os.path.exists(p):
                os.remove(p)
    written = []

    def w(rel, obj):
        dump(os.path.join(OUT, rel), obj)
        written.append(rel)

    report = []
    # 1) configured features that place ore blocks -> no_op
    fdir = os.path.join(GEN, "worldgen/feature")
    for fn in sorted(os.listdir(fdir)):
        if not fn.endswith(".json"):
            continue
        d = load(os.path.join(fdir, fn))
        found = set()
        ore_blocks(d, found)
        if found:
            w(f"minecraft/worldgen/feature/{fn}", {"type": "minecraft:no_op", "config": {}})
            report.append(f"feature {fn[:-5]}: {sorted(found)}")

    # 2) processor lists rewriting ore blocks inside structures
    strip_rules = [{
        "processor_type": "minecraft:rule",
        "rules": [{
            "input_predicate": {"predicate_type": "minecraft:block_match", "block": f"minecraft:{k}"},
            "location_predicate": {"predicate_type": "minecraft:always_true"},
            "output_state": f"minecraft:{v}",
        } for k, v in STRIP_TO.items()],
    }]
    w("last_ember/worldgen/processor_list/strip_ores.json", {"processors": strip_rules})
    # fossils: coal overlay (and its diamond variant) -> stone instead of ore
    for name in ("fossil_coal", "fossil_diamonds"):
        d = load(os.path.join(GEN, f"worldgen/processor_list/{name}.json"))
        d["processors"] = [p for p in d["processors"] if not (
            p.get("processor_type") == "minecraft:rule"
            and any("ore" in json.dumps(r["output_state"]) or "coal_ore" in json.dumps(r["input_predicate"]) for r in p["rules"]))]
        d["processors"].insert(1, {
            "processor_type": "minecraft:rule",
            "rules": [{"input_predicate": {"predicate_type": "minecraft:block_match", "block": "minecraft:coal_ore"},
                       "location_predicate": {"predicate_type": "minecraft:always_true"},
                       "output_state": "minecraft:stone"}]})
        w(f"minecraft/worldgen/processor_list/{name}.json", d)
        report.append(f"processor_list {name}: coal_ore -> stone")

    # 3) abandoned-camp template pool elements whose .nbt contain ore blocks
    ore_nbt = {
        "abandoned_camp/camp/forest/campsite_forest_4",
        "abandoned_camp/camp/windswept_forest/campsite_windswept_forest_2",
        "abandoned_camp/camp/windswept_forest/campsite_windswept_forest_3",
        "abandoned_camp/camp/windswept_forest/campsite_windswept_forest_4",
        "abandoned_camp/camp/wooded_badlands/campsite_wooded_badlands_3",
    }
    pdir = os.path.join(GEN, "worldgen/template_pool")
    for dp, _, fns in os.walk(pdir):
        for fn in fns:
            if not fn.endswith(".json"):
                continue
            d = load(os.path.join(dp, fn))
            changed = False
            for e in d.get("elements", []):
                el = e["element"]
                if el.get("location", "").removeprefix("minecraft:") in ore_nbt:
                    el["processors"] = "last_ember:strip_ores"
                    changed = True
                    report.append(f"template_pool element {el['location']}")
            if changed:
                rel = os.path.relpath(os.path.join(dp, fn), GEN)
                w(f"minecraft/{rel}", d)

    # 4) ore veins (large copper/iron veins, raw ore blocks, tuff/granite fillers) are material rules, not features:
    #    replace with a rule gated by a never-true condition (y >= 2031, above any world height).
    never = {"type": "minecraft:condition",
             "if_true": {"type": "minecraft:y_above", "add_stone_depth": False,
                         "anchor": {"absolute": 2031}, "surface_depth_multiplier": 0},
             "then_run": {"type": "minecraft:block", "result_state": "minecraft:stone"}}
    for v in ("copper_ore_vein", "iron_ore_vein"):
        w(f"minecraft/worldgen/material_rule/overworld/{v}.json", never)
        report.append(f"material_rule overworld/{v}: disabled")

    with open(MARK, "w") as f:
        f.write("\n".join(written) + "\n")
    print("\n".join(report))
    print(f"{len(written)} files written")

if __name__ == "__main__":
    main()
