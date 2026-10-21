#!/usr/bin/env python3
"""T-009 checks (server running, the dev client Cam in the game): attributes of all peoples and classes, second wind, ashborn, arrows,
passages, kits. Usage: python3 tools/test_char.py [section...]   sections: attr wind ash arrows kits"""
import importlib.util, math, os, re, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("rcon", os.path.join(ROOT, "tools/rcon.py")); rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
ok = bad = 0
def check(name, cond, extra=""):
    global ok, bad
    if cond: ok += 1; print("  ok  ", name)
    else: bad += 1; print("  FAIL", name, extra)
def attr(p, a): return float(re.search(r"is ([-0-9.eE]+)$", rc.run(f"attribute {p} minecraft:{a} get").strip()).group(1))
def reset(p="Cam"):
    rc.run(f"execute as {p} run function last_ember:char/reset"); time.sleep(1.6); rc.run(f"gamemode survival {p}")
def setc(race, cls, p="Cam", tier=0):
    rc.run(f"clear {p}"); reset(p); rc.run(f"execute as {p} run function last_ember:char/set {{race:{race},class:{cls},tier:{tier}}}"); time.sleep(0.5)
def near(a, b, t=1e-3): return abs(a - b) <= t
RACE = {1: dict(scale=1.0, luck=1.0, max_health=20), 2: dict(scale=1.1, max_health=16, movement_speed=0.11, jump_strength=0.42 * 1.15, safe_fall_distance=6.0, attack_damage=0.0),
        3: dict(scale=0.8, max_health=24, attack_damage=2.0, block_break_speed=1.3, knockback_resistance=0.5, movement_speed=0.09, jump_strength=0.42 * 0.92, block_interaction_range=4.0, entity_interaction_range=2.5),
        4: dict(scale=0.65, max_health=14, sneaking_speed=0.45, fall_damage_multiplier=0.5, safe_fall_distance=9.0, luck=1.0, attack_damage=0.0, block_interaction_range=3.75, entity_interaction_range=2.25),
        5: dict(scale=1.0, max_health=22, burning_time=0.2)}
def t_attr():
    print("[attr]")
    for r, vals in RACE.items():
        setc(r, 3)
        for a, v in vals.items(): check(f"race {r} {a} = {v}", near(attr("Cam", a), v, 2e-3), attr("Cam", a))
    setc(1, 1); check("knight attack_speed 4.8", near(attr("Cam", "attack_speed"), 4.8)); check("knight entity_interaction_range 3.5", near(attr("Cam", "entity_interaction_range"), 3.5))
    check("knight resistance effect", "resistance" in rc.run("data get entity Cam active_effects"))
    setc(1, 3); check("human hero_of_the_village effect", "hero_of_the_village" in rc.run("data get entity Cam active_effects"))
    check("seer attack_speed unchanged", near(attr("Cam", "attack_speed"), 4.0))
def t_wind():
    print("[wind]")
    setc(1, 3); rc.run("effect clear Cam"); rc.run("effect give Cam minecraft:instant_health 1 10 true"); time.sleep(0.5)
    rc.run("damage Cam 15 minecraft:generic"); time.sleep(0.4)
    fx = rc.run("data get entity Cam active_effects"); check("second wind: regeneration + strength", "regeneration" in fx and "strength" in fx, fx)
    rc.run("effect clear Cam minecraft:regeneration"); rc.run("effect clear Cam minecraft:strength"); rc.run("effect give Cam minecraft:instant_health 1 10 true"); time.sleep(0.4)
    rc.run("damage Cam 15 minecraft:generic"); time.sleep(0.4)
    fx = rc.run("data get entity Cam active_effects"); check("second wind: cooldown (no second trigger)", "regeneration" not in fx, fx)
    sw = int(re.search(r"has (\d+)", rc.run("scoreboard players get Cam le.swcd")).group(1)); gt = int(re.search(r"is (\d+)", rc.run("time query gametime")).group(1))
    check("cooldown ~3 min", 3400 < sw - gt <= 3600, (sw, gt))
    rc.run("effect clear Cam minecraft:regeneration"); rc.run("scoreboard players set Cam le.swcd 0")
    setc(2, 3); rc.run("effect clear Cam"); rc.run("damage Cam 13 minecraft:generic"); time.sleep(0.4)
    check("elf: no second wind", "regeneration" not in rc.run("data get entity Cam active_effects"))
def t_ash():
    print("[ash]")
    setc(5, 3); rc.run("effect give Cam minecraft:wither 20 2"); time.sleep(0.3)
    check("ashborn: wither removed", "wither" not in rc.run("data get entity Cam active_effects"))
    setc(1, 3); rc.run("effect give Cam minecraft:wither 20 2"); time.sleep(0.3)
    check("human: wither stays", "wither" in rc.run("data get entity Cam active_effects")); rc.run("effect clear Cam")
    # time to death under water: a pool at (330,260,330)
    rc.run("forceload add 320 320 340 340"); time.sleep(3)
    rc.run("fill 325 259 325 329 275 329 minecraft:glass"); rc.run("fill 326 260 326 328 274 328 minecraft:water")
    def drown(race):
        setc(race, 3); rc.run("effect give Cam minecraft:instant_health 1 10 true"); rc.run("effect give Cam minecraft:saturation 60 1 true"); rc.run("effect give Cam minecraft:regeneration 1 0 true")
        rc.run("effect clear Cam"); rc.run("tp Cam 327.5 262 327.5"); t0 = time.time(); dead = None
        while time.time() - t0 < 80:
            time.sleep(0.1)
            r = rc.run("data get entity Cam Pos")          # death: the player respawns far away (the bonfire), the pool is at x 327
            m = re.search(r"\[([-0-9.]+)d", r)
            if m and float(m.group(1)) < 300: dead = time.time() - t0; break
        return dead
    th = drown(1); time.sleep(4); ta = drown(5); time.sleep(4)
    print("   time under water to death: human %.1fs ashborn %.1fs" % (th or -1, ta or -1))
    check("ashborn drowns clearly faster", th and ta and ta < th * 0.7, (th, ta))
    rc.run("tp Cam 0.5 57 -4.5")
def t_arrows():
    print("[arrows] see tools/test_char.py notes: range measured with owned arrows on a sky platform")
    U = rc.run("data get entity Cam UUID").split("[I;")[1].strip().rstrip("]")
    rc.run("forceload add 300 300 700 302"); time.sleep(4); rc.run("fill 300 250 300 700 250 302 minecraft:stone")
    def shoot(theta, owner=True, v=3.0):
        rc.run("kill @e[type=minecraft:arrow]"); vx, vy = v * math.cos(math.radians(theta)), v * math.sin(math.radians(theta))
        own = f"Owner:[I;{U}]," if owner else ""
        rc.run(f"summon minecraft:arrow 300.5 251.0 301.5 {{{own}Motion:[{vx}d,{vy}d,0.0d],pickup:0b}}"); t0 = time.time()
        while time.time() - t0 < 25:
            time.sleep(0.25)
            if rc.run("data get entity @e[type=minecraft:arrow,limit=1] inGround").strip().endswith("1b"): break
        pos = rc.run("data get entity @e[type=minecraft:arrow,limit=1] Pos"); dmg = rc.run("data get entity @e[type=minecraft:arrow,limit=1] damage")
        rc.run("kill @e[type=minecraft:arrow]"); return float(re.findall(r"\[([-0-9.]+)d", pos)[0]) - 300.5, float(re.findall(r": ([-0-9.]+)d", dmg)[0])
    setc(1, 1); base = shoot(25); mob = shoot(25, owner=False)
    setc(1, 2); rg = shoot(25)
    setc(2, 1); el = shoot(25)
    check("ranger range x2 (+-10%)", 1.8 <= rg[0] / base[0] <= 2.2, (base, rg)); check("ranger damage factor unchanged (2.0 * speed ratio kept)", near(rg[1] * 1.5, 2.0, 0.01), rg)
    check("elf damage x1.25", near(el[1], 2.5, 1e-3) and near(el[0], base[0], 0.5), el); check("mob/dispenser arrow untouched", near(mob[0], base[0], 0.5) and near(mob[1], 2.0), mob)
    print("   range human %.1f ranger %.1f (x%.2f), damage human %.2f ranger %.4f elf %.2f" % (base[0], rg[0], rg[0] / base[0], base[1], rg[1], el[1]))
def t_kits():
    print("[kits]")
    for cls, need in ((1, ["stone_sword", "bread", "torch", "wooden_pickaxe", "wooden_axe"]), (2, ["bow", "arrow", "goat_horn"]), (3, ["stick", "stone_sword", "written_book"]),
                      (4, ["cauldron", "stone_sword", "glass_bottle", "potion", "brown_mushroom", "sugar"])):
        setc(1, cls); inv = rc.run("data get entity Cam Inventory")
        for it in need: check(f"class {cls} has {it}", f"minecraft:{it}" in inv)
        check(f"class {cls} bread x6", "count: 6, Slot" in inv or re.search(r"count: 6[^}]*bread", inv) is not None)
        n = inv.count("{")
        rc.run(f"execute as Cam run function last_ember:char/set {{race:1,class:{cls},tier:0}}"); inv2 = rc.run("data get entity Cam Inventory")
        check(f"class {cls}: kit not given twice", inv2.count("{") == n)
        if cls == 3: check("seer: staff has le_keep", "le_staff" in inv and "le_keep" in inv)
    setc(1, 1); eq = rc.run("data get entity Cam equipment"); check("knight: chainmail chest + shield offhand", "chainmail_chestplate" in eq and "shield" in eq, eq)
SECT = {"attr": t_attr, "wind": t_wind, "ash": t_ash, "arrows": t_arrows, "kits": t_kits}
if __name__ == "__main__":
    for s in (sys.argv[1:] or list(SECT)): SECT[s]()
    print(f"\n{ok} ok, {bad} failed"); sys.exit(1 if bad else 0)
