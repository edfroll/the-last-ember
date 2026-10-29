#!/usr/bin/env python3
"""T-020: contracts/contracts.txt (+ extra files: the test playground contracts/test_contracts.txt) -> generated, do not edit:
  datapack function/contract/gen/*   (state of every contract, boards, the trail of clues, the monster of the contract, rewards, rituals, twins, choices)
  datapack loot_table/contract/*     (rewards by region, trophies), dialog/contract/* (the text of a contract in a dialog window)
Usage: python3 tools/gen_contracts.py [extra_file ...]      (regenerate WITHOUT the test file before a commit)
The format of the lines is in the comment at the top of contracts/contracts.txt."""
import json, os, shlex, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DP = os.path.join(ROOT, "datapack/data/last_ember")
GEN = os.path.join(DP, "function/contract/gen"); LOOT = os.path.join(DP, "loot_table/contract"); DLG = os.path.join(DP, "dialog/contract")
for d in (GEN, LOOT, DLG): shutil.rmtree(d, ignore_errors=True)
os.makedirs(os.path.join(GEN, "p"), exist_ok=True); os.makedirs(LOOT, exist_ok=True); os.makedirs(DLG, exist_ok=True)
def w(name, lines): open(os.path.join(GEN, name + ".mcfunction"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True); open(path, "w", encoding="utf-8").write(json.dumps(obj, ensure_ascii=False, indent=1) + "\n")
def J(o): return json.dumps(o, ensure_ascii=False)
def tx(t, c="gray", **k): d = {"text": t, "color": c}; d.update(k); return d
DIMS = {"overworld": "o", "the_nether": "n", "the_end": "e"}
KINDS = {  # the monsters (function/contract/k/<kind>/): lab sample, the head on the trophy shelf, the sound from the lair
    "heath_wolf": {"head": "last_ember:lab/heath_head", "hs": 0.55, "lair": "last_ember:creature.wild_dog.growl"},
    "grove_leshy": {"head": "last_ember:lab/leshy_head", "hs": 0.45, "lair": "last_ember:creature.leshen.mv_wood_stress"},
    "bog_womb": {"head": "last_ember:lab/womb", "hs": 0.35, "lair": "last_ember:creature.rotfiend.vo_breath"},
}
STRENGTH = {"r0": (120, 6, 4), "r1": (120, 6, 4), "r2": (160, 8, 6), "r3": (200, 9, 8), "r4": (240, 10, 10), "r5": (300, 12, 12), "r6": (360, 14, 14)}   # contracts.md: health, blow, armour
VALUE = {"r0": 8, "r1": 8, "r2": 10, "r3": 11, "r4": 12, "r5": 14, "r6": 15}
XP = {"r0": 5, "r1": 5, "r2": 7, "r3": 9, "r4": 11, "r5": 13, "r6": 15}
RNAME = {"r0": "Приют", "r1": "Сумеречный Дол", "r2": "Кольцевые горы", "r3": "Белая Тишь", "r4": "Опалённый Юг", "r5": "Глубины", "r6": "Пепельные Земли"}
TROPHY = {"r0": "Трофей Приюта", "r1": "Трофей Дола", "r2": "Трофей Кольцевых гор", "r3": "Трофей Белой Тиши", "r4": "Трофей Опалённого Юга", "r5": "Трофей Глубин", "r6": "Трофей Пепельных Земель"}
PART = {  # the particles of a clue: (dust colour, block crumbs)
    "blood": ([0.55, 0.03, 0.03], "minecraft:redstone_block"), "fur": ([0.42, 0.3, 0.2], "minecraft:brown_wool"), "scratch": ([0.85, 0.8, 0.7], "minecraft:stripped_oak_log"),
    "track": ([0.35, 0.28, 0.2], "minecraft:coarse_dirt"), "slime": ([0.4, 0.55, 0.25], "minecraft:slime_block"), "bark": ([0.3, 0.22, 0.14], "minecraft:oak_log"),
    "bone": ([0.85, 0.82, 0.72], "minecraft:bone_block")}

# ------------------------------------------------------------------ parsing
srcs = [os.path.join(ROOT, "contracts/contracts.txt")] + sys.argv[1:]
boards, contracts, clues, rituals, twins, choices, items = {}, {}, [], {}, [], {}, {}
def P3(s): return tuple(float(v) if "." in v else int(v) for v in s.split(","))
for src in srcs:
    for ln, raw in enumerate(open(src, encoding="utf-8"), 1):
        l = raw.strip()
        if not l or l.startswith("#"): continue
        f = shlex.split(l); kind = f[0]
        def kv(fs): return dict(x.split("=", 1) for x in fs)
        try:
            if kind == "board":
                b = dict(id=f[1], dim=f[2], **kv(f[3:])); b["signs"] = [P3(p) for p in b["signs"].split(";")]; b["heads"] = [P3(p) for p in b.get("heads", "").split(";") if p]
                b["n"] = len(boards) + 1; boards[b["id"]] = b
            elif kind == "contract":
                c = dict(id=f[1], **kv(f[2:])); c["n"] = len(contracts) + 1; contracts[c["id"]] = c
            elif kind == "clue":
                clues.append(dict(c=f[1], n=int(f[2]), x=int(f[3]), y=int(f[4]), z=int(f[5]), text=f[6], **kv(f[7:])))
            elif kind == "ritual":
                rituals[f[1]] = dict(c=f[1], x=int(f[2]), y=int(f[3]), z=int(f[4]), **kv(f[5:]))
            elif kind == "twin":
                twins.append(dict(c=f[1], name=f[2], **kv(f[3:])))
            elif kind == "choice":
                ch = dict(id=f[1], q=f[2], **kv(f[3:])); ch["n"] = len(choices) + 1; choices[ch["id"]] = ch
            elif kind == "item":
                items[f[1]] = dict(key=f[1], id=f[2], name=f[3], lore=f[4] if len(f) > 4 else "")
            else: raise ValueError("unknown line")
        except Exception as e: raise SystemExit(f"{src}:{ln}: {e}")
for c in contracts.values():
    if c["monster"] not in KINDS: raise SystemExit("unknown monster " + c["monster"])
    if c["board"] not in boards: raise SystemExit("unknown board " + c["board"])
    c["lair"] = P3(c["lair"]); c.setdefault("dim", "overworld"); c["coop"] = [x for x in c.get("coop", "").split(",") if x]
    c["hp"], c["dmg"], c["arm"] = STRENGTH[c["region"]]
    c["duo"] = c.get("duo", "1") == "1"; c["slot"] = int(c.get("slot", 1)); c["warn"] = int(c.get("warn", 15))
    c["open"] = int(c.get("open", max(0, int(c["region"][1:]) - 1)))
    c["from"] = [P3(p) for p in c.get("from", "").split(";") if p] or [c["lair"]]
    c["main"] = sorted([k for k in clues if k["c"] == c["id"] and "branch" not in k], key=lambda k: k["n"])
    c["br"] = {b: sorted([k for k in clues if k["c"] == c["id"] and k.get("branch") == b], key=lambda k: k["n"]) for b in "ab"}
    c["split"] = bool(c["br"]["a"] or c["br"]["b"])
    c["rit"] = rituals.get(c["id"]); c["tw"] = [t for t in twins if t["c"] == c["id"]]
    if c["split"] and not c["main"]: raise SystemExit(c["id"] + ": branches need a main trail to the fork")

def S(c, k): return "#%s_%s le.ct" % (c["id"], k)
def IN(c): return "execute in minecraft:%s " % c["dim"]
def xyz(p): return " ".join(str(v) for v in p)

# ------------------------------------------------------------------ loot: the reward of a region (value from economy.md), the trophy
def tbl(pools): return {"type": "minecraft:chest", "pools": pools}
def it(name, n=1, mods=()):
    e = {"type": "minecraft:item", "name": "minecraft:" + name}
    m = list(mods) + ([{"type": "minecraft:set_count", "count": n}] if n != 1 else [])
    if m: e["modifier"] = m
    return e
def book(lv_min, lv_max): return {"type": "minecraft:item", "name": "minecraft:book", "modifier": [{"type": "minecraft:enchant_randomly", "only_compatible": False},
                                  {"type": "minecraft:set_enchantments", "enchantments": {}, "add": False}] if False else [{"type": "minecraft:enchant_with_levels", "levels": {"type": "minecraft:uniform", "min": lv_min, "max": lv_max}, "options": "#minecraft:on_random_loot"}]}
for r, v in VALUE.items():
    ingots = v // 2
    dump(os.path.join(LOOT, "reward_%s.json" % r), tbl([
        {"rolls": 1, "entries": [dict(book(8 + v * 2, 12 + v * 3), weight=2), dict(it("iron_ingot", v - 2), weight=2), dict(it("gold_ingot", max(2, v // 2)), weight=1)]},
        {"rolls": 1, "entries": [dict(it("iron_ingot", ingots // 2 + 1), weight=2), dict(it("golden_apple"), weight=1) if v >= 12 else dict(it("experience_bottle", 4), weight=1),
                                 dict(it("potion", 2, [{"type": "minecraft:set_potion", "id": "minecraft:healing"}]), weight=2)]}]))
    dump(os.path.join(LOOT, "trophy_%s.json" % r), tbl([{"rolls": 1, "entries": [{"type": "minecraft:item", "name": "minecraft:nautilus_shell", "modifier": [
        {"type": "minecraft:set_components", "components": {"minecraft:custom_data": {"le_trophy": r}, "minecraft:item_model": "last_ember:trophy_" + r, "minecraft:max_stack_size": 16, "minecraft:rarity": "rare",
         "minecraft:lore": [tx("Знак убитой элиты. Его ценят торговцы.", italic=False)]}},
        {"type": "minecraft:set_name", "entity": "this", "target": "custom_name", "name": tx(TROPHY[r], "gold", italic=False)}]}]}]))
for k, i in items.items():   # quest items (the bait of the second branch, the thing of the cursed one's past life): never lost on death (le_keep)
    comp = {"minecraft:custom_data": {"le_keep": 1, "le_citem": k}, "minecraft:item_name": tx(i["name"], "gold", italic=False), "minecraft:max_stack_size": 1}
    if i["lore"]: comp["minecraft:lore"] = [tx(i["lore"], italic=False)]
    dump(os.path.join(LOOT, "item_%s.json" % k), tbl([{"rolls": 1, "entries": [{"type": "minecraft:item", "name": i["id"], "modifier": [{"type": "minecraft:set_components", "components": comp}]}]}]))

# ------------------------------------------------------------------ init, the cell index
init = ["# generated: the state of every contract (kept over reloads) and the cells of the index"]
for c in contracts.values():
    for k in ("s", "m", "w", "cl", "ca", "cb", "oa", "ob", "da", "db", "hf", "rs", "rt", "wk", "g", "cu", "wt", "t1", "t2", "dr", "lc", "sb"):
        init.append("execute unless score %s matches -2147483648..2147483647 run scoreboard players set %s 0" % (S(c, k), S(c, k)))
    init.append("execute unless data storage last_ember:contracts c.%s run data modify storage last_ember:contracts c.%s set value {s:0,n:0,got:0,parts:[],title:%s}" % (c["id"], c["id"], J(c["title"])))
    init.append("execute if score %s matches 0 run scoreboard players set %s 1" % (S(c, "cl"), S(c, "cl")))
    for b in "ab":
        init.append("execute if score %s matches 0 run scoreboard players set %s 1" % (S(c, "c" + b), S(c, "c" + b)))
for b in boards.values():
    init.append("execute unless score #b_%s_bl le.ct matches 0.. run scoreboard players set #b_%s_bl le.ct 0" % (b["id"], b["id"]))
    init.append("execute unless score #b_%s_hd le.ct matches 0.. run scoreboard players set #b_%s_hd le.ct 0" % (b["id"], b["id"]))
cells = {}
def addcell(c, pts, m):
    for (x, y, z) in pts:
        for cx in range((x - m + 8192) // 64, (x + m + 8192) // 64 + 1):
            for cz in range((z - m + 8192) // 64, (z + m + 8192) // 64 + 1):
                lst = cells.setdefault((DIMS[c["dim"]], cx, cz), [])
                if c not in lst: lst.append(c)
for c in contracts.values():
    pts = [(k["x"], k["y"], k["z"]) for k in c["main"] + c["br"]["a"] + c["br"]["b"]]
    addcell(c, pts, 21)
    if "bait" in c: bx, by, bz, br = P3(c["bait"]); addcell(c, [(bx, by, bz)], br + 2)
    for t in c["tw"]: addcell(c, [P3(t["a"]), P3(t["b"])], 6)
    if c["rit"]: addcell(c, [(c["rit"]["x"], c["rit"]["y"], c["rit"]["z"])], int(c["rit"].get("r", 3)) + 2)
    if "drag" in c: addcell(c, [P3(c["drag"])], 6)
for (d, cx, cz), cs in cells.items():
    init.append("data modify storage last_ember:contracts cells.%s%d_%d set value 1b" % (d, cx, cz))
    w("p/%s%d_%d" % (d, cx, cz), ["# generated: the contracts with clues, baits, twins or a ritual circle in this cell (as a player at himself)"] +
      ["execute if score %s matches 2..4 run function last_ember:contract/gen/near_%s" % (S(c, "s"), c["id"]) for c in cs])
w("init", init)

# ------------------------------------------------------------------ boards: signs, interactions, the trophy shelf
FACE = {"n": ("north", 0, -1, 180), "s": ("south", 0, 1, 0), "e": ("east", 1, 0, -90), "w": ("west", -1, 0, 90)}
bp = ["# generated: every second: boards whose chunk is loaded get their click boxes (once) and their texts"]
for b in boards.values():
    fn, fx, fz, yaw = FACE[b.get("facing", "n")]; bi = b["id"]; dim = "execute in minecraft:%s " % b["dim"]
    on = [c for c in contracts.values() if c["board"] == bi]
    build = ["# generated: build the board %s (the signs if build=1, the click boxes, the texts)" % bi, "scoreboard players set #b_%s_bl le.ct 1" % bi,
             dim + "run kill @e[type=minecraft:interaction,tag=le.cb_%s]" % bi]
    for k, (x, y, z) in enumerate(b["signs"], 1):
        if b.get("build") == "1":
            build.append(dim + "run setblock %d %d %d minecraft:dark_oak_wall_sign[facing=%s]" % (x, y, z, fn))
        # the click box covers the sign plate (it lies against the wall, on the far side of its block)
        ix, iz = x + 0.5 - fx * 0.3, z + 0.5 - fz * 0.3
        build.append(dim + "run summon minecraft:interaction %.2f %.2f %.2f {Tags:[\"le.cboard\",\"le.cb_%s\"],width:0.9f,height:0.75f,response:1b}" % (ix, y + 0.05, iz, bi))
        build.append(dim + "positioned %.2f %.2f %.2f run scoreboard players set @e[type=minecraft:interaction,tag=le.cb_%s,distance=..0.1] le.cslot %d" % (ix, y + 0.05, iz, bi, b["n"] * 100 + k))
    build.append("function last_ember:contract/gen/board_%s" % bi)
    w("bbuild_" + bi, build)
    bx, by, bz = b["signs"][0]
    bp.append("execute if score #b_%s_bl le.ct matches 0 %sif loaded %d %d %d run function last_ember:contract/gen/bbuild_%s" % (bi, dim.replace("execute ", ""), bx, by, bz, bi))
    # the text of every slot: the first contract of the slot (in file order) that is on the board (state 1..4)
    bd = ["# generated: the texts of the board %s" % bi, "execute unless score #b_%s_bl le.ct matches 1 run return 0" % bi]
    for k, (x, y, z) in enumerate(b["signs"], 1):
        sl = [c for c in on if c["slot"] == k]
        bd.append("scoreboard players set #shown le.ct 0")
        for c in sl:
            t = c["title"]; words = t.split(); l1, l2 = "", ""
            for wd in words:
                if len(l1) + len(wd) + 1 <= 15 and not l2: l1 = (l1 + " " + wd).strip()
                else: l2 = (l2 + " " + wd).strip()
            for st, status in ((1, tx("на двоих" if c["duo"] else "", "dark_gray")), (2, tx("взят", "dark_red")), (3, tx("взят", "dark_red")), (4, tx("взят", "dark_red"))):
                msg = [tx(RNAME[c["region"]], "dark_gray"), tx(l1, "black"), tx(l2, "black"), status]
                bd.append("execute if score #shown le.ct matches 0 if score %s matches %d run %srun data merge block %d %d %d {is_waxed:1b,front_text:{messages:%s}}"
                          % (S(c, "s"), st, dim, x, y, z, J(msg)))
            bd.append("execute if score %s matches 1..4 run scoreboard players set #shown le.ct 1" % S(c, "s"))
        bd.append("execute if score #shown le.ct matches 0 run %srun data merge block %d %d %d {is_waxed:1b,front_text:{messages:['\"\"','\"\"','\"\"','\"\"']}}" % (dim, x, y, z))
    w("board_" + bi, bd)
    # a click: as the player (le.cslot of the box in #slot); the slot shows its contract; any click also hands out the rewards owed here
    ck = ["# generated: a click on the board %s (as the player, the slot in #slot)" % bi, "function last_ember:contract/gen/claim_%s" % bi]
    for k in range(1, len(b["signs"]) + 1):
        sl = [c for c in on if c["slot"] == k]
        line = ["scoreboard players set #shown le.ct 0"]
        for c in sl:
            line.append("execute if score #shown le.ct matches 0 if score %s matches 1..4 run function last_ember:contract/gen/show_%s" % (S(c, "s"), c["id"]))
            line.append("execute if score %s matches 1..4 run scoreboard players set #shown le.ct 1" % S(c, "s"))
        line.append("execute if score #shown le.ct matches 0 run title @s actionbar %s" % J(tx("Здесь пока ничего нет", "gray")))
        w("slot_%s_%d" % (bi, k), ["# generated"] + line)
        ck.append("execute if score #slot le.ct matches %d run function last_ember:contract/gen/slot_%s_%d" % (b["n"] * 100 + k, bi, k))
    w("click_" + bi, ck)
    cl = ["# generated: as a player at the board %s: every reward owed to him here" % bi]
    for c in on: cl.append("execute if score %s matches 5 if entity @s[tag=le.cp_%s,tag=!le.cr_%s] run function last_ember:contract/gen/reward_%s" % (S(c, "s"), c["id"], c["id"], c["id"]))
    w("claim_" + bi, cl)
w("bp", bp)
w("click", ["# generated: a click on a board box (le.cslot in #slot), as the player"] +
  ["execute if score #slot le.ct matches %d..%d run function last_ember:contract/gen/click_%s" % (b["n"] * 100, b["n"] * 100 + 99, b["id"]) for b in boards.values()])

# ------------------------------------------------------------------ per contract
sec = ["# generated: every second, every contract", "scoreboard players set #active le.ct 0"]; fast = ["# generated: every 5 ticks: twins (two braziers / levers within 1 s) of the contracts that are on"]
mt = ["# generated: as a monster of a contract (le.contract), every tick: 1 = the lab body skips this tick"]; died = ["# generated: as a monster of a contract that died by our rules"]
take = ["# generated: the trigger le.ctake (the take button of a contract window), as the player"]
stats = ["# generated: the states of all contracts", "tellraw @s %s" % J(tx("Заказы: состояние 0 не виден, 1 на доске, 2 взят, 3 след пройден, 4 чудовище, 5 выполнен, 6 награда выдана", "gold"))]
hurt_p = ["# generated: as a player hurt by the main monster of a contract (#cid): the drag of that contract"]
for c in contracts.values():
    i, n, kd = c["id"], c["n"], c["monster"]; lx, ly, lz = c["lair"]; L = "%d %d %d" % (lx, ly, lz); I = IN(c); st = S(c, "s")
    hp, dmg, arm = c["hp"], c["dmg"], c["arm"]; HMAX = (500 + hp) * 10
    ME = "@e[tag=le.ct_%s,tag=le.cmain,limit=1]" % i
    PL = "@a[gamemode=!spectator,gamemode=!creative]"
    def setst(s): return ["scoreboard players set %s %d" % (st, s), "function last_ember:contract/gen/set_%s" % i]
    w("set_" + i, ["# generated: the state score of %s -> storage, the board" % i,
                   "execute store result storage last_ember:contracts c.%s.s int 1 run scoreboard players get %s" % (i, st),
                   "execute if score %s matches 2..4 run scoreboard players set #active le.ct 1" % st,
                   "function last_ember:contract/gen/board_%s" % c["board"]])
    # --- visible on the board when the path to its region is open
    sec.append("execute if score %s matches 0 if score #chapters le.alt matches %d.. run function last_ember:contract/gen/reveal_%s" % (st, c["open"], i))
    w("reveal_" + i, ["# generated"] + setst(1))
    # --- the window (dialog): the offer with the take button, or the notice when it is taken
    body = [{"type": "minecraft:plain_message", "contents": tx(c.get("giver", "Заказчик"), "dark_gray"), "width": 300},
            {"type": "minecraft:plain_message", "contents": tx(c.get("text", "…"), "white"), "width": 300},
            {"type": "minecraft:plain_message", "contents": tx("Присядь — увидишь следы. Следопыт видит их и стоя.", "gray", italic=True), "width": 300}]
    if c["duo"]: body.append({"type": "minecraft:plain_message", "contents": tx("Этот заказ — на двоих.", "gold"), "width": 300})
    dump(os.path.join(DLG, i + ".json"), {"type": "minecraft:multi_action", "title": tx(c["title"], "gold"), "body": body, "can_close_with_escape": True, "pause": False, "after_action": "close",
         "actions": [{"label": tx("Взять заказ", "green"), "width": 150, "action": {"type": "minecraft:run_command", "command": "trigger le.ctake set %d" % n}}],
         "exit_action": {"label": tx("Закрыть", "gray"), "width": 150}, "columns": 1})
    dump(os.path.join(DLG, i + "_taken.json"), {"type": "minecraft:notice", "title": tx(c["title"], "gold"), "body": body[:2] + [
         {"type": "minecraft:plain_message", "contents": tx("Заказ взят.", "dark_red"), "width": 300}], "can_close_with_escape": True, "pause": False,
         "action": {"label": tx("Закрыть", "gray"), "width": 150}})
    w("show_" + i, ["# generated: as the player who clicked the slot of %s" % i,
                    "execute if score %s matches 1 run scoreboard players enable @s le.ctake" % st,
                    "execute if score %s matches 1 run return run dialog show @s last_ember:contract/%s" % (st, i),
                    "dialog show @s last_ember:contract/%s_taken" % i])
    duo = ["execute if score #online le.ct matches ..1 run return run tellraw @s %s" % J(tx("Этот заказ — на двоих. Возвращайтесь вдвоём.", "gold"))] if c["duo"] else []
    w("take_" + i, ["# generated: as the player who pressed the take button of %s" % i, "execute unless score %s matches 1 run return 0" % st,
                    "execute unless entity @e[type=minecraft:interaction,tag=le.cb_%s,distance=..10] run return 0" % c["board"]] + duo +
      ["function last_ember:contract/gen/give_" + i])
    take.append("execute if score #t le.ct matches %d run function last_ember:contract/gen/take_%s" % (n, i))
    w("give_" + i, ["# generated: %s is taken (by the take button or the admin)" % i] + setst(2) +
      ["tellraw %s [%s,%s,%s]" % (PL, J(tx("Заказ взят: ", "gold")), J(tx("«%s»" % c["title"], "white")), J(tx(". Присядьте у места, где всё случилось, — увидите следы.", "gray"))),
       "execute as %s at @s run playsound minecraft:item.book.page_turn player @s ~ ~ ~ 1 0.8" % PL])
    # --- the trail: main clues, the fork, branches a and b
    nm = len(c["main"]); nb = {b: len(c["br"][b]) for b in "ab"}
    near = ["# generated: as a player in a cell of %s (state 2..4), every 5 ticks" % i, "scoreboard players set #ch le.ct 0",
            "execute if predicate last_ember:sneaking run scoreboard players set #ch le.ct 1", "execute if entity @s[tag=le.class.ranger] run scoreboard players set #ch le.ct 2",
            "execute if score #ch le.ct matches 1.. run function last_ember:contract/pn"]
    def particles(k, strong):
        col, blk = PART.get(k.get("p", "blood"), PART["blood"])
        return (["particle minecraft:dust{color:%s,scale:%s} %d %.1f %d 0.35 0.1 0.35 0 %d force @s" % (J(col), "1.1" if strong else "0.7", k["x"], k["y"] + 0.15, k["z"], 6 if strong else 2)] +
                (["particle minecraft:block{block_state:\"%s\"} %d %.1f %d 0.3 0.05 0.3 0 2 force @s" % (blk, k["x"], k["y"] + 0.1, k["z"])] if strong else []))
    def trail(lst, idx, tag):
        """the reading and the glow of a list of clues (idx = the score of the next one); returns the lines"""
        out = []
        for j, k in enumerate(lst, 1):
            kx, ky, kz = k["x"], k["y"], k["z"]
            show = []
            for jj, strong in ((j, True), (j + 1, False), (j + 2, False)):
                if jj <= len(lst): show += particles(lst[jj - 1], strong)
            fn = "%s_%s_%d" % (i, tag, j)
            vis = ["# generated: the glow of the clue %s %d and the two after it (only to this player)" % (tag, j)]
            for p in show: vis.append(p)
            w("cv_" + fn, vis)
            out.append("execute if score #half le.ct matches 0 if score %s matches %d if score #ch le.ct matches 1 positioned %d %d %d if entity @s[distance=..12] run function last_ember:contract/gen/cv_%s" % (idx, j, kx, ky, kz, fn))
            out.append("execute if score #half le.ct matches 0 if score %s matches %d if score #ch le.ct matches 2 positioned %d %d %d if entity @s[distance=..20] run function last_ember:contract/gen/cv_%s" % (idx, j, kx, ky, kz, fn))
            out.append("execute if score %s matches %d if score #ch le.ct matches 1.. positioned %d %d %d if entity @s[distance=..3] run function last_ember:contract/gen/cr_%s" % (idx, j, kx, ky, kz, fn))
            rd = ["# generated: the clue %s %d of %s is read" % (tag, j, i), "scoreboard players add %s 1" % idx,
                  "title @s actionbar %s" % J(tx(k["text"], "gold")), "playsound minecraft:block.sculk_sensor.clicking player @s ~ ~ ~ 0.6 1.6"]
            if j == len(lst): rd.append("function last_ember:contract/gen/tend_%s_%s" % (i, tag))
            w("cr_" + fn, rd)
        return out
    near += trail(c["main"], S(c, "cl"), "m")
    tend = {"m": ["# generated: the end of the main trail of %s" % i]}
    if c["split"]:
        fx_, fy_, fz_ = c["main"][-1]["x"], c["main"][-1]["y"], c["main"][-1]["z"]
        tend["m"] += ["title @s actionbar %s" % J(tx(c.get("fork_text", "Следы расходятся надвое."), "gold"))]
        near.append("execute if score %s matches %d.. if score #ch le.ct matches 1.. positioned %d %d %d if entity @s[distance=..4] run function last_ember:contract/gen/fork_%s" % (S(c, "cl"), nm + 1, fx_, fy_, fz_, i))
        fork = ["# generated: a player crouches at the fork of %s: if he follows no branch, he takes the first free one" % i,
                "execute if score %s = @s le.cpn run return 0" % S(c, "oa"), "execute if score %s = @s le.cpn run return 0" % S(c, "ob")]
        for b in "ab":
            lbl = c.get("branch_" + b, "Ветка " + ("первая" if b == "a" else "вторая"))
            fork.append("execute if score %s matches 0 if score %s matches 0 run return run function last_ember:contract/gen/own_%s_%s" % (S(c, "d" + b), S(c, "o" + b), i, b))
            w("own_%s_%s" % (i, b), ["# generated: the player takes the branch %s of %s" % (b, i), "scoreboard players operation %s = @s le.cpn" % S(c, "o" + b),
                                     "title @s actionbar %s" % J(tx("Ты идёшь по следу: " + lbl, "gold")), "playsound minecraft:block.sculk_sensor.clicking player @s ~ ~ ~ 0.8 1.2"])
        w("fork_" + i, fork)
        for b in "ab":
            if not c["br"][b]: continue
            bl = trail(c["br"][b], S(c, "c" + b), b)
            # only its owner sees and reads the branch; another player crouching ON its next clue takes it over
            for ln_ in bl:
                near.append("execute if score %s matches %d.. if score %s matches 0 if score %s = @s le.cpn run " % (S(c, "cl"), nm + 1, S(c, "d" + b), S(c, "o" + b)) + ln_[len("execute "):].replace("execute ", "", 0) if False else
                            ln_.replace("execute if ", "execute if score %s matches %d.. if score %s matches 0 if score %s = @s le.cpn if " % (S(c, "cl"), nm + 1, S(c, "d" + b), S(c, "o" + b)), 1))
            for j, k in enumerate(c["br"][b], 1):
                near.append("execute if score %s matches %d.. if score %s matches 0 if score %s matches %d unless score %s = @s le.cpn if score #ch le.ct matches 1.. positioned %d %d %d if entity @s[distance=..3] run function last_ember:contract/gen/steal_%s_%s"
                            % (S(c, "cl"), nm + 1, S(c, "d" + b), S(c, "c" + b), j, S(c, "o" + b), k["x"], k["y"], k["z"], i, b))
            w("steal_%s_%s" % (i, b), ["# generated: the player takes over the branch %s of %s" % (b, i), "scoreboard players operation %s = @s le.cpn" % S(c, "o" + b),
                                       "title @s actionbar %s" % J(tx("Ты перехватил след", "gold"))])
            give = ["loot give @s loot last_ember:contract/item_%s" % c["give_" + b]] if c.get("give_" + b) else []
            tend[b] = ["# generated: the end of the branch %s of %s" % (b, i), "scoreboard players set %s 1" % S(c, "d" + b), "scoreboard players set %s 0" % S(c, "o" + b)] + give + \
                      ["execute if score %s matches 1 if score %s matches 1 run function last_ember:contract/gen/trail_done_%s" % (S(c, "da"), S(c, "db"), i) if c["br"]["a"] and c["br"]["b"]
                       else "function last_ember:contract/gen/trail_done_%s" % i]
        if not c["br"]["a"]: init.append("scoreboard players set %s 1" % S(c, "da"))
        if not c["br"]["b"]: init.append("scoreboard players set %s 1" % S(c, "db"))
    else:
        tend["m"].append("function last_ember:contract/gen/trail_done_%s" % i)
    if c.get("give_m"): tend["m"].insert(1, "loot give @s loot last_ember:contract/item_%s" % c["give_m"])
    for k, v in tend.items(): w("tend_%s_%s" % (i, k), v)
    w("trail_done_" + i, ["# generated: the whole trail of %s is read" % i, "execute if score %s matches 2 run scoreboard players set %s 3" % (st, st),
                          "execute if score %s matches 3 run function last_ember:contract/gen/set_%s" % (st, i)])
    if not c["main"] and not c["split"]: init.append("execute if score %s matches 2 run function last_ember:contract/gen/trail_done_%s" % (st, i))
    # --- the bait, the ritual circle and the twins (as a player near them)
    rule = c["spawn"]; when = c.get("when", "night" if rule == "night" else "storm" if rule == "storm" else "any")
    if "bait" in c:
        bx, by, bz, br = P3(c["bait"])
        need = c.get("need")
        cond = "execute if score %s matches 3 if score %s matches 0 " % (st, S(c, "m")) + ("if score %s matches 1 " % S(c, "d" + need) if need else "") + "positioned %d %d %d if entity @s[distance=..%d] " % (bx, by, bz, br)
        if c.get("bait_item"): cond += "if items entity @s weapon.* *[minecraft:custom_data~{le_citem:\"%s\"}] " % c["bait_item"]
        near.append(cond + "unless items entity @s weapon.* #last_ember:weapons unless items entity @s weapon.* *[minecraft:custom_data~{le_staff:1}] run scoreboard players set %s 1" % S(c, "sb"))
    if c["rit"]:
        R_ = c["rit"]; rr = int(R_.get("r", 3))
        near.append("execute if score %s matches 4 positioned %d %d %d if entity @s[distance=..%d] run function last_ember:contract/gen/incircle_%s" % (st, R_["x"], R_["y"], R_["z"], rr, i))
        key = R_.get("item")
        w("incircle_" + i, ["# generated: a player stands in the ritual circle of %s" % i] +
          (["execute unless items entity @s weapon.* *[minecraft:custom_data~{le_citem:\"%s\"}] run return run title @s actionbar %s" % (key, J(tx("Нужна вещь из его прошлой жизни", "gray")))] if key else []) +
          ["scoreboard players set #incircle_%s le.ct 1" % i])
    if "guard" in c:
        for (gx, gy, gz) in [(k["x"], k["y"], k["z"]) for k in c["main"] + c["br"]["a"] + c["br"]["b"]] + [c["lair"]]:   # only near its own clues and its lair
            near.append("execute if score #ch le.ct matches 1.. if score %s matches 2 if score %s matches ..0 positioned %d %d %d if entity @s[distance=..14] run function last_ember:contract/gen/guard_%s" % (st, S(c, "g"), gx, gy, gz, i))
    near.append("execute if score #ch le.ct matches 1.. run scoreboard players set #reading_%s le.ct 1" % i)
    # the lines that need a crouching player (or a ranger) go to their own function: most of the time nobody crouches
    head, rd_, rest = near[:5], [l for l in near[5:] if "#ch le.ct matches" in l], [l for l in near[5:] if "#ch le.ct matches" not in l]
    w("nr_" + i, ["# generated: the clues of %s for a player who crouches (rangers standing): #ch 1 crouching, 2 ranger" % i] + rd_)
    w("near_" + i, head + ["execute if score #ch le.ct matches 1.. run function last_ember:contract/gen/nr_" + i] + rest)
    # --- every second
    sl = ["# generated: every second while %s is taken (state 2..4)" % i, "execute if score %s matches 1.. run scoreboard players remove %s 1" % (S(c, "g"), S(c, "g"))]
    alive = "if score %s matches 1 " % S(c, "m")
    wait_duo = "if score #online le.ct matches 2.. " if c["duo"] else ""
    if rule == "lair":
        sl.append("execute if score %s matches 2..3 if score %s matches 0 %s%sif loaded %s unless entity @a[distance=..16] positioned %s run function last_ember:contract/gen/spawn_%s" % (st, S(c, "m"), I.replace("execute ", ""), wait_duo, L, L, i))
    else:
        cond = {"night": "if predicate last_ember:night ", "storm": "if predicate last_ember:thundering ", "any": ""}[when]
        trig = ""
        if rule == "bait": trig = "if score %s matches 1 " % S(c, "sb")
        elif rule == "event": trig = "if score %s matches 1 " % S(c, "sb")
        elif rule in ("night", "storm"): trig = ""
        sl.append("execute if score %s matches 3 if score %s matches 0 if score %s matches 0 %s%s%s%sif entity @a[gamemode=!spectator,gamemode=!creative,distance=..48] run function last_ember:contract/gen/warn_start_%s"
                  % (st, S(c, "m"), S(c, "w"), I.replace("execute ", "") + "positioned %s " % L, wait_duo, cond, trig, i))
        sl.append("execute if score %s matches 1.. run function last_ember:contract/gen/warn_%s" % (S(c, "w"), i))
        fr = c["from"][0]
        w("warn_start_" + i, ["# generated: something comes to %s: a warning sound from where it will come, %d s ahead" % (i, c["warn"]),
                              "scoreboard players set %s %d" % (S(c, "w"), c["warn"] + 1), "scoreboard players set %s 0" % S(c, "wt")])
        sound = c.get("warn_sound", {"heath_wolf": "last_ember:creature.wild_dog.howl", "bog_womb": "last_ember:creature.rotfiend.vo_breath", "grove_leshy": "last_ember:creature.leshen.crow_call_double_custom"}[kd])
        wl = ["# generated: the warning of %s (every second)" % i, "scoreboard players remove %s 1" % S(c, "w")]
        for fx, fy, fz in c["from"][:1]:
            wl.append("execute if score %s matches %d run %spositioned %d %d %d run playsound %s hostile @a[distance=..72] ~ ~ ~ 3.5 1" % (S(c, "w"), c["warn"], I, fx, fy, fz, sound))
            wl.append("execute if score %s matches %d run %spositioned %d %d %d run playsound %s hostile @a[distance=..72] ~ ~ ~ 3.5 0.9" % (S(c, "w"), max(1, c["warn"] // 2), I, fx, fy, fz, sound))
            if kd == "bog_womb":
                wl.append("execute if score %s matches 1.. %spositioned %d %d %d run particle minecraft:bubble_column_up ~ ~0.5 ~ 1 0.2 1 0.05 12" % (S(c, "w"), I.replace("execute ", ""), fx, fy, fz))
        wl.append("execute if score %s matches ..0 run function last_ember:contract/gen/arrive_%s" % (S(c, "w"), i))
        w("warn_" + i, wl)
        # the arrival: the first point not closer than 16 to any player and out of sight of all of them; else wait; after 15 s the spare one
        ar = ["# generated: the monster of %s arrives (the warning is over)" % i, "scoreboard players set %s 1" % S(c, "w"), "scoreboard players add %s 1" % S(c, "wt")]
        for fx, fy, fz in c["from"]:
            ar.append("%spositioned %d %d %d unless entity @a[gamemode=!spectator,distance=..16] unless function last_ember:contract/seen run return run function last_ember:contract/gen/spawn_%s" % (I, fx, fy, fz, i))
        if "alt" in c:
            ax, ay, az = P3(c["alt"])
            ar.append("execute if score %s matches 15.. %spositioned %d %d %d unless entity @a[gamemode=!spectator,distance=..16] run return run function last_ember:contract/gen/spawn_%s" % (S(c, "wt"), I.replace("execute ", ""), ax, ay, az, i))
        w("arrive_" + i, ar)
        sl.append("scoreboard players set %s 0" % S(c, "sb"))
    # the monster lives: the fighters within 24 are participants; nobody within 48 of the lair -> back to the lair with full health
    sl.append("execute %sas %s at @s run function last_ember:contract/gen/alive_%s" % (alive, ME, i))
    al = ["# generated: as the main monster of %s, every second" % i,
          "execute if score @s le.ls matches 2 as @a[gamemode=!spectator,gamemode=!creative,distance=..24] run function last_ember:contract/gen/part_%s" % i,
          "execute if score @s le.ls matches 2 if score %s matches 2..3 run function last_ember:contract/gen/fight_%s" % (st, i),
          "%spositioned %s unless entity @a[gamemode=!spectator,gamemode=!creative,distance=..48] run return run function last_ember:contract/gen/return_%s" % (I, L, i)]
    if when == "night": al.append("execute unless predicate last_ember:night unless entity @a[gamemode=!spectator,gamemode=!creative,distance=..24] run return run function last_ember:contract/gen/return_%s" % i)
    if c["duo"]: al.append("execute if score #online le.ct matches ..1 unless entity @a[gamemode=!spectator,gamemode=!creative,distance=..24] run return run function last_ember:contract/gen/return_%s" % i)
    al.append("execute if score @s le.ls matches 2 if score %s matches 1.. run function last_ember:contract/gen/rit_%s" % (S(c, "rs"), i) if c["rit"] else "# (no ritual)")
    al.append("execute if score %s matches 0 run function last_ember:contract/gen/rit_try_%s" % (S(c, "rs"), i) if c["rit"] else "# -")
    al.append("execute if entity @s[tag=le.cweak] run function last_ember:contract/gen/weak_tick_%s" % i if c["tw"] else "# -")
    al.append("execute if score @s le.ls matches 0 if entity @a[gamemode=!spectator,gamemode=!creative,distance=..40] if predicate last_ember:chance_30 run playsound %s hostile @a[distance=..40] ~ ~ ~ 1.2 0.8" % KINDS[kd]["lair"])
    w("alive_" + i, al)
    w("fight_" + i, ["# generated: the fight with the monster of %s has begun" % i] + setst(4))
    sec.append("execute if score %s matches 2..4 run scoreboard players add #active le.ct 1" % st)
    sec.append("execute if score %s matches 2..4 run function last_ember:contract/gen/sec_%s" % (st, i))
    w("sec_" + i, sl)
    w("part_" + i, ["# generated: as a player who takes part in the fight of %s" % i, "execute if entity @s[tag=le.cp_%s] run return 0" % i, "tag @s add le.cp_%s" % i,
                    "data modify storage last_ember:contracts c.%s.parts append from entity @s UUID" % i,
                    "execute store result storage last_ember:contracts c.%s.n int 1 run data get storage last_ember:contracts c.%s.parts" % (i, i)])
    # --- the spawn
    kp = "{id:\"%s\",n:%d,hp:%d,max:%d,hpm:%d,dmg:%d,arm:%d}" % (i, n, hp, 500 + hp, 500 + hp - 8, dmg, arm)
    w("spawn_" + i, ["# generated: the monster of %s at this place (lair: it waits dormant; others: it appears)" % i,
                     "scoreboard players set %s 1" % S(c, "m"), "scoreboard players set %s 0" % S(c, "w"), "scoreboard players set %s 0" % S(c, "hf"),
                     "function last_ember:contract/k/%s/spawn %s" % (kd, kp),
                     ("execute as %s run scoreboard players set @s le.ls 0" % ME) if rule == "lair" else ("execute if score %s matches 3 run function last_ember:contract/gen/fight_%s" % (st, i)),
                     "execute as %s at @s run rotate @s facing entity @p[gamemode=!spectator] feet" % ME])
    w("return_" + i, ["# generated: everyone is far away (or it is day / the second player left): the monster of %s goes back; nothing of the contract is reset" % i,
                      "scoreboard players set %s 0" % S(c, "rs"), "scoreboard players set %s 0" % S(c, "rt"),
                      ("%srun tp @s %s" % (I, L) + "\nscoreboard players set @s le.ls 0\nfunction last_ember:contract/m/full") if rule == "lair" else
                      "function last_ember:contract/m/vanish\nscoreboard players set %s 0\nexecute if score %s matches 4 run scoreboard players set %s 3\nfunction last_ember:contract/gen/set_%s" % (S(c, "m"), st, st, i)])
    # --- the monster's tick: the blows (the back, the ritual floor), the last hitter, half health, the leash
    floor = (500 + hp // 10) * 10
    m = ["# generated: as the main monster of %s at itself, every tick (from lab/body)" % i, "execute if score @s le.ls matches 3 run return 0"]
    m.append("execute store result score #h le.ct run data get entity @s Health 10")
    m.append("execute if score #h le.ct < @s le.chp run function last_ember:contract/gen/hurt_%s" % i)
    m.append("scoreboard players operation @s le.chp = #h le.ct")
    m.append("execute if function last_ember:contract/k/%s/pre run return 1" % kd)
    m.append("execute if score %s matches 0 if score #h le.ct matches ..%d run function last_ember:contract/gen/half_%s" % (S(c, "hf"), (500 + hp // 2) * 10, i))
    m.append("scoreboard players operation #t10 le.ct = #gt le.l")
    m.append("scoreboard players operation #t10 le.ct %= #10 le.ct")
    m.append("execute if score #t10 le.ct matches 0 unless score #noleash le.ct matches 1 %spositioned %s unless entity @s[distance=..%d] facing %s run tp @s ^ ^ ^1.5" % (I.replace("execute ", ""), L, int(c.get("leash", 32)), L))
    m.append("execute if score #t10 le.ct matches 0 run function last_ember:contract/k/%s/tick10" % kd)
    m.append("return 0")
    w("mt_" + i, m)
    mt.append("execute if entity @s[tag=le.ct_%s,tag=le.cmain] run return run function last_ember:contract/gen/mt_%s" % (i, i))
    hu = ["# generated: the monster of %s lost health (#h < le.chp, x10)" % i, "scoreboard players set #hurt le.ct 1", "scoreboard players operation #d le.ct = @s le.chp", "scoreboard players operation #d le.ct -= #h le.ct",
          "tag @s add le.cme", "execute on attacker if entity @s[type=minecraft:player] run function last_ember:contract/gen/hitby_%s" % i]
    if "back" in c["coop"]:
        hu.append("execute unless entity @s[tag=le.cweak] if function last_ember:contract/m/front run function last_ember:contract/m/glance")
        hu.append("execute unless entity @s[tag=le.cweak] unless function last_ember:contract/m/front if score #atk le.ct matches 1 run function last_ember:contract/m/backhit")
    if c["rit"]: hu.append("execute if score %s matches 1.. if score #h le.ct matches ..%d run scoreboard players set #h le.ct %d" % (S(c, "rs"), floor, floor))
    hu += ["execute store result entity @s Health float 0.1 run scoreboard players get #h le.ct", "tag @s remove le.cme", "tag @a remove le.catk"]
    w("hurt_" + i, hu)
    w("hitby_" + i, ["# generated: as the player who hurt the monster of %s: a participant, the last hitter" % i, "tag @s add le.catk", "scoreboard players set #atk le.ct 1",
                     "function last_ember:contract/gen/part_%s" % i, "data modify storage last_ember:contracts c.%s.last set from entity @s UUID" % i])
    w("half_" + i, ["# generated: the monster of %s is at half health" % i, "scoreboard players set %s 1" % S(c, "hf"), "function last_ember:contract/k/%s/half %s" % (kd, kp)])
    # --- the death, the reward, the head on the shelf
    b = boards[c["board"]]
    died.append("execute if entity @s[tag=le.ct_%s,tag=le.cmain] run return run function last_ember:contract/gen/died_%s" % (i, i))
    w("died_" + i, ["# generated: the monster of %s is dead (lab/die)" % i, "scoreboard players set %s 2" % S(c, "m"), "scoreboard players set %s 0" % S(c, "rs"),
                    "execute as @a[gamemode=!spectator,gamemode=!creative,distance=..24] run function last_ember:contract/gen/part_%s" % i, "function last_ember:contract/gen/done_%s" % i])
    w("done_" + i, ["# generated: %s is done (killed or the curse lifted)" % i] + setst(5) +
      ["execute as @a[tag=le.cp_%s] run tellraw @s %s" % (i, J([tx("Заказ выполнен: ", "gold"), tx("«%s»" % c["title"], "white"), tx(". Награда ждёт у доски.", "gray")])),
       "function last_ember:contract/gen/head_%s" % i])
    hx = ["# generated: the head of the monster of %s on the trophy shelf of the board %s (the next free place)" % (i, b["id"]), "scoreboard players add #b_%s_hd le.ct 1" % b["id"]]
    for h, (x, y, z) in enumerate(b["heads"], 1):
        fn_, fx_, fz_, yaw = FACE[b.get("facing", "n")]
        hx.append("execute if score #b_%s_hd le.ct matches %d run execute in minecraft:%s run summon minecraft:item_display %.1f %.2f %.1f {Tags:[\"le.chead\"],Rotation:[%df,0f],item_display:\"none\",item:{id:\"minecraft:stick\",count:1,components:{\"minecraft:item_model\":\"%s\"}},transformation:{translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],scale:[%sf,%sf,%sf],right_rotation:[0f,0f,0f,1f]}}"
                  % (b["id"], h, b["dim"], x + 0.5, y + 0.05, z + 0.5, yaw + 180, KINDS[kd]["head"], KINDS[kd]["hs"], KINDS[kd]["hs"], KINDS[kd]["hs"]))
    w("head_" + i, hx)
    reg = c["region"]
    rw = ["# generated: as a participant of %s at a board: his own full reward, the trophy to the last hitter" % i, "tag @s add le.cr_%s" % i]
    if c.get("cured_reward") or not c["rit"]:
        rw.append("execute if score %s matches 0 run loot give @s loot %s" % (S(c, "cu"), c.get("reward", "last_ember:contract/reward_" + reg)))
    else:
        rw.append("execute if score %s matches 0 run loot give @s loot %s" % (S(c, "cu"), c.get("reward", "last_ember:contract/reward_" + reg)))
    rw += ["xp add @s %d levels" % XP[reg], "data modify storage last_ember:contracts cmp set from storage last_ember:contracts c.%s.last" % i,
           "execute if score %s matches 0 store success score #diff le.ct run data modify storage last_ember:contracts cmp set from entity @s UUID" % S(c, "cu"),
           "execute if score %s matches 0 if score #diff le.ct matches 0 run loot give @s loot last_ember:contract/trophy_%s" % (S(c, "cu"), reg),
           "tellraw @s %s" % J([tx(c.get("giver", "Заказчик"), "gray"), tx(": «Спасибо. Это ваше — по праву».", "white")]),
           "playsound minecraft:entity.player.levelup player @s ~ ~ ~ 0.6 1",
           "execute store result score #got le.ct run data get storage last_ember:contracts c.%s.got" % i, "scoreboard players add #got le.ct 1",
           "execute store result storage last_ember:contracts c.%s.got int 1 run scoreboard players get #got le.ct" % i,
           "execute store result score #pn le.ct run data get storage last_ember:contracts c.%s.n" % i]
    rw += ["execute if score #got le.ct >= #pn le.ct run scoreboard players set %s 6" % st, "execute if score %s matches 6 run function last_ember:contract/gen/set_%s" % (st, i)]
    w("reward_" + i, rw)
    # --- the ritual: someone in the circle (with the thing), the monster within `hold`, the right time: a countdown that pauses
    if c["rit"]:
        R_ = c["rit"]; rx, ry, rz = R_["x"], R_["y"], R_["z"]; hold = int(R_.get("hold", 12)); secs = int(R_.get("secs", 40))
        tm = {"midnight": "if predicate last_ember:contract/midnight ", "night": "if predicate last_ember:night ", "any": ""}[R_.get("time", "midnight")]
        w("rit_try_" + i, ["# generated: as the monster of %s: the ritual starts when all is ready" % i,
                           "execute unless score #incircle_%s le.ct matches 1 run return 0" % i,
                           "execute unless score @s le.ls matches 2 run return 0",
                           "%spositioned %d %d %d unless entity @s[distance=..%d] run return run title @a[tag=le.cp_%s,distance=..32] actionbar %s" % (I, rx, ry, rz, hold, i, J(tx("Приведите его к кругу", "gray"))),
                           ("execute unless predicate last_ember:contract/midnight run return run title @a[distance=..32] actionbar %s" % J(tx("Не время. Ритуал — в полночь", "gray"))) if tm else "# any time",
                           "scoreboard players set %s 1" % S(c, "rs"), "scoreboard players set %s %d" % (S(c, "rt"), secs),
                           "title @a[tag=le.cp_%s] title %s" % (i, J(tx("Ритуал", "gold"))), "title @a[tag=le.cp_%s] subtitle %s" % (i, J(tx("Держите его. Не убивайте и не отпускайте.", "gray"))),
                           "%spositioned %d %d %d run playsound minecraft:block.beacon.activate block @a[distance=..32] ~ ~ ~ 1 0.6" % (I, rx, ry, rz),
                           "scoreboard players set #incircle_%s le.ct 0" % i])
        w("rit_" + i, ["# generated: as the monster of %s, every second of the ritual" % i,
                       "effect give @s minecraft:slowness 2 1 true",
                       "%srun particle minecraft:soul_fire_flame %d %d.2 %d %d 0.05 %d 0 24 force" % (I, rx, ry, rz, int(R_.get("r", 3)), int(R_.get("r", 3))),
                       "execute unless score #incircle_%s le.ct matches 1 run return run title @a[tag=le.cp_%s] actionbar %s" % (i, i, J(tx("Не выходи из круга", "gold"))),
                       "%spositioned %d %d %d unless entity @s[distance=..%d] run return run title @a[tag=le.cp_%s] actionbar %s" % (I, rx, ry, rz, hold, i, J(tx("Не отпускай его", "gold"))),
                       "scoreboard players remove %s 1" % S(c, "rt"),
                       "scoreboard players operation #show le.ct = %s" % S(c, "rt"),
                       "title @a[tag=le.cp_%s] actionbar [%s,{\"score\":{\"name\":\"#show\",\"objective\":\"le.ct\"},\"color\":\"gold\"}]" % (i, J(tx("Ритуал: ", "gray"))),
                       "particle minecraft:enchant ~ ~1.5 ~ 0.6 0.8 0.6 0.5 30",
                       "scoreboard players set #incircle_%s le.ct 0" % i,
                       "execute if score %s matches ..0 run function last_ember:contract/gen/cure_%s" % (S(c, "rt"), i)])
        hum = R_.get("human", "Проклятый")
        w("cure_" + i, ["# generated: as the monster of %s: the curse is lifted, it becomes a man" % i, "scoreboard players set %s 1" % S(c, "cu"), "scoreboard players set %s 0" % S(c, "rs"),
                        "scoreboard players set %s 2" % S(c, "m"),
                        "execute as @a[gamemode=!spectator,gamemode=!creative,distance=..24] run function last_ember:contract/gen/part_%s" % i,
                        "particle minecraft:flash{color:[1.0,0.9,0.7,1.0]} ~ ~1 ~ 0 0 0 0 1 force", "particle minecraft:end_rod ~ ~1 ~ 0.6 1 0.6 0.05 60 force",
                        "playsound minecraft:block.beacon.power_select hostile @a[distance=..32] ~ ~ ~ 1.2 0.7",
                        "summon minecraft:villager ~ ~ ~ {Tags:[\"le.npc\",\"le.noelite\",\"le.cured\",\"le.cured_%s\"],NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,CustomNameVisible:1b,CustomName:%s,VillagerData:{level:1,profession:\"minecraft:none\",type:\"minecraft:plains\"}}" % (i, J(tx(hum, "white"))),
                        "function last_ember:contract/m/vanish",
                        "tellraw @a[tag=le.cp_%s] %s" % (i, J(tx("Проклятие снято.", "gold"))),
                        ("function " + R_["on_cure"]) if R_.get("on_cure") else "# (the help of the cured: a hook for the region task: on_cure=<function>)",
                        "function last_ember:contract/gen/done_%s" % i])
    # --- twins: two braziers / levers within 1 s
    if c["tw"]:
        for t in c["tw"]:
            tn = t["name"]; ax, ay, az = P3(t["a"]); bx_, by_, bz_ = P3(t["b"]); fc = t.get("facing", "north"); kind_ = t.get("kind", "brazier")
            on_, off = ({"brazier": ("minecraft:campfire[lit=true,facing=%s]" % fc, "minecraft:campfire[lit=false,facing=%s]" % fc),
                         "lever": ("minecraft:lever[face=wall,facing=%s,powered=true]" % fc, "minecraft:lever[face=wall,facing=%s,powered=false]" % fc),
                         "douse": ("minecraft:campfire[lit=false,facing=%s]" % fc, "minecraft:campfire[lit=true,facing=%s]" % fc)})[kind_]
            ta, tb = "#%s_%s_ta le.ct" % (i, tn), "#%s_%s_tb le.ct" % (i, tn)
            init += ["execute unless score %s matches -2147483648.. run scoreboard players set %s 0" % (ta, ta), "execute unless score %s matches -2147483648.. run scoreboard players set %s 0" % (tb, tb)]
            on_chk = on_.split("[")[0] + "[" + on_.split("[")[1].split(",")[0] + "]" if kind_ != "lever" else "minecraft:lever[powered=true]"
            tl = ["# generated: the twin %s of %s (every 5 ticks while a player is near)" % (tn, i)]
            for side, (x_, y_, z_), tt in (("a", (ax, ay, az), ta), ("b", (bx_, by_, bz_), tb)):
                tl.append("%sif score %s matches 0 if block %d %d %d %s run scoreboard players operation %s = #gt le.ct" % (I, tt, x_, y_, z_, on_chk, tt))
            tl.append("execute if score %s matches 1.. if score %s matches 1.. run return run function last_ember:contract/gen/twin_ok_%s_%s" % (ta, tb, i, tn))
            for side, (x_, y_, z_), tt in (("a", (ax, ay, az), ta), ("b", (bx_, by_, bz_), tb)):
                tl.append("scoreboard players operation #dt le.ct = #gt le.ct")
                tl.append("scoreboard players operation #dt le.ct -= %s" % tt)
                tl.append("execute if score %s matches 1.. if score #dt le.ct matches 21.. run function last_ember:contract/gen/twin_off_%s_%s_%s" % (tt, i, tn, side))
                w("twin_off_%s_%s_%s" % (i, tn, side), ["# generated: only one of the two in time: it goes out again", "scoreboard players set %s 0" % tt,
                                                         "%srun setblock %d %d %d %s" % (I, x_, y_, z_, off),
                                                         "%spositioned %d %d %d run playsound minecraft:block.fire.extinguish block @a[distance=..16] ~ ~ ~ 1 0.8" % (I, x_, y_, z_),
                                                         "%spositioned %d %d %d run title @a[distance=..16] actionbar %s" % (I, x_, y_, z_, J(tx(t.get("hint", "Одному не успеть — нужно вместе"), "gray")))])
            w("twin_%s_%s" % (i, tn), tl)
            fast.append("execute if score %s matches 2..4 %spositioned %d %d %d if entity @a[gamemode=!spectator,distance=..24] run function last_ember:contract/gen/twin_%s_%s" % (st, I.replace("execute ", ""), ax, ay, az, i, tn))
            eff = t.get("effect", "weak"); dur = int(t.get("dur", 20))
            ok = ["# generated: the twin %s of %s is done together (-1: done until it is rearmed)" % (tn, i), "scoreboard players set %s -1" % ta, "scoreboard players set %s -1" % tb,
                  "%spositioned %d %d %d run playsound minecraft:block.respawn_anchor.charge block @a[distance=..32] ~ ~ ~ 1.2 0.7" % (I, ax, ay, az)]
            if eff == "weak":
                ok += ["execute as %s at @s run function last_ember:contract/m/weaken {t:%d}" % (ME, dur * 20),
                       "tellraw @a[tag=le.cp_%s] %s" % (i, J(tx(t.get("text", "Его защита погасла."), "gold"))),
                       "execute as @a[gamemode=!spectator,gamemode=!creative] at @s %spositioned %d %d %d if entity @s[distance=..32] run tellraw @s %s" % (I.replace("execute ", ""), ax, ay, az, J(tx(t.get("text", "Его защита погасла."), "gold")))]
            elif eff == "open":
                ox1, oy1, oz1, ox2, oy2, oz2 = P3(t["open"]); ok += ["%srun fill %d %d %d %d %d %d minecraft:air" % (I, ox1, oy1, oz1, ox2, oy2, oz2)]
            if t.get("on"): ok.append("function " + t["on"])
            if eff == "weak": ok += ["schedule function last_ember:contract/gen/twin_rearm_%s_%s %ds replace" % (i, tn, dur)]
            w("twin_ok_%s_%s" % (i, tn), ok)
            w("twin_rearm_%s_%s" % (i, tn), ["# generated: the twins go out again (they can be lit again)", "scoreboard players set %s 0" % ta, "scoreboard players set %s 0" % tb, "%srun setblock %d %d %d %s" % (I, ax, ay, az, off), "%srun setblock %d %d %d %s" % (I, bx_, by_, bz_, off)])
        w("weak_tick_" + i, ["# generated: as the weakened monster of %s, every second" % i, "particle minecraft:smoke ~ ~1.5 ~ 0.6 0.8 0.6 0.02 12"])
    # --- the guard: the brood comes for the one who reads the clues
    if "guard" in c:
        mob, cnt = (c["guard"].split(":") + ["2"])[:2]
        gd = ["# generated: as a player reading the clues of %s: the brood comes from behind (cooldown 20 s, at most 4 alive)" % i, "scoreboard players set %s 20" % S(c, "g"),
              "execute store result score #brood le.ct if entity @e[tag=le.brood_%s]" % i, "execute if score #brood le.ct matches 4.. run return 0"]
        for k in range(int(cnt)):
            gd.append("execute rotated ~%d 0 positioned ^ ^ ^-9 positioned over motion_blocking run summon minecraft:%s ~ ~ ~ {Tags:[\"le.brood\",\"le.brood_%s\",\"le.noelite\",\"le.rolled\",\"le.eq_done\"]}" % (180 + (k * 50 - 25), mob, i))
        gd.append("playsound minecraft:entity.spider.ambient hostile @s ~ ~ ~ 1.2 1.4")
        w("guard_" + i, gd)
    # --- the drag: the monster takes one player to its lair, the other follows the blood
    if "drag" in c:
        dx, dy, dz = P3(c["drag"])
        hurt_p.append("execute if score #cid le.ct matches %d run function last_ember:contract/gen/drag_try_%s" % (n, i))
        w("drag_try_" + i, ["# generated: as the player hit by the monster of %s" % i, "execute if score %s matches 1.. run return 0" % S(c, "dr"),
                            "execute if score #online le.ct matches ..1 run return 0", "execute store result score #r le.ct run random value 1..3", "execute unless score #r le.ct matches 1 run return 0",
                            "scoreboard players set %s 40" % S(c, "dr"), "tag @s add le.dragged", "tag @s add le.drag_%s" % i,
                            "%srun summon minecraft:marker %d %d %d {Tags:[\"le.ctarget\"]}" % (I, dx, dy, dz), "scoreboard players set #steps le.ct 0",
                            "execute positioned ~ ~0.2 ~ facing %d %d %d run function last_ember:contract/m/trail_step" % (dx, dy, dz),
                            "tag @e[type=minecraft:marker,tag=le.ctrail_new] add le.ctrail_%s" % i, "tag @e[type=minecraft:marker,tag=le.ctrail_new] remove le.ctrail_new", "kill @e[type=minecraft:marker,tag=le.ctarget]",
                            "effect give @s minecraft:blindness 2 0 true", "effect give @s minecraft:slowness 30 1 true", "effect give @s minecraft:weakness 30 0 true",
                            "%srun tp @s %d %d %d" % (I, dx, dy, dz),
                            "execute as %s run %srun tp @s %d %d %d" % (ME, I, dx + 3, dy, dz),
                            "playsound minecraft:entity.player.hurt_sweet_berry_bush player @a ~ ~ ~ 1 0.5",
                            "title @s actionbar %s" % J(tx("Тебя утащило. Держись — тебя найдут по следу крови.", "dark_red")),
                            "tellraw @a[gamemode=!spectator,tag=!le.dragged] %s" % J(tx("Кого-то утащило! Присядь — по следу крови найдёшь.", "dark_red"))])
        sec.append("execute if score %s matches 1.. run scoreboard players remove %s 1" % (S(c, "dr"), S(c, "dr")))
        sec.append("execute as @a[tag=le.drag_%s] at @s run function last_ember:contract/gen/dragged_%s" % (i, i))
        w("dragged_" + i, ["# generated: as the dragged player of %s, every second: rescued when another player is within 4" % i,
                           "execute if entity @a[gamemode=!spectator,tag=!le.dragged,distance=..4] run return run function last_ember:contract/gen/rescued_%s" % i,
                           "execute if score %s matches ..10 run function last_ember:contract/gen/rescued_%s" % (S(c, "dr"), i)])
        w("rescued_" + i, ["# generated", "tag @s remove le.dragged", "tag @s remove le.drag_%s" % i, "effect clear @s minecraft:slowness", "effect clear @s minecraft:weakness",
                           "kill @e[type=minecraft:marker,tag=le.ctrail_%s]" % i, "title @s actionbar %s" % J(tx("Ты свободен", "gold"))])
    # --- admin
    w("reset_" + i, ["# generated: %s back to the start (the monster is removed; the participants lose their marks)" % i,
                     "execute as @e[tag=le.ct_%s] run function last_ember:contract/m/vanish" % i, "execute as @e[tag=le.ct_%s_sm] run function last_ember:contract/m/vanish" % i,
                     "kill @e[tag=le.brood_%s]" % i, "kill @e[type=minecraft:marker,tag=le.ctrail_%s]" % i]
      + ["scoreboard players set %s 0" % S(c, k) for k in ("s", "m", "w", "oa", "ob", "da", "db", "hf", "rs", "rt", "wk", "g", "cu", "wt", "dr", "sb")]
      + ["scoreboard players set %s 1" % S(c, k) for k in ("cl", "ca", "cb")]
      + (["scoreboard players set %s 1" % S(c, "da")] if c["split"] and not c["br"]["a"] else []) + (["scoreboard players set %s 1" % S(c, "db")] if c["split"] and not c["br"]["b"] else [])
      + ["tag @a remove le.cp_%s" % i, "tag @a remove le.cr_%s" % i, "tag @a remove le.drag_%s" % i,
         "data modify storage last_ember:contracts c.%s set value {s:0,n:0,got:0,parts:[],title:%s}" % (i, J(c["title"])),
         "function last_ember:contract/gen/set_%s" % i])
    stats.append("tellraw @s [%s,{\"score\":{\"name\":\"#%s_s\",\"objective\":\"le.ct\"}},%s,{\"score\":{\"name\":\"#%s_cl\",\"objective\":\"le.ct\"}},%s,{\"score\":{\"name\":\"#%s_m\",\"objective\":\"le.ct\"}}]"
                 % (J(tx(i + ": состояние ", "white")), i, J(tx(" улика ", "gray")), i, J(tx(" чудовище ", "gray")), i))

w("sec", sec); w("fast", fast); w("mt", mt + ["return 0"]); w("died", died); w("take", take); w("stats", stats); w("hurt_p", hurt_p)
for a in ("give", "reset", "spawn"):
    open(os.path.join(GEN, a + ".mcfunction"), "w").write("# generated: macro id\n" + ("$function last_ember:contract/gen/%s_$(id)\n" % a if a != "spawn" else
        "$execute in minecraft:overworld positioned as @s run function last_ember:contract/gen/spawn_$(id)\n"))
open(os.path.join(GEN, "state.mcfunction"), "w").write("# generated: macro id, s\n$scoreboard players set #$(id)_s le.ct $(s)\n$function last_ember:contract/gen/set_$(id)\n")
w("reset_all", ["# generated"] + ["function last_ember:contract/gen/reset_%s" % c["id"] for c in contracts.values()])

# ------------------------------------------------------------------ choices: clickable lines in the chat, the first who clicks decides for the party
cho = ["# generated: the trigger le.choice (code = choice*10 + option), as the player"]
for ch in choices.values():
    cid, n = ch["id"], ch["n"]; opts = [(k, ch[k]) for k in "abcd" if k in ch]
    of = ["# generated: offer the choice %s to every player in the game" % cid, "scoreboard players set #ch_%s le.ct 1" % cid, "scoreboard players enable @a le.choice",
          "tellraw @a[gamemode=!spectator] %s" % J(tx(ch["q"], "gold"))]
    for j, (k, t) in enumerate(opts, 1):
        of.append("tellraw @a[gamemode=!spectator] %s" % J({"text": "  [" + t + "]", "color": "aqua", "click_event": {"action": "run_command", "command": "/trigger le.choice set %d" % (n * 10 + j)},
                                                            "hover_event": {"action": "show_text", "value": tx("Выбрать", "gray")}}))
    if ch.get("final") == "1": of.append("tellraw @a[gamemode=!spectator] %s" % J(tx("Это нельзя будет изменить.", "dark_red", italic=True)))
    w("offer_" + cid, of)
    for j, (k, t) in enumerate(opts, 1):
        cho.append("execute if score #v le.ct matches %d if score #ch_%s le.ct matches 1 run function last_ember:contract/gen/chose_%s_%s" % (n * 10 + j, cid, cid, k))
        w("chose_%s_%s" % (cid, k), ["# generated: %s: the option %s is chosen (by the first who clicked)" % (cid, k), "scoreboard players set #ch_%s le.ct 2" % cid,
                                     "data modify storage last_ember:choices %s set value \"%s\"" % (cid, k),
                                     "tellraw @a[gamemode=!spectator] [{\"selector\":\"@s\",\"color\":\"white\"},%s]" % J(tx(" выбрал: " + t, "gold")),
                                     ("function " + ch["on_" + k]) if ch.get("on_" + k) else "# (the consequence: a hook for the region task: on_%s=<function>)" % k])
    init.append("execute unless score #ch_%s le.ct matches 0.. run scoreboard players set #ch_%s le.ct 0" % (cid, cid))
w("choice", cho); w("init", init)
open(os.path.join(GEN, "offer.mcfunction"), "w").write("# generated: macro id\n$function last_ember:contract/gen/offer_$(id)\n")
print("contracts: %d, boards: %d, clues: %d, rituals: %d, twins: %d, choices: %d, cells: %d" % (len(contracts), len(boards), len(clues), len(rituals), len(twins), len(choices), len(cells)))
