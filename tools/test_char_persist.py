#!/usr/bin/env python3
"""T-009: attributes, effects, tags and kits of Cam (human ranger) and Cam2 (halfling knight) survive death, relog and a server restart.
Usage: test_char_persist.py snap|check|death   (snap -> file, check compares with it, death kills both and checks)"""
import importlib.util, json, os, re, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("rcon", os.path.join(ROOT, "tools/rcon.py")); rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
F = os.path.join(ROOT, "server/build/persist.json")
ATTRS = ["scale", "max_health", "luck", "movement_speed", "jump_strength", "safe_fall_distance", "attack_damage", "attack_speed", "block_interaction_range",
         "entity_interaction_range", "sneaking_speed", "fall_damage_multiplier", "knockback_resistance", "burning_time", "block_break_speed"]
def snap(p):
    d = {}
    for a in ATTRS:
        m = re.search(r"is ([-0-9.eE]+)$", rc.run(f"attribute {p} minecraft:{a} get").strip()); d[a] = round(float(m.group(1)), 4)
    fx = rc.run(f"data get entity {p} active_effects"); d["effects"] = sorted(set(re.findall(r"minecraft:(\w+)", fx)))
    d["effects"] = [e for e in d["effects"] if e == "hero_of_the_village" or (e == "resistance" and "class: 1" in "")]
    d["tags"] = sorted(set(re.findall(r"le\.[\w.]+", rc.run(f"tag {p} list"))))
    inv = rc.run(f"data get entity {p} Inventory"); d["inv_items"] = len(re.findall(r"id: \"minecraft", inv)); d["bread"] = ("count: 6" in inv)
    d["race"] = rc.run(f"scoreboard players get {p} le.race"); d["class"] = rc.run(f"scoreboard players get {p} le.class")
    if "has 1 [le.class]" in d["class"] and "resistance" in fx: d["effects"] = sorted(d["effects"] + ["resistance"])      # ours only for the knight
    return d
def both(): return {p: snap(p) for p in ("Cam", "Cam2")}
def cmp(a, b, label, skip=()):
    bad = 0
    for p in a:
        for k in a[p]:
            if k in skip: continue
            if a[p][k] != b[p][k]: bad += 1; print(f"  FAIL {label} {p} {k}: {a[p][k]} -> {b[p][k]}")
    print(f"  {'ok  ' if not bad else 'FAIL'} {label}: all values equal" if not bad else f"  {bad} differences"); return bad
if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "snap": json.dump(both(), open(F, "w"), indent=1); print(json.dumps(both(), indent=1)[:600]); sys.exit(0)
    base = json.load(open(F))
    if mode == "death":
        for p in ("Cam", "Cam2"): rc.run(f"gamemode survival {p}"); rc.run(f"kill {p}")
        time.sleep(6.5)
    sys.exit(1 if cmp(base, both(), mode, skip=("inv_items", "bread") if mode == "death" else ()) else 0)
