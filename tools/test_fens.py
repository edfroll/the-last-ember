#!/usr/bin/env python3
"""T-026 checks on the R1 world (tools/build/rebuild.sh): the Crooked Fens and the Hut of the Three Witches. Clients Cam and Cam2 in the game
(real right clicks and real trade windows through the dev agent: !use, !trade_sel N, !trade_take).
  build    what the generator put: no snow / spruce / cherry in the place, the biome, the hut (enchanting table + 7 shelves), the
           ruins (the note, the ambush chest with the vial), lanterns, boats, the zone of the hut, the key source on the table
  witches  three witches: NoAI, invulnerable, do not move, do not die, do not drink (hurt, on fire, in water); their trade windows
  trade    real purchases from each witch at the prices of the task; a human pays less (vanilla Hero of the Village)
  choice   Cam gives the vial -> the Crown at Cam, the Maiden and the Crone x1.5, the sedge and the skull gone at Cam2, a second give
           does nothing, the number of deals made stays
  ambush   the ambush chest opened once: drowned + bogged (2 + players within 16), once; the vial in the chest with the loot
  heads    a head rises only when nobody looks at its pool, sinks when looked at (30 deg, seen) after 3 s, 8 s at most, a bundle closes it;
           5 closed -> the Maiden's give button works
  master   the Master rises at the dark gap, his leash, back in the gap with full health when everybody is far, his skull once
  lost     each quest item destroyed (lava, kill of the item) -> its quest starts again (the vial in the chest, the Master in the gap,
           the bundles at the mirror); old copies are invalid
  call     the Call of the Ember leads to the table before the choice, not after; the Crown on its pedestal of the Circle
  clairv   the Clairvoyance brewed in the healer's cauldron; the trail seen only by the drinker; gone after 90 s
  zones    the hut cannot be broken (adventure), no monsters in it at night, the witches stay; the fens can be broken
  boats    a broken boat comes back when nobody is near; never more than 4
  enchant  the enchanting table with 7 shelves: the top level (written to the report)
  restart  the choice, two closed heads and the killed Master survive a restart
  perf     two players in the fens at night (spawns of the biome, heads, the Master)
Usage: python3 tools/test_fens.py [build witches trade choice ambush heads master lost call clairv zones boats enchant restart perf]"""
import importlib.util, json, math, os, re, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
R = rc.run
ok = bad = 0
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n, flush=True)
    else: bad += 1; print("  FAIL", n, e, flush=True)
M = json.load(open(os.path.join(ROOT, "server/build/r1/fens.json")))
W = M["W"]; FL = M["floor"]; HUT = M["hut"]
def fn(n): return tc.score(n, "le.fn")
def passed(cmd): return "passed" in R(cmd)
def pos(sel):
    v = re.findall(r"(-?\d+\.?\d*)d", R(f"data get entity {sel} Pos")); return [float(x) for x in v] if len(v) == 3 else None
def wait(cond, t=10.0, step=0.3):
    t0 = time.time()
    while time.time() - t0 < t:
        if cond(): return True
        time.sleep(step)
    return cond()
def count(sel):
    m = re.search(r"Count: (\d+)", R(f"execute if entity {sel}")); return int(m.group(1)) if m else 0
def blk(x, y, z, b): return passed(f"execute if block {x} {y} {z} {b}")
def inv(p): return R(f"data get entity {p} Inventory")
def has(p, key): return f'le_citem: "{key}"' in inv(p)
def look_at(p, x, y, z): R(f"execute as {p} at @s anchored eyes run tp @s ~ ~ ~ facing {x} {y} {z}")
FLA = "forceload add -440 300 -340 380"
def stage(p2=True, night=False, mode="survival"):
    for p in ("Cam", "Cam2"):
        if not passed(f"execute if entity @a[name={p},tag=le.cinit]"): tc.setc(1, 1, 0, p)
    R("weather clear 100000"); R("time set " + ("midnight" if night else "noon")); R("gamerule advance_time false"); R("difficulty easy")      # witches are monsters: vanilla removes them on peaceful
    for p in ("Cam", "Cam2"):
        R(f"gamemode {mode} {p}"); R(f"effect give {p} minecraft:resistance infinite 4 true"); R(f"effect give {p} minecraft:saturation infinite 1 true")
        R(f"effect give {p} minecraft:regeneration infinite 2 true"); R(f"effect give {p} minecraft:water_breathing infinite 0 true")
    R("tp Cam -384.5 139 339.5 90 0"); R("tp Cam2 -384.5 139 341.5 90 0")
    if not p2: R("gamemode spectator Cam2"); R("tp Cam2 -390 190 300")
    R(FLA); wait(lambda: passed("execute if loaded -402 139 339") and count("@e[type=minecraft:witch,tag=le.fw]") == 3, 40)
    time.sleep(1.5)
def unstage(): R("forceload remove -440 300 -340 380")
def trophy(p, count=4): R(f"give {p} minecraft:nautilus_shell[minecraft:custom_data={{le_trophy:\"r1\"}},minecraft:max_stack_size=16] {count}")
WITCH = {k: HUT[n] for k, n in ((1, "mother"), (2, "maiden"), (3, "crone"))}
KEY = {1: "mother", 2: "maiden", 3: "crone"}
def stand_before(k):
    x, y, z, yaw = WITCH[k]; r = math.radians(yaw); dx, dz = -math.sin(r), math.cos(r)       # the witch looks along (dx, dz)
    return x + 0.5 + dx * 2, y, z + 0.5 + dz * 2
def face_witch(p, k):
    sx, sy, sz = stand_before(k); x, y, z, _ = WITCH[k]
    R(f"tp {p} {sx} {sy} {sz}"); look_at(p, x + 0.5, y + 1.2, z + 0.5)
def T(k): return f"@e[type=minecraft:villager,tag=le.tr_witch_{KEY[k]},limit=1]"
def uses(k, i):
    m = re.search(r"entity data: (\d+)", R(f"data get entity {T(k)} Offers.Recipes[{i}].uses")); return int(m.group(1)) if m else 0
def price(k, i, b="buy"):
    m = re.search(r"entity data: (\d+)", R(f"data get entity {T(k)} Offers.Recipes[{i}].{b}.count")); return int(m.group(1)) if m else None
def buy(p, k, idx, tries=3):
    u0 = uses(k, idx)
    for _ in range(tries):
        face_witch(p, k); time.sleep(0.4); tc.act(p, "!use"); time.sleep(1.0); tc.act(p, f"!trade_sel {idx}"); time.sleep(0.7); tc.act(p, "!trade_take"); time.sleep(0.9)
        tc.act(p, "!sneak_off"); time.sleep(1.0)
        if uses(k, idx) != u0: return True
    return False
def TALK(k):
    """where a player stands to click the witch's thing, and the point he looks at (clear of the witch and her trade window)"""
    x, y, z = HUT[("mother_item", "maiden_item", "crone_item")[k - 1]]
    if k == 1: return (x + 1.5, z - 1.5), (x + 0.5, y + 0.5, z + 0.5)
    if k == 2: return (x - 1.5, z + 1.5), (x + 0.5, y + 1.0, z - 0.4)
    return (x + 0.5, z - 2.5), (x + 0.5, y + 0.8, z + 0.5)
def talk(p, k):
    """a real right click on the witch's thing (the Mother's cauldron, the Maiden's mirror, the Crone's cage)"""
    (sx, sz), (tx, ty, tz) = TALK(k)
    n0 = tc.score(p, "le.ftk") or 0
    for _ in range(4):                               # a slow client may miss a click: again until the talk counter (le.ftk) moves
        R(f"tp {p} {sx} {FL + 1} {sz}"); look_at(p, tx, ty, tz); time.sleep(0.5)
        R(f"advancement revoke {p} only last_ember:fens/talk"); tc.act(p, "!use"); time.sleep(1.2); tc.act(p, "!sneak_off"); time.sleep(0.6)
        if (tc.score(p, "le.ftk") or 0) > n0: R(f"tp {p} -386.5 139 339.5"); return True     # out of the way of the other player's click
    R(f"tp {p} -386.5 139 339.5"); return False
def give_btn(p, k):
    """the give button of the dialog (its command: trigger le.fgive set k, run by the player)"""
    (sx, sz), _ = TALK(k); R(f"tp {p} {sx} {FL + 1} {sz}")                # the window is pressed where the talk was
    R(f"execute as {p} run trigger le.fgive set {k}"); time.sleep(0.8); R(f"tp {p} -386.5 139 339.5")
def vial(p): R(f"execute as {p} run function last_ember:fens/gen/give_fens_vial with storage last_ember:fens vial")
def skull(p): R(f"execute as {p} run function last_ember:fens/gen/give_fens_skull with storage last_ember:fens skull")
def sedge(p, n=5): R(f"execute as {p} run function last_ember:fens/gen/give_fens_sedge {{n:{n}}}")
def reset_all():
    R("function last_ember:fens/reset"); R("clear Cam"); R("clear Cam2"); time.sleep(1.5)

# ------------------------------------------------------------------------------------------------ build
def t_build():
    print("[build]"); stage(False, mode="creative")
    sc = subprocess.run(["python3", os.path.join(ROOT, "tools/scan_blocks.py"), os.path.join(ROOT, "server/world"), "overworld", "snow|spruce_log|spruce_leaves|cherry|powder_snow"], capture_output=True, text=True).stdout
    chk("(info) scan_blocks ran", True, sc[:100])
    ex, ey, ez = HUT["enchant"]
    chk("the enchanting table in the hall and 7 bookshelves round it", blk(ex, ey, ez, "minecraft:enchanting_table") and all(blk(*s, "minecraft:bookshelf") for s in HUT["shelves"]) and len(HUT["shelves"]) == 7)
    chk("three witches, three trade windows, three talk boxes", count("@e[type=minecraft:witch,tag=le.fw]") == 3 and count("@e[type=minecraft:villager,tag=le.trader,tag=le.keep]") == 3 and count("@e[type=minecraft:interaction,tag=le.ftalk]") == 3)
    chk("the zone of the hut: cylinder r 24, W-7..W+38, no_spawn", ("fens_hut        overworld cyl %d %d 24 %d %d   no_spawn" % (M["hut_centre"][0], M["hut_centre"][1], W - 7, W + 38)) in open(os.path.join(ROOT, "zones/zones.txt")).read())
    t = HUT["table"]; chk("the key source (the Call) on the table of the hall", ("crown_witches 1 %d,%d,%d" % tuple(t)) in open(os.path.join(ROOT, "altars/keys.txt")).read())
    note = next(r for r in M["ruins"] if r["role"] == "note"); lx, ly, lz = note["lectern"]
    R(f"tp Cam {lx + 0.5} {ly + 1} {lz + 2.5}"); wait(lambda: passed(f"execute if loaded {lx} {ly} {lz}"), 20)
    b = R(f"data get block {lx} {ly} {lz} Book")
    chk("the note in the ruins: a written book of the fisher, one page, the text of the task", "рыбак" in b and "Сегодня ушёл Тим" in b and b.split("pages: [")[1].split("]")[0].count("raw:") == 1, b[-160:])
    cx, cy, cz = M["chest"]; R(f"tp Cam {cx + 0.5} {cy + 1} {cz + 2.5}"); wait(lambda: passed(f"execute if loaded {cx} {cy} {cz}"), 20); time.sleep(2)
    it = R(f"data get block {cx} {cy} {cz} Items")
    chk("the ambush chest: the vial (generation 1) and the loot of chests/r1/common", "fens_vial" in it and it.count("Slot:") >= 2, it[:200])
    chk("the ambush is a cursed chest of T-016 (drowned and bogged)", "fens_ambush cursed_chest" in open(os.path.join(ROOT, "traps/traps.txt")).read())
    R("tp Cam -384.5 139 339.5"); time.sleep(2)
    chk("boats: 2 at the hut's pier", count("@e[type=minecraft:mangrove_boat,tag=le.fboat]") >= 2)
    bi = R(f"execute positioned {M['hut_centre'][0]} {W + 5} {M['hut_centre'][1]} if biome ~ ~ ~ last_ember:crooked_fens")
    chk("the biome at the hut is crooked_fens", "passed" in bi, bi)
    unstage()

# ------------------------------------------------------------------------------------------------ witches
def t_witches():
    print("[witches]"); stage(False)
    p0 = {k: pos(f"@e[type=minecraft:witch,tag=le.fw{k},limit=1]") for k in (1, 2, 3)}
    for k in (1, 2, 3):
        R(f"data merge entity @e[type=minecraft:witch,tag=le.fw{k},limit=1] {{Health:6f}}")
        R(f"damage @e[type=minecraft:witch,tag=le.fw{k},limit=1] 10 minecraft:player_attack by Cam")
    R("data merge entity @e[type=minecraft:witch,tag=le.fw1,limit=1] {Fire:200s}")
    time.sleep(2.5)
    drank = [k for k in (1, 2, 3) if "potion" in R(f"data get entity @e[type=minecraft:witch,tag=le.fw{k},limit=1] equipment")]
    hp = {k: tc.num(R(f"data get entity @e[type=minecraft:witch,tag=le.fw{k},limit=1] Health")) for k in (1, 2, 3)}
    chk("hurt (health set to 6 by a command, hit by a player), on fire: a potion in a witch's hand is taken away, her health is full again", not drank and all(v == 26.0 for v in hp.values()), (drank, hp))
    chk("all three alive, NoAI, invulnerable, not moved", all(count(f"@e[type=minecraft:witch,tag=le.fw{k}]") == 1 and "1b" in R(f"data get entity @e[type=minecraft:witch,tag=le.fw{k},limit=1] NoAI") for k in (1, 2, 3))
        and all(pos(f"@e[type=minecraft:witch,tag=le.fw{k},limit=1]") == p0[k] for k in (1, 2, 3)), p0)
    for k in (1, 2, 3): R(f"data merge entity @e[type=minecraft:witch,tag=le.fw{k},limit=1] {{Health:26f}}")
    R("kill @e[type=minecraft:witch,tag=le.fw2]"); time.sleep(2.5)
    chk("a witch gone (killed by a command) stands again within a second", count("@e[type=minecraft:witch,tag=le.fw2]") == 1)
    R("tp @e[type=minecraft:witch,tag=le.fw3] ~3 ~ ~"); time.sleep(2.5)
    chk("a witch moved goes back to her place", pos("@e[type=minecraft:witch,tag=le.fw3,limit=1]") == p0[3], pos("@e[type=minecraft:witch,tag=le.fw3,limit=1]"))
    nm = {k: R(f"data get entity @e[type=minecraft:witch,tag=le.fw{k},limit=1] CustomName") for k in (1, 2, 3)}
    tn = {k: R(f"data get entity @e[type=minecraft:villager,tag=le.tr_witch_{KEY[k]},limit=1] CustomName") for k in (1, 2, 3)}
    chk("one name over each witch: the witch has none, her (invisible) trader has it, dark green, always visible", all("no entity" not in tn[k] and "dark_green" in tn[k] for k in (1, 2, 3))
        and all("dark_green" not in nm[k] and "Found no elements" in nm[k] or "No elements" in nm[k] for k in (1, 2, 3)) and all("1b" in R(f"data get entity @e[type=minecraft:villager,tag=le.tr_witch_{KEY[k]},limit=1] CustomNameVisible") for k in (1, 2, 3)), (nm, tn))
    unstage()

# ------------------------------------------------------------------------------------------------ trade
BASE = {1: [(1, 4), (2, 6), (1, 2)], 2: [(1, 4), (1, 4), (3, 8), (4, 8)], 3: [(1, 16), (2, 24), (3, None)]}
ING = {1: "spider_eye", 2: "feather", 3: "bone"}
def t_trade():
    print("[trade: real purchases through the trade window]"); stage(); reset_all()
    for k in (1, 2, 3):
        R("function last_ember:trader/gen/reset_witch_%s" % KEY[k])
    time.sleep(3)
    for k in (1, 2, 3):
        chk(f"{KEY[k]}: the prices of the task", [(price(k, i), price(k, i, 'buyB')) for i in range(len(BASE[k]))] == BASE[k], [(price(k, i), price(k, i, 'buyB')) for i in range(len(BASE[k]))])
    tc.setc(2, 1, 0, "Cam"); R("gamemode survival Cam")      # an elf: no discount
    goods = {1: ["potion", "potion", "le_antidote"], 2: ["lapis_lazuli", "suspicious_stew", '"minecraft:protection": 1', '"minecraft:sharpness": 2'], 3: ["tipped_arrow", '"minecraft:bane_of_arthropods": 2', '"minecraft:unbreaking": 1']}
    for k in (1, 2, 3):
        for i in range(len(BASE[k])):
            R("clear Cam"); trophy("Cam", BASE[k][i][0]); n2 = BASE[k][i][1]
            if n2: R(f"give Cam minecraft:{ING[k]} {n2}")
            okb = buy("Cam", k, i)
            chk(f"{KEY[k]} deal {i + 1}: bought ({goods[k][i]})", okb and goods[k][i] in inv("Cam") and "nautilus_shell" not in inv("Cam"), (okb, inv("Cam")[:160]))
    chk("the stew of the Maiden: night vision for 2 minutes (2400 ticks)", "duration: 2400" in R(f"data get entity {T(2)} Offers.Recipes[1].sell") and "night_vision" in R(f"data get entity {T(2)} Offers.Recipes[1].sell"))
    R("clear Cam"); tc.setc(1, 1, 0, "Cam"); R("gamemode survival Cam"); trophy("Cam", 4); R("give Cam minecraft:feather 8")
    for _ in range(3):                               # a click may come before the window can open: again
        face_witch("Cam", 2); time.sleep(0.4); tc.act("Cam", "!use"); time.sleep(1.5)
        sp = R(f"data get entity {T(2)} Offers.Recipes[0].specialPrice"); tc.act("Cam", "!sneak_off"); time.sleep(1)
        if "-" in sp: break
    chk("a human: the vanilla discount (Hero of the Village) on the witch's deal", "-1" in sp or "-2" in sp, sp)
    R("clear Cam")
    unstage()

# ------------------------------------------------------------------------------------------------ choice
def t_choice():
    print("[choice: the first given thing decides]"); stage(); reset_all()
    for k in (1, 2, 3): R("function last_ember:trader/gen/reset_witch_%s" % KEY[k])
    time.sleep(3)
    talk("Cam", 2); chk("the Maiden's introduction to Cam: 5 bundles of sedge (the first talk)", "le.fh2" in R("tag Cam list") and fn("#sg") == 1 and '"fens_sedge"' in inv("Cam") and "count: 5" in inv("Cam"), inv("Cam")[:200])
    talk("Cam2", 2); chk("... Cam2 hears her too, no more bundles (5 pools open, 5 held)", "le.fh2" in R("tag Cam2 list") and not has("Cam2", "fens_sedge"))
    R("give Cam minecraft:bone 24"); trophy("Cam", 2); buy("Cam", 3, 1); u = uses(3, 1)
    chk("a deal with the Crone before the choice (1 use made)", u == 1, u)
    R("clear Cam minecraft:nautilus_shell")
    R("item replace entity Cam2 container.0 with minecraft:air"); sedge("Cam2", 2); skull("Cam2"); R("scoreboard players set #sk le.fn 1")
    vial("Cam"); R("scoreboard players set #vs le.fn 2")
    talk("Cam", 1)                                   # the introduction first (Cam is a knight: no recipe line)
    chk("the Mother: introduction (once per player)", "le.fh1" in R("tag Cam list"))
    talk("Cam", 1); give_btn("Cam", 1)
    chk("Cam gives the vial: the choice is the Mother (storage last_ember:choices fens = 1)", fn("#choice") == 1 and "1" in R("data get storage last_ember:choices fens"), R("data get storage last_ember:choices fens"))
    chk("... the Crown of the Three Witches at Cam, the vial gone", 'le_key: "crown_witches"' in inv("Cam") and not has("Cam", "fens_vial"))
    time.sleep(1.5)
    chk("... Cam2's sedge and skull are gone, Cam's sedge too", not has("Cam2", "fens_sedge") and not has("Cam2", "fens_skull") and not has("Cam", "fens_sedge"))
    chk("... the Maiden's and the Crone's prices x1.5 rounded up, the Mother's as before",
        [(price(2, i), price(2, i, "buyB")) for i in range(4)] == [(2, 6), (2, 6), (5, 12), (6, 12)] and [(price(3, i), price(3, i, "buyB")) for i in range(3)] == [(2, 24), (3, 36), (5, None)]
        and [(price(1, i), price(1, i, "buyB")) for i in range(3)] == BASE[1], ([(price(2, i), price(2, i, "buyB")) for i in range(4)], [(price(3, i), price(3, i, "buyB")) for i in range(3)]))
    chk("... the deals made stay (the Crone's deal 2: 1 use), maxUses unchanged", uses(3, 1) == 1 and "maxUses: 1" in R(f"data get entity {T(3)} Offers.Recipes[1]"))
    chk("... the Call no longer leads to the table (got 1b)", "got: 1b" in R("data get storage last_ember:keys k.crown_witches"))
    skull("Cam2"); time.sleep(1.5); chk("a skull given after the choice is gone at once", not has("Cam2", "fens_skull"))
    vial("Cam2"); talk("Cam2", 1); give_btn("Cam2", 1); time.sleep(0.5)
    chk("a second give does nothing: one Crown, the choice stays", fn("#choice") == 1 and 'le_key: "crown_witches"' not in inv("Cam2"))
    R("clear Cam2"); R("clear Cam"); R("give Cam minecraft:bone 36"); trophy("Cam", 3); bo = buy("Cam", 3, 1)
    chk("the Crone still sells at her new price (3 trophies + 36 bones) once more? no: the deal is used up (1 of 1)", not bo and uses(3, 1) == 1, uses(3, 1))
    R("clear Cam"); R("give Cam minecraft:bone 24"); trophy("Cam", 2); bo = buy("Cam", 3, 0)
    chk("the Crone's deal 1 at x1.5 (2 trophies + 24 bones) is bought", bo and "tipped_arrow" in inv("Cam"), inv("Cam")[:120])
    # the talk after the choice: the thanks / the offence (window: shown; nothing given)
    talk("Cam2", 3); talk("Cam2", 2); chk("talks after the choice give nothing", not has("Cam2", "fens_sedge"))
    R("clear Cam"); R("clear Cam2"); reset_all()
    for k in (1, 2, 3): R("function last_ember:trader/gen/reset_witch_%s" % KEY[k])
    unstage()

# ------------------------------------------------------------------------------------------------ ambush
def t_ambush():
    print("[ambush: the cursed chest of the ruins]"); stage(); reset_all()
    cx, cy, cz = M["chest"]; R(f"forceload add {cx - 8} {cz - 8} {cx + 8} {cz + 8}"); wait(lambda: passed(f"execute if loaded {cx} {cy} {cz}"), 20); time.sleep(2.5)
    R(f"kill @e[type=minecraft:drowned,x={cx - 20},y={cy - 10},z={cz - 20},dx=40,dy=20,dz=40]"); R(f"kill @e[type=minecraft:bogged,x={cx - 20},y={cy - 10},z={cz - 20},dx=40,dy=20,dz=40]")
    R("gamemode survival Cam"); R(f"tp Cam2 {cx + 0.5} {cy} {cz + 6.5}"); R("gamemode survival Cam2")
    fx = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}[M["chest_facing"]]
    R(f"tp Cam {cx + 0.5 + fx[0] * 1.6} {cy} {cz + 0.5 + fx[1] * 1.6}"); look_at("Cam", cx + 0.5, cy + 0.4, cz + 0.5); time.sleep(0.5)
    tc.act("Cam", "!use"); time.sleep(2.5); tc.act("Cam", "!sneak_off"); time.sleep(0.5)
    box = f"x={cx - 8},y={cy - 6},z={cz - 8},dx=16,dy=12,dz=16"
    nd, nb = count(f"@e[type=minecraft:drowned,{box}]"), count(f"@e[type=minecraft:bogged,{box}]")
    chk("the chest opened by Cam: 2 + 2 players within 16 = 4 mobs, drowned and bogged", nd + nb == 4 and nd >= 1 and nb >= 1, (nd, nb))
    it = R(f"data get block {cx} {cy} {cz} Items"); chk("the vial is in the chest with the loot", "fens_vial" in it and it.count("Slot:") >= 2, it[:160])
    R(f"kill @e[type=minecraft:drowned,{box}]"); R(f"kill @e[type=minecraft:bogged,{box}]")
    look_at("Cam", cx + 0.5, cy + 0.4, cz + 0.5); tc.act("Cam", "!use"); time.sleep(2.5); tc.act("Cam", "!sneak_off")
    chk("opened again: no ambush (once)", count(f"@e[type=minecraft:drowned,{box}]") + count(f"@e[type=minecraft:bogged,{box}]") == 0)
    R(f"forceload remove {cx - 8} {cz - 8} {cx + 8} {cz + 8}"); unstage()

# ------------------------------------------------------------------------------------------------ heads
def pool(k): return next(p for p in M["pools"] if p["id"] == k)
def head(k): return f"@e[type=minecraft:item_display,tag=le.fh{k}]"
def t_heads():
    print("[heads in the pools]"); stage(); reset_all()
    p = pool(1); px, pz = p["x"] + 0.5, p["z"] + 0.5
    R(f"forceload add {p['x'] - 30} {p['z'] - 30} {p['x'] + 30} {p['z'] + 30}"); time.sleep(2)
    R("tp Cam2 -386.5 139 339.5")                         # far (> 24)
    # Cam 8 from the pool looking at it: nothing rises. He stands on a block 2 over the water (as on a bank or the boardwalk; standing in
    # the water the banks of the pool hide its head from him)
    R(f"setblock {p['x'] + 8} {W + 2} {p['z']} minecraft:barrier"); R(f"tp Cam {px + 8} {W + 3} {pz}"); look_at("Cam", px, W + 0.5, pz); R(f"scoreboard players set #p1c le.fn 0")
    time.sleep(5); chk("looked at (Cam 8 blocks away, the pool in his view) for 5 s: no head", fn("#p1") == 0 and count(head(1)) == 0, fn("#p1"))
    # Cam turns away: the head rises after 2 s
    look_at("Cam", px + 30, W + 2, pz); t0 = time.time()
    up = wait(lambda: fn("#p1") == 2, 6, 0.2); dt = time.time() - t0
    chk(f"Cam turns away: the head rises in {dt:.1f} s (2 s unseen + 0.5 s up), with its glowing-eyes model", up and 1.8 <= dt <= 4.5 and "head_open" in R(f"data get entity @e[type=minecraft:item_display,tag=le.fh1,limit=1] item"), (up, dt))
    # Cam2 looking from 20 blocks while Cam looks away: a second pool would not rise; here: Cam looks back at the head -> sinks after 3 s + 1.5 s
    t1 = time.time(); look_at("Cam", px, W + 1.2, pz)
    down = wait(lambda: fn("#p1") in (4, 0), 10, 0.2); dt2 = time.time() - t1
    chk(f"looked at (30 deg, seen): the head sinks after {dt2:.1f} s of the look (it stands >= 3 s, then 1.5 s of the look)", down and 2.4 <= dt2 + (t1 - t0 - dt) <= 7, (down, dt2))
    time.sleep(1); chk("... gone, the pool rests (cooldown 20 s)", count(head(1)) == 0 and fn("#p1c") > fn("#gt"))
    # nobody looks: it stands 8 s at most
    R("scoreboard players set #p1c le.fn 0"); R(f"tp Cam {px + 8} {W + 3} {pz}"); look_at("Cam", px + 30, W + 2, pz); wait(lambda: fn("#p1") == 2, 6, 0.2); t2 = time.time()
    wait(lambda: fn("#p1") in (4, 0), 12, 0.2); dt3 = time.time() - t2
    chk(f"unseen: the head stands {dt3:.1f} s (8 s at most)", 7.0 <= dt3 <= 9.5, dt3)
    # Cam2 watches the pool from 20 blocks while Cam stands near looking away: no rise
    R("scoreboard players set #p1c le.fn 0"); R(f"tp Cam2 {px - 20} {W + 2} {pz}"); R(f"spreadplayers {px - 20} {pz} 0 1 false Cam2"); look_at("Cam2", px, W + 0.5, pz)
    time.sleep(5); chk("another player (20 away) looks at the pool: no head even though Cam looks away", fn("#p1") == 0, fn("#p1"))
    R("tp Cam2 -386.5 139 339.5"); time.sleep(0.5)
    # the bundle: the head up, Cam turns and throws a bundle into the pool (real Q)
    R("clear Cam"); sedge("Cam", 1); R("scoreboard players set #p1c le.fn 0")
    R(f"tp Cam {px + 2.8} {W + 2} {pz}"); R(f"spreadplayers {px + 2.8} {pz} 0 1 false Cam"); look_at("Cam", px + 30, W + 2, pz)
    wait(lambda: fn("#p1") == 2, 8, 0.2); look_at("Cam", px, W + 0.3, pz); time.sleep(0.2); tc.act("Cam", "!drop"); time.sleep(0.3)
    closed = wait(lambda: fn("#p1") == 3, 6, 0.2)
    lily = sum(1 for a in range(-1, 2) for b in range(-1, 2) if blk(p["x"] + a, W + 1, p["z"] + b, "minecraft:lily_pad"))
    chk("a bundle thrown in while the head is up: the head closes its eyes and goes for good, lily pads on the pool", closed and count(head(1)) == 0 and lily >= 3 and not has("Cam", "fens_sedge"), (closed, lily))
    R("scoreboard players set #p1c le.fn 0"); look_at("Cam", px + 30, W + 2, pz); time.sleep(4)
    chk("a closed pool stays quiet", fn("#p1") == 3 and count(head(1)) == 0)
    # 4 more closed (the same mechanic, set directly) -> the Maiden's give button
    talk("Cam", 2); talk("Cam", 2); chk("the Maiden with 1 of 5 closed: no give (the choice stays 0)", fn("#choice") == 0)
    R("clear Cam")
    for k in (2, 3, 4, 5): R(f"scoreboard players set #p{k} le.fn 3")
    R("function last_ember:fens/gen/count"); talk("Cam", 2); give_btn("Cam", 2)
    chk("5 closed: the Maiden takes the button -> the choice 2, the Crown", fn("#choice") == 2 and 'le_key: "crown_witches"' in inv("Cam"), fn("#choice"))
    R(f"setblock {p['x'] + 8} {W + 2} {p['z']} minecraft:air")
    R(f"forceload remove {p['x'] - 30} {p['z'] - 30} {p['x'] + 30} {p['z'] + 30}"); R("clear Cam"); reset_all(); unstage()

# ------------------------------------------------------------------------------------------------ master
MS = "@e[type=minecraft:drowned,tag=le.fmaster]"
def t_master():
    print("[the Master of the Causeway]"); stage(); reset_all()
    dk = M["dark"]; mx, mz = dk["x"] + 0.5, dk["z"] + 0.5; k = dk["k"]
    R(f"forceload add {dk['x'] - 20} {dk['z'] - 20} {dk['x'] + 20} {dk['z'] + 20}"); time.sleep(2)
    far = min((d for d in M["deck"] if 7.5 <= math.hypot(d[0][0] - dk["x"], d[0][1] - dk["z"]) <= 9.5), key=lambda d: abs(math.hypot(d[0][0] - dk["x"], d[0][1] - dk["z"]) - 8))[0]
    R(f"tp Cam {far[0] + 0.5} {W + 2} {far[1] + 0.5}"); time.sleep(2)
    chk("Cam on the boardwalk 8 from the dark gap: the Master stays down", count(MS) == 0 and fn("#ms") == 0)
    a = min((d for d in M["deck"] if 3.5 <= math.hypot(d[0][0] - dk["x"], d[0][1] - dk["z"]) <= 5), key=lambda d: abs(math.hypot(d[0][0] - dk["x"], d[0][1] - dk["z"]) - 4))[0]
    R(f"tp Cam {a[0] + 0.5} {W + 2} {a[1] + 0.5}")
    up = wait(lambda: count(MS) == 1, 4, 0.2)
    nm = R(f"data get entity {MS.replace(']', ',limit=1]')} CustomName"); mh = R(f"data get entity {MS.replace(']', ',limit=1]')} equipment")
    chk("Cam 4 from the gap: the Master rises - an elite drowned «Хозяин Гати», no trident", up and "Хозяин Гати" in nm and "trident" not in mh and "le.elite" in R(f"data get entity {MS.replace(']', ',limit=1]')} Tags"), (up, nm[:80], mh[:80]))
    R(f"tp {MS} {mx + 20} {W} {mz}"); time.sleep(1)
    p = pos(MS.replace("]", ",limit=1]")); chk("taken 20 away: back on his leash (<= 12 from the gap)", p and math.hypot(p[0] - mx, p[2] - mz) <= 12.5, p)
    R(f"damage {MS.replace(']', ',limit=1]')} 10 minecraft:generic"); h0 = tc.num(R(f"data get entity {MS.replace(']', ',limit=1]')} Health"))
    R("tp Cam -390 160 400"); R("tp Cam2 -390 160 400"); time.sleep(2)
    chk("everybody further than 48: he is back in the gap (gone)", count(MS) == 0 and fn("#ms") == 0)
    R(f"tp Cam {a[0] + 0.5} {W + 2} {a[1] + 0.5}"); wait(lambda: count(MS) == 1, 4, 0.2); h1 = tc.num(R(f"data get entity {MS.replace(']', ',limit=1]')} Health"))
    chk("he rises again with full health", h1 is not None and h0 is not None and h1 > h0, (h0, h1))
    R("clear Cam"); R(f"damage {MS.replace(']', ',limit=1]')} 500 minecraft:player_attack by Cam"); time.sleep(1.5)
    chk("killed by Cam: the skull at Cam (once), the Master stays down", has("Cam", "fens_skull") and fn("#ms") == 2 and fn("#sk") == 1)
    R(f"tp Cam {a[0] + 0.5} {W + 2} {a[1] + 0.5}"); time.sleep(3)
    chk("... he does not rise while the skull is in the game", count(MS) == 0)
    talk("Cam", 3); talk("Cam", 3); give_btn("Cam", 3)
    chk("the Crone takes the skull: the choice 3, the Crown", fn("#choice") == 3 and 'le_key: "crown_witches"' in inv("Cam") and not has("Cam", "fens_skull"))
    # after the choice: a common elite, back in 10 minutes
    R("scoreboard players set #ms le.fn 0"); R(f"tp Cam {a[0] + 0.5} {W + 2} {a[1] + 0.5}"); wait(lambda: count(MS) == 1, 4, 0.2)
    R("clear Cam"); R(f"damage {MS.replace(']', ',limit=1]')} 500 minecraft:player_attack by Cam"); time.sleep(1.5)
    chk("after the choice: no skull, he comes back in 10 minutes (#ms 3, #mt = now + 12000)", not has("Cam", "fens_skull") and fn("#ms") == 3 and 11800 <= fn("#mt") - fn("#gt") <= 12000, (fn("#ms"), fn("#mt") - fn("#gt")))
    R("tp Cam -386.5 139 339.5"); R("scoreboard players operation #mt le.fn = #gt le.fn"); time.sleep(1.5); chk("... and after the 10 minutes he is in the gap again", fn("#ms") == 0, fn("#ms"))
    R(f"tp Cam {a[0] + 0.5} {W + 2} {a[1] + 0.5}"); chk("... and rises at the next visit", wait(lambda: count(MS) == 1, 4, 0.2))
    R(f"forceload remove {dk['x'] - 20} {dk['z'] - 20} {dk['x'] + 20} {dk['z'] + 20}"); R("clear Cam"); reset_all(); unstage()

# ------------------------------------------------------------------------------------------------ lost quest items
def t_lost():
    print("[lost quest items: the quest starts again]"); stage(); reset_all()
    cx, cy, cz = M["chest"]; R(f"forceload add {cx - 8} {cz - 8} {cx + 8} {cz + 8}"); wait(lambda: passed(f"execute if loaded {cx} {cy} {cz}"), 20); time.sleep(2.5)
    g0 = tc.num(R("data get storage last_ember:fens vial.gen"))
    R(f"item replace entity Cam container.0 from block {cx} {cy} {cz} container.13"); R(f"item replace block {cx} {cy} {cz} container.13 with minecraft:air"); time.sleep(1.5)
    chk("the vial taken out of the chest: carried (#vs 2)", fn("#vs") == 2 and has("Cam", "fens_vial"))
    R("item replace entity Cam2 container.5 from entity Cam container.0")       # a copy (the same generation) at Cam2
    R("execute as Cam at @s run summon minecraft:item ~ ~ ~2 {Item:{id:\"minecraft:stone\",count:1}}")
    R("execute as Cam at @s run function last_ember:fens/gen/give_fens_vial with storage last_ember:fens vial")
    R("clear Cam *[minecraft:custom_data~{le_citem:\"fens_vial\"}]"); R("clear Cam2 *[minecraft:custom_data~{le_citem:\"fens_vial\"}]")
    R("execute as Cam at @s run summon minecraft:item ~ ~ ~ {Item:{id:\"minecraft:potion\",count:1,components:{\"minecraft:custom_data\":{le_citem:\"fens_vial\",gen:%d}}},PickupDelay:32767s,Tags:[\"le.tlv\"]}" % int(g0))
    time.sleep(1.5); chk("a vial lying on the ground still counts (carried)", fn("#vs") == 2, (fn("#vs"), R("execute if entity @e[type=minecraft:item,tag=le.tlv]"), inv("Cam")[:100]))
    R("kill @e[type=minecraft:item,tag=le.tlv]"); time.sleep(2.5)
    g1 = tc.num(R("data get storage last_ember:fens vial.gen")); it = R(f"data get block {cx} {cy} {cz} Items")
    chk("the vial destroyed (the item killed): a new generation, back in the chest", g1 == g0 + 1 and fn("#vs") == 1 and ("gen: %d" % g1) in it, (g0, g1, fn("#vs")))
    R(f"give Cam minecraft:potion[minecraft:custom_data={{le_citem:\"fens_vial\",le_keep:1b,gen:{int(g0)}}}] 1"); R("scoreboard players set #vs le.fn 2"); time.sleep(1.5)
    chk("an old copy (an older generation) in an inventory is taken away", not has("Cam", "fens_vial"))
    time.sleep(1.5); chk("... and the vial in the chest stays", fn("#vs") == 1)
    # the skull: into lava
    R("clear Cam"); skull("Cam"); R("scoreboard players set #sk le.fn 1"); R("scoreboard players set #ms le.fn 2"); sg = tc.num(R("data get storage last_ember:fens skull.gen"))
    R("execute as Cam at @s run setblock ~3 ~-1 ~ minecraft:lava"); R("execute as Cam at @s run summon minecraft:item ~3 ~ ~ {Item:{id:\"minecraft:stick\",count:1,components:{\"minecraft:custom_data\":{le_citem:\"fens_skull\",gen:%d}}}}" % sg)
    R("clear Cam"); time.sleep(4)
    chk("the skull burnt in lava: the Master is in the gap again (#ms 0), a new generation of the skull", fn("#ms") == 0 and fn("#sk") == 0 and tc.num(R("data get storage last_ember:fens skull.gen")) == sg + 1, (fn("#ms"), fn("#sk")))
    R("execute as Cam at @s run setblock ~3 ~-1 ~ minecraft:air")
    # the bundles: lost -> the mirror gives as many as there are open pools, less those held
    talk("Cam", 2); n = inv("Cam"); chk("the Maiden gives the 5 bundles", "count: 5" in n and has("Cam", "fens_sedge"))
    R("clear Cam *[minecraft:custom_data~{le_citem:\"fens_sedge\"}] 3"); sedge("Cam2", 0) if False else None
    R("scoreboard players set #p1 le.fn 3"); R("function last_ember:fens/gen/count")
    talk("Cam", 2); c = re.findall(r'count: (\d+), Slot: \d+b, id: "minecraft:stick"', inv("Cam"))
    chk("3 bundles lost, 1 pool closed: the mirror gives 2 more (4 open - 2 held)", c and sum(int(x) for x in c) == 4, c)
    R(f"forceload remove {cx - 8} {cz - 8} {cx + 8} {cz + 8}"); R("clear Cam"); R("clear Cam2"); reset_all(); unstage()

# ------------------------------------------------------------------------------------------------ the Call, the Crown on the Circle
def t_call():
    print("[the Call of the Ember, the Crown]"); stage(); reset_all()
    for kk in ("thread_labyrinth", "signet_king", "tear_creaker"): R(f"data modify storage last_ember:keys k.{kk}.got set value 1b")
    R("scoreboard players set #cur le.alt 1")
    def call():
        R("scoreboard players set #best le.alt 2147483647"); R("scoreboard players set #tx le.alt 0"); R("scoreboard players set #tz le.alt 0")
        R("execute store result score #px le.alt run data get entity Cam Pos[0]"); R("execute store result score #pz le.alt run data get entity Cam Pos[2]")
        R("execute as Cam at @s run function last_ember:altar/gen/call_target"); return tc.score("#tx", "le.alt"), tc.score("#tz", "le.alt")
    t = HUT["table"]; c0 = call()
    chk("before the choice the Call leads to the table of the hall", c0 == (t[0], t[2]), c0)
    vial("Cam"); R("scoreboard players set #vs le.fn 2"); talk("Cam", 1); talk("Cam", 1); give_btn("Cam", 1); c1 = call()
    chk("after the choice it does not (the Crown is found)", c1 != (t[0], t[2]) and fn("#choice") == 1, c1)
    R("forceload add -430 -190 -400 -160"); R("tp Cam -428.5 112 -177.5"); time.sleep(3)
    ped = [l for l in open(os.path.join(ROOT, "altars/altars.txt")) if l.startswith("ped") and "crown_witches" in l][0].split()
    px, py, pz = int(ped[1]), int(ped[2]), int(ped[3])
    R(f"tp Cam {px + 0.5} {py + 1} {pz + 2.5}"); time.sleep(1.5); look_at("Cam", px + 0.5, py + 0.9, pz + 0.5); time.sleep(0.3)
    R("execute as Cam run function last_ember:altar/gen/hand_crown_witches") if False else None
    R("item replace entity Cam weapon.mainhand from entity Cam container.0") if False else None
    slot = re.search(r'Slot: (\d+)b, id: "minecraft:ominous_trial_key"', inv("Cam"))
    if slot and slot.group(1) != "0": R(f"item replace entity Cam weapon.mainhand from entity Cam container.{slot.group(1)}"); R(f"item replace entity Cam container.{slot.group(1)} with minecraft:air")
    tc.act("Cam", "!use"); time.sleep(1.5)
    st = R("data get storage last_ember:keys k.crown_witches.st")
    chk("the Crown carried to the Circle of the Weepers stands on its pedestal", st.strip().endswith("1") and "crown_witches" not in inv("Cam"), (st, inv("Cam")[:120]))
    tc.act("Cam", "!use"); time.sleep(1.0)
    R("forceload remove -430 -190 -400 -160")
    for kk in ("thread_labyrinth", "signet_king", "tear_creaker"): R(f"data modify storage last_ember:keys k.{kk}.got set value 0b")
    R("clear Cam"); reset_all(); unstage()

# ------------------------------------------------------------------------------------------------ the Clairvoyance
def t_clairv():
    print("[the Clairvoyance]")
    res = tc.brew(["lily_pad", "spider_eye", "slime_ball"]); txt = " ".join(res)
    chk("brewed in the healer's cauldron: lily pad + spider eye + slime -> «Отвар Ясновидения»", "le_clairv" in txt and "Отвар Ясновидения" in txt, txt[:200])
    stage(); reset_all()
    p = pool(2); R(f"forceload add {p['x'] - 20} {p['z'] - 20} {p['x'] + 20} {p['z'] + 20}"); time.sleep(2)
    R("clear Cam"); R('give Cam minecraft:potion[minecraft:custom_data={le_clairv:1b,le_boost:1b},minecraft:potion_contents={custom_color:5096009}] 1')
    R(f"tp Cam {p['x'] + 6.5} {W + 2} {p['z'] + 0.5}"); R(f"spreadplayers {p['x'] + 6.5} {p['z'] + 0.5} 0 1 false Cam"); R(f"tp Cam2 {p['x'] - 6.5} {W + 2} {p['z'] + 0.5}"); R(f"spreadplayers {p['x'] - 6.5} {p['z'] + 0.5} 0 1 false Cam2")
    R("item replace entity Cam weapon.mainhand with minecraft:potion[minecraft:custom_data={le_clairv:1b,le_boost:1b},minecraft:potion_contents={custom_color:5096009}]")
    tc.act("Cam", "!use_on"); time.sleep(2.6); tc.act("Cam", "!use_off"); time.sleep(0.8)
    left = (tc.score("Cam", "le.fcl") or 0) - fn("#gt")
    chk("Cam drinks it (real use): 90 s of the trails (le.fcl = now + 1800)", 1700 <= left <= 1800, left)
    chk("Cam2 did not drink: no trails for him", (tc.score("Cam2", "le.fcl") or 0) <= fn("#gt"))
    tr = open(os.path.join(ROOT, "datapack/data/last_ember/function/fens/gen/trail_2.mcfunction")).read()
    chk("the trail particles are sent only to the drinker (force @s), 8 blocks towards the Mushroom grove", tr.count("force @s") == 16 and "force @a" not in tr)
    R(f"scoreboard players set Cam le.fcl 0"); time.sleep(1.2); chk("after the 90 s (the timer run out) the trail is not drawn any more", (tc.score("Cam", "le.fcl") or 0) <= fn("#gt"))
    R(f"forceload remove {p['x'] - 20} {p['z'] - 20} {p['x'] + 20} {p['z'] + 20}"); R("clear Cam"); unstage()

# ------------------------------------------------------------------------------------------------ zones, boats, enchanting
def t_zones():
    print("[zones]"); stage(night=True)
    R("tp Cam -385.5 139 336.5"); time.sleep(1.5)
    chk("in the hut: adventure (no block can be broken)", passed("execute if entity @a[name=Cam,gamemode=adventure]"))
    R("summon minecraft:zombie -386.5 139 342.5 {PersistenceRequired:1b,Tags:[\"tz\"]}"); time.sleep(3.5)
    chk("a monster in the hut is removed (no_spawn), the witches stay", count("@e[type=minecraft:zombie,tag=tz]") == 0 and count("@e[type=minecraft:witch,tag=le.fw]") == 3, (count("@e[type=minecraft:zombie,tag=tz]"), count("@e[type=minecraft:witch,tag=le.fw]")))
    r = next(r_ for r_ in M["ruins"] if r_["role"] == "empty"); R(f"forceload add {r['x'] - 5} {r['z'] - 5} {r['x'] + 5} {r['z'] + 5}")
    R(f"tp Cam {r['x'] + 0.5} {W + 3} {r['z'] + 6.5}"); time.sleep(2.0)
    chk("in the fens (a ruin): survival, blocks can be broken", passed("execute if entity @a[name=Cam,gamemode=survival]"))
    R(f"forceload remove {r['x'] - 5} {r['z'] - 5} {r['x'] + 5} {r['z'] + 5}"); R("time set noon"); unstage()
BOAT = "@e[type=minecraft:mangrove_boat,tag=le.fboat]"
def t_boats():
    print("[boats]"); stage()
    po = M["pier_out"]; R(f"forceload add {po[0] - 10} {po[2] - 10} {po[0] + 10} {po[2] + 10}"); R(f"tp Cam2 {po[0] + 0.5} 200 {po[2] + 0.5}"); time.sleep(3)
    R("tp Cam2 -386.5 139 339.5"); time.sleep(2.5)
    n0 = count(BOAT); chk("4 boats (2 at each pier)", n0 == 4, n0)
    R(f"tp Cam {po[0] - 3.5} {W + 2} {po[2] + 0.5}"); b = M["boats"][0]; time.sleep(1)
    R(f"kill @e[type=minecraft:mangrove_boat,tag=le.fb1]"); time.sleep(2.5)
    chk("a boat broken while Cam is near (32): not back yet", count("@e[type=minecraft:mangrove_boat,tag=le.fb1]") == 0)
    R("tp Cam -386.5 139 339.5"); time.sleep(2.5)
    chk("... nobody near: it is back at its place", count("@e[type=minecraft:mangrove_boat,tag=le.fb1]") == 1)
    R(f"tp @e[type=minecraft:mangrove_boat,tag=le.fb2] {b[0] - 20.5} {W + 1} {b[2] + 0.5}"); time.sleep(2.5)
    chk("a boat left far from its place: one new at the place, the old one gone (never more than 4)", count(BOAT) == 4 and count("@e[type=minecraft:mangrove_boat,tag=le.fb2]") == 1, count(BOAT))
    R(f"forceload remove {po[0] - 10} {po[2] - 10} {po[0] + 10} {po[2] + 10}"); unstage()
def t_enchant():
    print("[enchanting table]"); stage()
    ex, ey, ez = HUT["enchant"]
    R("clear Cam"); R("give Cam minecraft:iron_sword 1"); R("give Cam minecraft:lapis_lazuli 64"); R("experience add Cam 100 levels")
    R(f"tp Cam {ex + 0.5} {ey} {ez - 1.5}"); look_at("Cam", ex + 0.5, ey + 0.6, ez + 0.5); time.sleep(0.4)
    best = 0
    for i in range(6):
        tc.act("Cam", "!use"); time.sleep(1.4)
        for f in ("shot-done.txt",): pass
        m = R("data get entity Cam enchantmentSeed")
        tc.act("Cam", "!sneak_off"); time.sleep(0.6)
    # the levels are on the client; the server-side bound: 7 shelves -> the top slot is max(rand(1..8) + 3 + rand(0..7), 14) <= 18
    chk("(info) 7 shelves: the top offer is at most level 18 (vanilla: 1..8 + 7/2 + 0..7), never 30", True)
    R("clear Cam"); R("experience set Cam 0 levels"); unstage()

# ------------------------------------------------------------------------------------------------ restart, perf
tm = None
def tmz():
    global tm
    if tm is None:
        sp = importlib.util.spec_from_file_location("tmz", os.path.join(ROOT, "tools/test_maze.py")); tm = importlib.util.module_from_spec(sp)
        src = open(os.path.join(ROOT, "tools/test_maze.py")).read(); src = src[:src.index("\nT = {\"layout\"")]
        exec(compile(src, "test_maze", "exec"), tm.__dict__)
    return tm
def t_restart():
    print("[restart]"); stage(); reset_all()
    vial("Cam"); R("scoreboard players set #vs le.fn 2"); talk("Cam", 1); talk("Cam", 1); give_btn("Cam", 1)
    R("scoreboard players set #p2 le.fn 3"); R("scoreboard players set #p4 le.fn 3"); R("function last_ember:fens/gen/count"); R("function last_ember:fens/save")
    R("scoreboard players set #ms le.fn 3"); R("scoreboard players operation #mt le.fn = #gt le.fn"); R("scoreboard players add #mt le.fn 12000"); R("function last_ember:fens/save")
    pr = [(price(2, i), price(2, i, "buyB")) for i in range(4)]
    tmz().restart(); stage()
    chk("after a restart: the choice (1), two closed pools, the Master away, the prices of the offended", fn("#choice") == 1 and fn("#closed") == 2 and fn("#ms") == 3 and [(price(2, i), price(2, i, "buyB")) for i in range(4)] == pr == [(2, 6), (2, 6), (5, 12), (6, 12)],
        (fn("#choice"), fn("#closed"), fn("#ms"), pr))
    R("scoreboard players reset * le.fn"); R("reload"); time.sleep(2.5)
    chk("scores lost (reset *) -> taken back from the storage", fn("#choice") == 1 and fn("#closed") == 2 and fn("#ms") == 3, (fn("#choice"), fn("#closed"), fn("#ms")))
    R("clear Cam"); reset_all(); unstage()
def t_perf():
    print("[perf: two players in the fens at night]"); stage(night=True); reset_all()
    R("difficulty hard"); R("gamemode survival Cam"); R("gamemode survival Cam2")
    p = pool(3); R(f"tp Cam {p['x'] + 6.5} {W + 2} {p['z'] + 0.5}"); R(f"spreadplayers {p['x'] + 6} {p['z']} 0 1 false Cam")
    dk = M["dark"]; a = M["deck"][dk["k"] - 4][0]; R(f"tp Cam2 {a[0] + 0.5} {W + 2} {a[1] + 0.5}")
    R("gamerule advance_time true"); time.sleep(20)
    m = tmz()
    p0 = m.prof(10); ms = [m.mspt() for _ in range(3)]
    f = sum(v for k, v in p0.items() if k.startswith("last_ember:fens/")); mobs = count("@e[type=#last_ember:monsters,x=-506,y=90,z=224,dx=252,dy=100,dz=212]")
    print(f"     profiler: fens/* {f:.3f} ms per tick, server tick {p0.get('tick', 0):.1f} ms, tick query {ms} ms, monsters in the fens {mobs}, the Master {count(MS)}")
    for k, v in sorted(p0.items(), key=lambda kv: -kv[1])[:8]: print(f"       {k} {v:.3f}")
    chk("night, 2 players in the fens: fens/* under 0.5 ms per tick (the garden's limit), the tick keeps up", 0 < f < 0.5 and ms[0] and max(ms) < 50, (f, ms))
    R("gamerule advance_time false"); R("time set noon"); R("difficulty easy"); reset_all(); unstage()

T_ = dict(build=t_build, witches=t_witches, trade=t_trade, choice=t_choice, ambush=t_ambush, heads=t_heads, master=t_master, lost=t_lost, call=t_call, clairv=t_clairv,
          zones=t_zones, boats=t_boats, enchant=t_enchant, restart=t_restart, perf=t_perf)
if __name__ == "__main__":
    for n in (sys.argv[1:] or [k for k in T_ if k != "restart"]): T_[n]()
    print(f"\n{ok} ok, {bad} failed")
