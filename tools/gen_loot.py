#!/usr/bin/env python3
"""T-019: loot of the regions and the treasuries -> datapack (generated, do not edit):
  loot_table/chests/r<N>/common.json       common containers of a region (LootTable of a chest / barrel / pot)
  loot_table/item/*.json                   class items, grimoires, murky vials (the staffs: tools/gen_seer.py)
  loot_table/vault/*.json                  one table per treasury + filler / good pools of the regions
  advancement/vault/open_<id>.json         a player generated the loot of a treasury
  function/vault/gen/*.mcfunction          the layout of the main items at the start, the start staff, building, admin
Pools and numbers are the tables below (docs/tasks/T-019-treasuries-loot.md, docs/design/economy.md).
Treasuries: treasury/vaults.txt (+ extra files for tests: treasury/test_vaults.txt).
Usage: python3 tools/gen_loot.py [extra_vaults_file ...]"""
import json, os, re, shlex, shutil, sys, zlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, "datapack/data/last_ember")
LT = os.path.join(DP, "loot_table"); GEN = os.path.join(DP, "function/vault/gen"); ADV = os.path.join(DP, "advancement/vault")
for d in (os.path.join(LT, "vault"), GEN, ADV): shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True); json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
def w(name, lines): open(os.path.join(GEN, name + ".mcfunction"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
def tx(t, c="gray"): return {"text": t, "color": c, "italic": False}
def table(pools, typ="minecraft:chest"): return {"type": typ, "pools": pools}
def item(name, weight=None, quality=None, count=None, mods=(), cond=None):
    e = {"type": "minecraft:item", "name": name if ":" in name else "minecraft:" + name}
    if weight: e["weight"] = weight
    if quality: e["quality"] = quality
    m = []
    if count is not None:
        m.append({"type": "minecraft:set_count", "count": count if isinstance(count, int) else {"type": "minecraft:uniform", "min": count[0], "max": count[1]}})
    m += list(mods)
    if m: e["modifier"] = m[0] if len(m) == 1 else m
    if cond: e["condition"] = cond
    return e
def ref(tid, weight=None, quality=None):
    e = {"type": "minecraft:loot_table", "value": tid if ":" in tid else "last_ember:" + tid}
    if weight: e["weight"] = weight
    if quality: e["quality"] = quality
    return e
def comps(c): return {"type": "minecraft:set_components", "components": c}
def ench(d): return {"type": "minecraft:set_enchantments", "enchantments": {("minecraft:" + k): v for k, v in d.items()}}
def pool(entries, rolls=1, cond=None):
    p = {"rolls": rolls if isinstance(rolls, int) else {"type": "minecraft:uniform", "min": rolls[0], "max": rolls[1]}, "entries": entries}
    if cond: p["condition"] = cond
    return p
def score_is(holder, lo, hi=None):
    return {"type": "minecraft:int_value_check", "value": {"type": "minecraft:score", "target": {"type": "minecraft:fixed", "name": holder}, "score": "le.vt"},
            "range": {"min": lo, "max": lo if hi is None else hi}}

REGIONS = ["r0", "r1", "r2", "r3", "r4", "r5", "r6"]
ENCH_RU = {"protection": "Защита", "sharpness": "Острота", "unbreaking": "Прочность", "power": "Сила", "efficiency": "Эффективность", "projectile_protection": "Защита от снарядов",
           "respiration": "Подводное дыхание", "feather_falling": "Невесомость", "fire_protection": "Огнеупорность", "knockback": "Отбрасывание", "fortune": "Удача", "mending": "Починка",
           "blast_protection": "Взрывоустойчивость", "smite": "Небесная кара", "bane_of_arthropods": "Бич членистоногих", "punch": "Откидывание"}
# ================================================================== items
ITEM = os.path.join(LT, "item")
# murky vials (T-010): looks the same, the healer identifies it; good and bad effects
MURKY = [("weakness", 600, 0), ("poison", 300, 0), ("slowness", 600, 0), ("nausea", 300, 0), ("blindness", 200, 0), ("hunger", 600, 0),
         ("regeneration", 400, 0), ("speed", 1200, 0), ("strength", 900, 0), ("night_vision", 2400, 0), ("fire_resistance", 1800, 0), ("jump_boost", 1200, 0)]
dump(os.path.join(ITEM, "murky.json"), table([pool([item("potion", mods=[comps({
    "minecraft:custom_data": "{le_murky:1b}", "minecraft:custom_name": tx("Мутная склянка", "dark_gray"),
    "minecraft:potion_contents": {"custom_color": 5000268, "custom_effects": [{"id": "minecraft:" + e, "duration": d, "amplifier": a}]},
    "minecraft:tooltip_display": {"hidden_components": ["minecraft:potion_contents"]}})]) for e, d, a in MURKY])], "minecraft:generic"))
def grimoire(e, lvl):  # the same item as function last_ember:seer/grimoire (T-011)
    gd = '{le_grimoire:{ench:"minecraft:%s",lvl:%d}}' % (e, lvl)
    return item("book", mods=[comps({"minecraft:custom_name": tx("Гримуар", "light_purple"), "minecraft:lore": [tx("Письмена на неизвестном языке")],
        "minecraft:custom_data": gd, "minecraft:max_stack_size": 1,
        "minecraft:consumable": {"consume_seconds": 0.6, "animation": "none", "sound": "minecraft:item.book.page_turn", "has_consume_particles": False},
        "minecraft:use_remainder": {"id": "minecraft:enchanted_book", "count": 1, "components": {"minecraft:custom_data": gd.replace("le_grimoire", "le_grimoire_res", 1),
                                                                                                  "minecraft:stored_enchantments": {"minecraft:" + e: lvl}}}})])
def book(e, lvl, weight=None, quality=None): return item("book", weight, quality, mods=[ench({e: lvl})])
KEEP = lambda extra="": "{le_keep:1b%s}" % extra
MAIN_ITEMS = {  # main items of the treasuries (number = the score #m.<vault> le.vt); 1..5 the staffs (same numbers as seer/give_random), 99 = filler
 1: ("blink", "Посох Мгновения", None), 2: ("frost", "Посох Хладной Длани", None), 3: ("flame", "Посох Пламенной Жатвы", None), 4: ("lift", "Посох Отринутой Тяжести", None),
 5: ("banish", "Посох Изгнания", None), 6: ("wrath", "Гнев Мёртвого Неба", None),
 7: ("guard_shield", "Щит Стража", item("shield", mods=[ench({"unbreaking": 3}), comps({"minecraft:custom_data": KEEP(",le_guard:1b"), "minecraft:custom_name": tx("Щит Стража", "gold"),
      "minecraft:rarity": "epic", "minecraft:lore": [tx("Щит последнего стража Приюта."), tx("Рыцарь отражает им половину удара.", "dark_gray")]})])),
 8: ("watch_plate", "Латы Последнего Дозора", item("iron_chestplate", mods=[comps({"minecraft:custom_data": KEEP(",le_watch:1b"), "minecraft:custom_name": tx("Латы Последнего Дозора", "gold"),
      "minecraft:rarity": "epic", "minecraft:lore": [tx("Дозор стоял до конца. Латы — до сих пор.")],
      "minecraft:attribute_modifiers": [{"type": "minecraft:armor", "id": "last_ember:watch_armor", "amount": 8, "operation": "add_value", "slot": "chest"},
                                        {"type": "minecraft:armor_toughness", "id": "last_ember:watch_toughness", "amount": 1, "operation": "add_value", "slot": "chest"},
                                        {"type": "minecraft:knockback_resistance", "id": "last_ember:watch_kb", "amount": 0.1, "operation": "add_value", "slot": "chest"}]})])),
 9: ("wind_bow", "Лук Дальнего Ветра", item("bow", mods=[ench({"power": 3, "infinity": 1}), comps({"minecraft:custom_data": KEEP(",le_windbow:1b"), "minecraft:custom_name": tx("Лук Дальнего Ветра", "gold"),
      "minecraft:rarity": "epic", "minecraft:lore": [tx("Тетива поёт, как ветер над перевалом.")]})])),
 10: ("shadow_quiver", "Колчан Теней", item("tipped_arrow", count=16, mods=[comps({"minecraft:custom_data": KEEP(",le_shadow:1b"), "minecraft:custom_name": tx("Стрела Теней", "dark_purple"),
      "minecraft:potion_contents": {"custom_color": 3484199, "custom_effects": [{"id": "minecraft:wither", "duration": 800, "amplifier": 1}]},
      "minecraft:lore": [tx("Из Колчана Теней. Иссушает того, в кого попала.")]})])),
 11: ("old_cauldron", "Котёл Старой Знахарки", item("cauldron", mods=[comps({"minecraft:custom_data": KEEP(",le_cauldron:1b,le_old:1b"), "minecraft:custom_name": tx("Котёл Старой Знахарки", "gold"),
      "minecraft:rarity": "epic", "minecraft:lore": [tx("Котёл знахаря: Shift+ПКМ по горящему очагу."), tx("Варит на одну склянку больше.", "dark_gray")]})])),
 12: ("herb_bag", "Сумка Травницы", item("bundle", mods=[comps({"minecraft:custom_data": KEEP(",le_herbbag:1b"), "minecraft:custom_name": tx("Сумка Травницы", "gold"),
      "minecraft:rarity": "epic", "minecraft:lore": [tx("Травница собирала это всю жизнь.")],
      "minecraft:bundle_contents": [{"id": "minecraft:rabbit_foot", "count": 2}, {"id": "minecraft:glow_berries", "count": 8}, {"id": "minecraft:honey_bottle", "count": 2},
                                    {"id": "minecraft:slime_ball", "count": 4}, {"id": "minecraft:spider_eye", "count": 4}, {"id": "minecraft:cobweb", "count": 4}]})])),
 13: ("template", "Шаблон незеритового улучшения", item("netherite_upgrade_smithing_template")),
}
NUM = {v[0]: k for k, v in MAIN_ITEMS.items()}
STAFFS = [1, 2, 3, 4, 5]
for k, (mid, name, it) in MAIN_ITEMS.items():
    if it: dump(os.path.join(ITEM, mid + ".json"), table([pool([it])], "minecraft:generic"))
# ---------------------------------------------------------------- the rules of the layout (economy.md): main -> regions
SINGLE = [(13, ["r6"], False), (6, ["r5", "r6"], True)]       # (main, regions, prefer the danger vaults)
PAIRS = [((7, 8), ("r2", "r4")), ((11, 12), ("r2", "r4")), ((9, 10), ("r3", "r5"))]
STAFF_REGIONS = ["r1", "r2", "r3", "r4", "r5"]
# ================================================================== common containers: 2..4 things of the region pool
FOOD = {"r0": ["bread", "apple", "cooked_mutton"], "r1": ["bread", "apple", "cooked_porkchop", "cooked_chicken", "carrot"], "r2": ["bread", "cooked_mutton", "cooked_salmon", "apple"],
        "r3": ["cooked_cod", "cooked_mutton", "bread", "dried_kelp"], "r4": ["bread", "cooked_rabbit", "dried_kelp", "melon_slice"], "r5": ["bread", "cooked_beef", "mushroom_stew"],
        "r6": ["bread", "cooked_porkchop", "rotten_flesh"]}
BOOK1 = {"r0": [], "r1": ["protection", "sharpness", "unbreaking", "power", "efficiency"], "r2": ["protection", "sharpness", "power", "projectile_protection", "respiration"],
         "r3": ["feather_falling", "unbreaking", "protection"], "r4": ["fire_protection", "power", "sharpness", "knockback"], "r5": ["efficiency", "fortune", "unbreaking", "protection"],
         "r6": ["fire_protection", "blast_protection", "power", "sharpness"]}
def common(r):
    n = int(r[1]); e = []
    for f in FOOD[r]: e.append(item(f, 10 // len(FOOD[r]) * 2 + 2, count=(1, 3)))
    e += [item("arrow", 8, count=(4, 8)), item("soul_torch" if r == "r6" else "torch", 8, count=(2, 6)), item("bone", 6, count=(1, 3)), item("string", 6, count=(1, 3)),
          item("leather", 5, count=(1, 2)), ref("item/murky", 4, 1)]
    # ingredients of the healer's cauldron (T-010)
    e += [item("brown_mushroom", 3, count=(1, 2)), item("red_mushroom", 2, count=(1, 2)), item("sugar", 3, count=(1, 3)), item("glow_berries", 3, count=(1, 3)),
          item("spider_eye", 3, count=(1, 2)), item("gunpowder", 2, count=(1, 2)), item("cobweb", 2, count=(1, 2)), item("slime_ball", 1, 2), item("rabbit_foot", 1, 2)]
    if r == "r1": e.append(item("honey_bottle", 3, count=(1, 2)))
    if n >= 2: e.append(item("iron_ingot", 2, 2, count=(1, 3)))
    for b in BOOK1[r]: e.append(book(b, 1, 1, 1))
    return table([pool(e, (2, 4))])
for r in REGIONS: dump(os.path.join(LT, "chests", r, "common.json"), common(r))
# ================================================================== treasury pools
BOOKS = {"r1": [("protection", 2), ("sharpness", 2), ("power", 2), ("efficiency", 2), ("unbreaking", 2)],
         "r2": [("protection", 3), ("sharpness", 2), ("power", 2), ("projectile_protection", 3), ("respiration", 2)],
         "r3": [("feather_falling", 3), ("unbreaking", 2), ("protection", 3), ("sharpness", 3)],
         "r4": [("power", 3), ("protection", 3), ("fire_protection", 3), ("sharpness", 3), ("knockback", 2)],
         "r5": [("fortune", 2), ("efficiency", 3), ("sharpness", 3), ("protection", 3), ("unbreaking", 3)],
         "r6": [("fire_protection", 4), ("protection", 4), ("power", 4), ("sharpness", 4), ("feather_falling", 4)]}
FILLER_BOOK = {"r1": ("protection", 3), "r2": ("sharpness", 3), "r3": ("feather_falling", 4), "r4": ("power", 4), "r5": ("efficiency", 4), "r6": ("protection", 4)}
GRIMOIRES = {"r2": [("sharpness", 3), ("protection", 3)], "r3": [("feather_falling", 4), ("unbreaking", 3)], "r4": [("power", 4), ("knockback", 2)],
             "r5": [("fortune", 3), ("efficiency", 4)], "r6": [("fire_protection", 4)]}
INGOTS = {"r1": ["iron_ingot"], "r2": ["iron_ingot"], "r3": ["iron_ingot"], "r4": ["iron_ingot", "gold_ingot"], "r5": ["iron_ingot", "gold_ingot"], "r6": ["gold_ingot", "iron_ingot"]}
POTIONS = {"r1": ["healing", "regeneration"], "r2": ["healing", "water_breathing", "strength"], "r3": ["healing", "regeneration", "strength"],
           "r4": ["fire_resistance", "healing", "strength"], "r5": ["night_vision", "healing", "regeneration"], "r6": ["fire_resistance", "strong_healing", "strength"]}
def potion(p, weight): return item("potion", weight, mods=[{"type": "minecraft:set_potion", "id": "minecraft:" + p}])
for r in BOOKS:
    good = [book(e, l, 3) for e, l in BOOKS[r]] + [item(i, 6 // len(INGOTS[r]), 1, count=(4, 8)) for i in INGOTS[r]] + [potion(p, 2) for p in POTIONS[r]]
    pools = [pool(good, (2, 3) if r in GRIMOIRES else (3, 5))]
    if r in GRIMOIRES: pools.append(pool([grimoire(e, l) for e, l in GRIMOIRES[r]], (1, 2)))
    dump(os.path.join(LT, "vault", f"good_{r}.json"), table(pools))
    e, l = FILLER_BOOK[r]
    dump(os.path.join(LT, "vault", f"filler_{r}.json"), table([pool([book(e, l)]), pool([item(INGOTS[r][0], count=(8, 16))])]))
dump(os.path.join(ITEM, "grimoire_mending.json"), table([pool([grimoire("mending", 1)])], "minecraft:generic"))
# ================================================================== the treasuries
FILES = [os.path.join(ROOT, "treasury/vaults.txt")] + [os.path.abspath(a) for a in sys.argv[1:]]
V = []
for fn in FILES:
    for ln, line in enumerate(open(fn, encoding="utf-8"), 1):
        line = line.split("#", 1)[0].strip() if not line.lstrip().startswith("#") else ""
        if not line: continue
        p = shlex.split(line)
        assert p[0] == "vault" and len(p) >= 7, f"{fn}:{ln}: vault <id> <region> <dim> <x> <y> <z> [...]"
        v = {"id": p[1], "r": p[2], "dim": p[3], "x": int(p[4]), "y": int(p[5]), "z": int(p[6]), "block": "minecraft:chest[facing=north]", "danger": False, "main": None, "clue": None, "hint": None, "build": True}
        assert re.fullmatch(r"[a-z0-9_]+", v["id"]) and v["r"] in BOOKS, f"{fn}:{ln}: id [a-z0-9_], region r1..r6"
        for a in p[7:]:
            if a == "danger": v["danger"] = True
            elif "=" in a:
                k, val = a.split("=", 1)
                if k == "block": v["block"] = val if ":" in val else "minecraft:" + val
                elif k in ("main", "clue", "hint"): v[k] = val
                elif k == "build": v["build"] = val != "0"
                else: raise SystemExit(f"{fn}:{ln}: unknown key {k}")
            else: raise SystemExit(f"{fn}:{ln}: unknown flag {a}")
        V.append(v)
ids = [v["id"] for v in V]; assert len(ids) == len(set(ids)), "duplicate vault ids"
BYID = {v["id"]: v for v in V}
for v in V:
    if v["clue"]: assert v["clue"] in BYID and BYID[v["clue"]]["hint"], f"clue={v['clue']}: no such vault or it has no hint"
FIXED = {}  # vault -> main number (known main) or loot table id (a biome reward of the region task)
for v in V:
    if v["main"]: FIXED[v["id"]] = NUM.get(v["main"], v["main"] if ":" in v["main"] else "last_ember:" + v["main"])
FIXED_NUMS = {m for m in FIXED.values() if isinstance(m, int)}
def H(kind, vid): return f"#{kind}.{vid}"  # score holders in le.vt: m main, m2 second main, o opened, a golden apple, e Mending, b built
REG = {r: [v for v in V if v["r"] == r] for r in BOOKS}
warn = []
for k, regs, _ in SINGLE:
    if k not in FIXED_NUMS and not any(REG[r] for r in regs): warn.append(f"{MAIN_ITEMS[k][1]}: no treasury in {'/'.join(regs)}")
for (a, b), regs in PAIRS:
    for r in regs:
        if not REG[r]: warn.append(f"{MAIN_ITEMS[a][1]} / {MAIN_ITEMS[b][1]}: no treasury in {r}")
for r in BOOKS:
    need = sum(1 for k, regs, _ in SINGLE if regs == [r]) + sum(1 for _, regs in PAIRS if r in regs) + (1 if r in STAFF_REGIONS else 0)
    free = sum(1 for v in REG[r] if v["id"] not in FIXED)
    if REG[r] and free < need: warn.append(f"{r}: {need} main items for {free} free treasuries (some go second)")
# ---------------------------------------------------------------- one loot table per treasury: the main item is chosen by the scores of the layout at the moment of opening
for v in V:
    vid, r = v["id"], v["r"]; pools = []
    if vid in FIXED and not isinstance(FIXED[vid], int): pools.append(pool([ref(FIXED[vid])]))
    for slot in ("m", "m2"):
        for k, (mid, name, it) in MAIN_ITEMS.items():
            src = f"item/staff_{mid}" if k <= 6 else f"item/{mid}"
            pools.append(pool([ref(src)], cond=score_is(H(slot, vid), k)))
    pools.append(pool([ref(f"vault/filler_{r}")], cond=score_is(H("m", vid), 99)))
    pools.append(pool([ref(f"vault/good_{r}")]))
    pools.append(pool([item("golden_apple")], cond=score_is(H("a", vid), 1)))
    if r == "r6": pools.append(pool([ref("item/grimoire_mending")], cond=score_is(H("e", vid), 1)))
    if v["clue"]:
        lines = BYID[v["clue"]]["hint"].split("|")
        pools.append(pool([item("paper", mods=[comps({"minecraft:custom_name": tx("Обрывок карты", "yellow"), "minecraft:lore": [tx(l) for l in lines],
                                                      "minecraft:custom_data": '{le_clue:"%s"}' % v["clue"], "minecraft:max_stack_size": 1})])]))
    tab = table(pools); tab["random_sequence"] = f"last_ember:vault/{vid}"
    dump(os.path.join(LT, "vault", f"{vid}.json"), tab)
    dump(os.path.join(ADV, f"open_{vid}.json"), {"criteria": {"o": {"trigger": "minecraft:player_generates_container_loot", "conditions": {"loot_tables": f"last_ember:vault/{vid}"}}},
                                                 "rewards": {"function": f"last_ember:vault/gen/opened_{vid}"}})
    o = [f"# a player generated the loot of the treasury {vid}: it is open, its main items are taken", f"advancement revoke @s only last_ember:vault/open_{vid}",
         f"scoreboard players set {H('o', vid)} le.vt 1"]
    for s in STAFFS:
        for slot in ("m", "m2"): o.append(f"execute if score {H(slot, vid)} le.vt matches {s} run scoreboard players set #st.{s} le.vt 1")
    w(f"opened_{vid}", o)
    dim = v["dim"] if ":" in v["dim"] else "minecraft:" + v["dim"]
    w(f"build_{vid}", [f"# the container of the treasury {vid} with its loot table (the loot is made when a player opens it)",
                       f'execute in {dim} run setblock {v["x"]} {v["y"]} {v["z"]} {v["block"]}{{LootTable:"last_ember:vault/{vid}"}} replace',
                       f"scoreboard players set {H('b', vid)} le.vt 1"])
    w(f"refill_{vid}", [f"# TEST/ADMIN: the treasury {vid} again closed and full (its main items by the current layout; a taken staff can repeat)",
                        f"execute in {dim} run setblock {v['x']} {v['y']} {v['z']} minecraft:air replace", f"function last_ember:vault/gen/build_{vid}",
                        f"scoreboard players set {H('o', vid)} le.vt 0", f"advancement revoke @a only last_ember:vault/open_{vid}"])
w("pending", ["# every second: build the containers of the treasuries whose chunk is loaded (once)"] +
  [f"execute unless score {H('b', v['id'])} le.vt matches 1 in {v['dim'] if ':' in v['dim'] else 'minecraft:' + v['dim']} if loaded {v['x']} {v['y']} {v['z']} run function last_ember:vault/gen/build_{v['id']}"
   for v in V if v["build"]])
# ---------------------------------------------------------------- choosing at random: a generated function per candidate list
CH = [0]
def chooser(cands, cond, assign, comment):
    """cands: list of keys; cond(key) -> 'execute' sub-conditions; assign(key) -> command. Returns the function id; it returns 1 when one was chosen, 0 when none fits."""
    CH[0] += 1; name = f"ch_{CH[0]}"
    L = [f"# {comment}: one at random of those that fit; return 0 when none", "scoreboard players set #n le.vt 0"]
    L += [f"execute {cond(c)} run scoreboard players add #n le.vt 1" for c in cands]
    L += ["execute if score #n le.vt matches 0 run return 0", "execute store result score #r le.vt run random value 0..9999", "scoreboard players operation #r le.vt %= #n le.vt"]
    for c in cands:
        L.append(f"execute {cond(c)} run scoreboard players remove #r le.vt 1")
        L.append(f"execute if score #r le.vt matches -1 {cond(c)} run return run {assign(c)}")
    L.append("return 0")
    w(name, L); return f"last_ember:vault/gen/{name}"
FREE = lambda vid: f"unless score {H('o', vid)} le.vt matches 1 if score {H('m', vid)} le.vt matches 0"
PUTS = {}
def put_fn(regs, danger):
    """function: put the main #k le.vt into a treasury of regs (danger ones first, then any free, then as the second main)"""
    key = ("_".join(regs), danger)
    if key in PUTS: return PUTS[key]
    vs = [v["id"] for r in regs for v in REG[r] if v["id"] not in FIXED]
    setm = lambda slot: (lambda vid: f"scoreboard players operation {H(slot, vid)} le.vt = #k le.vt")
    L = [f"# put the main item #k le.vt into a treasury of {', '.join(regs)}"]
    if danger:
        dv = [x for x in vs if BYID[x]["danger"]]
        if dv: L.append(f"execute if function {chooser(dv, FREE, setm('m'), 'a free danger treasury')} run return 1")
    if vs:
        L.append(f"execute if function {chooser(vs, FREE, setm('m'), 'a free treasury')} run return 1")
        L.append(f"execute if function {chooser(vs, lambda x: f'unless score {H(chr(111), x)} le.vt matches 1 if score {H(chr(109) + chr(50), x)} le.vt matches 0', setm('m2'), 'the second main slot')} run return 1")
    L += ['tellraw @a[tag=le.vdbg] {"text":"VAULT WARNING: no place for a main item","color":"red"}', "return 0"]
    PUTS[key] = f"last_ember:vault/gen/put_{len(PUTS) + 1}"; w(f"put_{len(PUTS)}", L); return PUTS[key]
def place(k, regs, danger=False):
    return [f"scoreboard players set #k le.vt {k}", f"execute unless score #u.{k} le.vt matches 1 run function {put_fn(regs, danger)}"]
# ---------------------------------------------------------------- the layout
L = ["# the layout of the main items over the treasuries (at the first start, after a change of the treasury list, vault/relayout); opened treasuries keep theirs",
     "# 1. not opened treasuries: empty"]
for v in V:
    for kind in ("m", "m2", "a", "e"): L.append(f"execute unless score {H('o', v['id'])} le.vt matches 1 run scoreboard players set {H(kind, v['id'])} le.vt 0")
L.append("# 2. what is already taken (opened treasuries, the start staffs, fixed by a region task) is not laid out again")
for k in MAIN_ITEMS: L.append(f"scoreboard players set #u.{k} le.vt {1 if k in FIXED_NUMS else 0}")
for v in V:
    for slot in ("m", "m2"):
        for k in MAIN_ITEMS: L.append(f"execute if score {H('o', v['id'])} le.vt matches 1 if score {H(slot, v['id'])} le.vt matches {k} run scoreboard players set #u.{k} le.vt 1")
for s in STAFFS: L.append(f"execute if score #st.{s} le.vt matches 1 run scoreboard players set #u.{s} le.vt 1")
L.append("# 3. fixed main items of the region tasks")
for vid, m in FIXED.items(): L.append(f"execute unless score {H('o', vid)} le.vt matches 1 run scoreboard players set {H('m', vid)} le.vt {m if isinstance(m, int) else 98}")
L.append("# 4. single items, pairs, the staffs over the regions")
for k, regs, dg in SINGLE: L += place(k, regs, dg)
for (a, b), (r1, r2) in PAIRS:
    one = f"pair_{a}_{b}_0"; two = f"pair_{a}_{b}_1"
    w(one, [f"# {MAIN_ITEMS[a][1]} -> {r1}, {MAIN_ITEMS[b][1]} -> {r2}"] + place(a, [r1]) + place(b, [r2]))
    w(two, [f"# {MAIN_ITEMS[a][1]} -> {r2}, {MAIN_ITEMS[b][1]} -> {r1}"] + place(a, [r2]) + place(b, [r1]))
    L += ["execute store result score #c le.vt run random value 0..1", f"execute if score #c le.vt matches 0 run function last_ember:vault/gen/{one}",
          f"execute if score #c le.vt matches 1 run function last_ember:vault/gen/{two}"]
# staffs: a random permutation of all five over Р1..Р5; a taken staff leaves its region without one (it gets a filler)
for s in STAFFS: L.append(f"scoreboard players set #p.{s} le.vt 0")
for r in STAFF_REGIONS:
    for s in STAFFS: w(f"stf_{s}_{r}", [f"# {MAIN_ITEMS[s][1]} -> {r}", f"scoreboard players set #p.{s} le.vt 1"] + place(s, [r]) + ["return 1"])
    L.append(f"function {chooser(STAFFS, lambda s: f'if score #p.{s} le.vt matches 0', lambda s, r=r: f'function last_ember:vault/gen/stf_{s}_{r}', f'a staff for {r}')}")
L.append("# 5. one golden apple per region, one grimoire of Mending in the game (Р6)")
for r in BOOKS:
    if not REG[r]: continue
    L.append("scoreboard players set #had le.vt 0")
    L += [f"execute if score {H('o', v['id'])} le.vt matches 1 if score {H('a', v['id'])} le.vt matches 1 run scoreboard players set #had le.vt 1" for v in REG[r]]
    L.append(f"execute if score #had le.vt matches 0 run function {chooser([v['id'] for v in REG[r]], lambda x: f'unless score {H(chr(111), x)} le.vt matches 1', lambda x: f'scoreboard players set {H(chr(97), x)} le.vt 1', f'the golden apple of {r}')}")
if REG["r6"]:
    L.append("scoreboard players set #had le.vt 0")
    L += [f"execute if score {H('o', v['id'])} le.vt matches 1 if score {H('e', v['id'])} le.vt matches 1 run scoreboard players set #had le.vt 1" for v in REG["r6"]]
    L.append(f"execute if score #had le.vt matches 0 run function {chooser([v['id'] for v in REG['r6']], lambda x: f'unless score {H(chr(111), x)} le.vt matches 1', lambda x: f'scoreboard players set {H(chr(101), x)} le.vt 1', 'the grimoire of Mending')}")
L.append("# 6. treasuries left without a main item: the filler (the best book of the region and ingots x2)")
for v in V: L.append(f"execute unless score {H('o', v['id'])} le.vt matches 1 if score {H('m', v['id'])} le.vt matches 0 run scoreboard players set {H('m', v['id'])} le.vt 99")
w("layout", L)
# ---------------------------------------------------------------- the start staff of a seer: one nobody has, out of its treasury
S = ["# as a seer at the start: #rnd le.e = a staff 1..5 that nobody has taken yet (else any); it is taken, its closed treasury gets the filler instead",
     "scoreboard players set #rnd le.e 0",
     f"function {chooser(STAFFS, lambda s: f'unless score #st.{s} le.vt matches 1', lambda s: f'scoreboard players set #rnd le.e {s}', 'a staff not taken')}",
     "execute if score #rnd le.e matches 0 store result score #rnd le.e run random value 1..5"]
for s in STAFFS:
    S.append(f"execute if score #rnd le.e matches {s} run scoreboard players set #st.{s} le.vt 1")
    for v in V:
        S.append(f"execute if score #rnd le.e matches {s} unless score {H('o', v['id'])} le.vt matches 1 if score {H('m', v['id'])} le.vt matches {s} run scoreboard players set {H('m', v['id'])} le.vt 99")
        S.append(f"execute if score #rnd le.e matches {s} unless score {H('o', v['id'])} le.vt matches 1 if score {H('m2', v['id'])} le.vt matches {s} run scoreboard players set {H('m2', v['id'])} le.vt 0")
w("staff_pick", S)
# ---------------------------------------------------------------- admin: the layout in chat
names = {k: n for k, (m, n, i) in MAIN_ITEMS.items()}; names[99] = "запасной"; names[98] = "свой (задача региона)"; names[0] = "—"
sh = ['tellraw @s {"text":"Сокровищницы: главный предмет [второй] · яблоко · Починка · открыта","color":"gold"}']
for v in V:
    vid = v["id"]
    sh.append('tellraw @s [{"text":"%s %s%s: ","color":"yellow"},{"score":{"name":"%s","objective":"le.vt"},"color":"white"},{"text":" ["},{"score":{"name":"%s","objective":"le.vt"}},{"text":"] · "},{"score":{"name":"%s","objective":"le.vt"}},{"text":" · "},{"score":{"name":"%s","objective":"le.vt"}},{"text":" · "},{"score":{"name":"%s","objective":"le.vt"}}]'
              % (vid, v["r"], " danger" if v["danger"] else "", H("m", vid), H("m2", vid), H("a", vid), H("e", vid), H("o", vid)))
sh.append('tellraw @s {"text":"%s","color":"gray"}' % ", ".join(f"{k} {n}" for k, n in sorted(names.items()) if k))
w("show", sh)
w("dump", ["# TEST: the layout into storage last_ember:vt d (one read for the tests)", "data remove storage last_ember:vt d"] +
  [f"execute store result storage last_ember:vt d.{v['id']}.{k} int 1 run scoreboard players get {H(k, v['id'])} le.vt" for v in V for k in ("m", "m2", "a", "e", "o")] +
  [f"execute store result storage last_ember:vt d.st{s} int 1 run scoreboard players get #st.{s} le.vt" for s in STAFFS])
ver = zlib.crc32(json.dumps([[v["id"], v["r"], v["danger"], v["main"]] for v in V]).encode()) & 0x7FFFFFFF
w("const", ["# generated: the version of the treasury list (a change -> the layout is made again for closed treasuries)", f"scoreboard players set #genver le.vt {ver}",
            f"scoreboard players set #count le.vt {len(V)}"])
print(f"loot: common r0..r6, {len(V)} treasuries ({', '.join(f'{r}:{len(REG[r])}' for r in BOOKS)}), {CH[0]} choosers")
for x in warn: print("WARNING:", x)
