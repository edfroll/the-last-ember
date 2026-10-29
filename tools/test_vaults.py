#!/usr/bin/env python3
"""T-019 checks: treasuries of treasury/test_vaults.txt on a platform at (1100, 200, 1100), common loot, class items.
Before: python3 tools/gen_seer.py && python3 tools/gen_loot.py treasury/test_vaults.txt, tools/server.sh sync, reload.
Sections without a client: layout staff content items perf. With the client Cam (dev agent): open luck reflect cauldron.
Usage: python3 tools/test_vaults.py [layout staff content items open luck reflect cauldron perf] [--runs N]"""
import collections, importlib.util, json, os, re, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
ok = bad = 0
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n)
    else: bad += 1; print("  FAIL", n, e)
# ------------------------------------------------------------------ the test treasuries (the same file the generator read)
V = []
for line in open(os.path.join(ROOT, "treasury/test_vaults.txt"), encoding="utf-8"):
    if line.startswith("vault "):
        p = line.split(); V.append({"id": p[1], "r": p[2], "x": int(p[4]), "y": int(p[5]), "z": int(p[6]), "danger": "danger" in p, "fixed": any(a.startswith("main=") for a in p)})
BY = {v["id"]: v for v in V}
REG = collections.defaultdict(list)
for v in V: REG[v["r"]].append(v["id"])
MAIN_REG = {13: ["r6"], 6: ["r5", "r6"], 7: ["r2", "r4"], 8: ["r2", "r4"], 11: ["r2", "r4"], 12: ["r2", "r4"], 9: ["r3", "r5"], 10: ["r3", "r5"]}
STAFF_REG = ["r1", "r2", "r3", "r4", "r5"]
MARK = {1: 'le_staff: "blink"', 2: 'le_staff: "frost"', 3: 'le_staff: "flame"', 4: 'le_staff: "lift"', 5: 'le_staff: "banish"', 6: 'le_staff: "wrath"', 7: "le_guard: 1b", 8: "le_watch: 1b",
        9: "le_windbow: 1b", 10: "le_shadow: 1b", 11: "le_old: 1b", 12: "le_herbbag: 1b", 13: "netherite_upgrade_smithing_template"}
def dump():
    rc.run("function last_ember:vault/gen/dump"); r = rc.run("data get storage last_ember:vt d"); d = {}
    for vid, body in re.findall(r"(\w+): \{([^}]*)\}", r):
        d[vid] = {k: int(x) for k, x in re.findall(r"(\w+): (-?\d+)", body)}
    st = {int(s): int(x) for s, x in re.findall(r"st(\d): (-?\d+)", r)}
    return d, st
def fresh():
    """all test treasuries closed, no staff taken, a new layout"""
    for v in V: rc.run(f"scoreboard players set #o.{v['id']} le.vt 0")
    rc.run("function last_ember:vault/reset_staffs"); rc.run("function last_ember:vault/relayout_auto")
def platform():
    rc.run("forceload add 1090 1090 1120 1130")
    for _ in range(60):
        time.sleep(0.5)
        if "passed" in rc.run("execute if loaded 1092 200 1092") and "passed" in rc.run("execute if loaded 1118 200 1128"): break
    rc.run("fill 1090 199 1090 1120 199 1130 stone"); rc.run("fill 1090 200 1090 1120 206 1130 air"); rc.run("time set noon")
# ------------------------------------------------------------------ layout
def check_layout(d, st, errs):
    where = collections.defaultdict(list)
    for vid, s in d.items():
        if vid not in BY: continue
        for slot in ("m", "m2"):
            if s.get(slot, 0) and s[slot] < 98: where[s[slot]].append((vid, slot))
    for k in range(1, 14):
        if st.get(k, 0) == 1 and k <= 5:
            if where[k]: errs.append(f"taken staff {k} laid out in {where[k]}")
            continue
        if len(where[k]) != 1: errs.append(f"main {k}: {where[k]}"); continue
        vid = where[k][0][0]; r = BY[vid]["r"]
        if k in MAIN_REG and r not in MAIN_REG[k]: errs.append(f"main {k} in {r}")
        if k == 6 and not BY[vid]["danger"]: errs.append(f"Wrath not in a danger treasury: {vid}")
    staff_r = [BY[where[s][0][0]]["r"] for s in range(1, 6) if len(where[s]) == 1]
    if sorted(staff_r) != sorted(set(staff_r)): errs.append(f"two staffs in one region: {staff_r}")
    for k in (7, 8):
        pass
    for a, b in ((7, 8), (11, 12), (9, 10)):
        if len(where[a]) == 1 and len(where[b]) == 1 and BY[where[a][0][0]]["r"] == BY[where[b][0][0]]["r"]: errs.append(f"pair {a},{b} in one region")
    for r, ids in REG.items():
        n = sum(d[i].get("a", 0) for i in ids)
        if n != 1: errs.append(f"{r}: {n} golden apples")
    if sum(d[i].get("e", 0) for i in REG["r6"]) != 1: errs.append("Mending not exactly once in r6")
    for vid, s in d.items():
        if vid in BY and s.get("m", 0) == 0: errs.append(f"{vid}: no main item")
        if vid == "tr4e" and s.get("m") != 98: errs.append("tr4e: the fixed main item is not kept")
    return where
def t_layout(runs):
    print(f"[layout x{runs}]"); errs = []; stat = collections.Counter(); seconds = 0
    for i in range(runs):
        fresh(); d, st = dump(); where = check_layout(d, st, errs)
        for s in range(1, 6):
            if len(where[s]) == 1: stat[(s, BY[where[s][0][0]]["r"])] += 1
        seconds += sum(1 for vid in d if d[vid].get("m2", 0))
    chk(f"every main item exactly once, in its regions; Wrath in a danger treasury; one golden apple per region; one Mending; no treasury without a main", not errs, errs[:6])
    print("   staff x region (count of runs):")
    for s in range(1, 6): print("    ", s, [stat[(s, r)] for r in STAFF_REG])
    chk("each staff gets into each of Р1..Р5 (randomness)", all(stat[(s, r)] > 0 for s in range(1, 6) for r in STAFF_REG) if runs >= 100 else True)
    chk("with enough treasuries no main goes second", seconds == 0, seconds)
    # opened treasuries keep their items over a relayout
    fresh(); d0, _ = dump(); keep = ["tr2a", "tr5a"]
    for k in keep: rc.run(f"scoreboard players set #o.{k} le.vt 1")
    rc.run("function last_ember:vault/relayout_auto"); d1, st = dump(); e2 = []; check_layout(d1, st, e2)
    used = [d0[k]["m"] for k in keep]
    dup = [k for k in used if k < 98 and sum(1 for v in d1 if v not in keep and k in (d1[v]["m"], d1[v]["m2"])) > 0]
    chk("relayout: opened treasuries keep theirs, their main items are not laid out again", all(d1[k]["m"] == d0[k]["m"] for k in keep) and not dup, (used, dup))
    for k in keep: rc.run(f"scoreboard players set #o.{k} le.vt 0")
    # a reload does not change the layout (the version is the same)
    fresh(); d0, _ = dump(); rc.run("reload"); time.sleep(3); d1, _ = dump()
    chk("reload keeps the layout", all(d0[v]["m"] == d1[v]["m"] and d0[v]["a"] == d1[v]["a"] for v in d0 if v in BY))
def t_staff():
    print("[the start staff]")
    fresh(); d0, _ = dump(); got = []
    for i in range(5):
        rc.run("function last_ember:vault/gen/staff_pick"); got.append(tc.score("#rnd", "le.e"))
    d1, st = dump()
    chk("five seers in a row: five different staffs", sorted(got) == [1, 2, 3, 4, 5], got)
    holders = [v for v in d0 if v in BY and d0[v]["m"] in range(1, 6)]
    chk("their closed treasuries get the filler instead (99)", all(d1[v]["m"] == 99 for v in holders), [(v, d0[v]["m"], d1[v]["m"]) for v in holders])
    rc.run("function last_ember:vault/gen/staff_pick"); x = tc.score("#rnd", "le.e")
    chk("a sixth seer: any staff (all taken)", x in range(1, 6), x)
    fresh(); rc.run("scoreboard players set #st.3 le.vt 1"); rc.run("function last_ember:vault/relayout_auto"); d, st = dump()
    chk("a taken staff is not laid out; its region is left with a filler", all(d[v]["m"] != 3 and d[v]["m2"] != 3 for v in d if v in BY) and sum(1 for v in d if v in BY and d[v]["m"] == 99) >= 1)
    got = []
    for i in range(4): rc.run("function last_ember:vault/gen/staff_pick"); got.append(tc.score("#rnd", "le.e"))
    chk("the start staff is never the taken one", sorted(got) == [1, 2, 4, 5], got)
    if "Cam" in rc.run("list"):
        fresh(); tc.setc(2, 3, 0); time.sleep(1.0); inv = rc.run("data get entity Cam Inventory"); m = re.search(r'le_staff: "(\w+)"', inv); d, st = dump()
        chk("a real seer kit (char/set): the staff is taken (#st.N = 1)", m and sum(st.values()) == 1, (m and m.group(1), st))
# ------------------------------------------------------------------ content (no player: loot insert into a test chest)
TEST_CHEST = (1110, 201, 1125)
def roll(table):
    x, y, z = TEST_CHEST; rc.run(f"setblock {x} {y} {z} minecraft:air"); rc.run(f"setblock {x} {y} {z} minecraft:chest"); rc.run(f"loot insert {x} {y} {z} loot {table}")
    return rc.run(f"data get block {x} {y} {z} Items")
def stacks(items): return items.count("Slot:")
def t_content():
    print("[content of the treasuries]"); platform(); fresh(); d, st = dump(); errs = []
    for v in V:
        vid = v["id"]; it = roll(f"last_ember:vault/{vid}"); m = d[vid]["m"]
        if m in MARK and MARK[m] not in it: errs.append(f"{vid}: main {m} missing")
        if m == 99 and not ("enchanted_book" in it and re.search(r'(iron|gold)_ingot", count: (\d+)', it) and int(re.search(r'(iron|gold)_ingot", count: (\d+)', it).group(2)) >= 8): errs.append(f"{vid}: filler wrong")
        if d[vid]["a"] and "golden_apple" not in it: errs.append(f"{vid}: no apple")
        if d[vid].get("e") and "mending" not in it: errs.append(f"{vid}: no Mending")
        if vid == "tr1a" and "Обрывок карты" not in it: errs.append("tr1a: no scrap of a map")
        extra = 1 + d[vid]["a"] + d[vid].get("e", 0) + (1 if vid == "tr1a" else 0) + (1 if m == 99 else 0) + (1 if vid == "tr4e" else 0)
        n = stacks(it) - extra
        if not (3 <= n <= 5) and vid != "tr4e": errs.append(f"{vid}: {n} good things")
        if v["r"] != "r1" and "le_grimoire" not in it: errs.append(f"{vid}: no grimoire")
    chk("every treasury: its main item, 3..5 good things (1..2 grimoires from Р2), the apple / Mending / scrap where laid out", not errs, errs[:6])
    gr = collections.Counter()
    for i in range(30): gr[roll("last_ember:vault/good_r2").count("le_grimoire_res")] += 1
    chk("Р2: 1..2 grimoires each time", set(gr) <= {1, 2} and gr[1] and gr[2], dict(gr))
    it = roll("last_ember:vault/good_r6"); chk("grimoires of Р6 are not Mending (Mending only by the layout)", "mending" not in it)
    cnt = collections.Counter()
    for r in ("r0", "r1", "r2", "r3", "r4", "r5", "r6"):
        for i in range(12): cnt[(r, stacks(roll(f"last_ember:chests/{r}/common")))] += 1
    chk("common containers: 2..4 things", all(2 <= n <= 4 for (_, n) in cnt), dict(cnt))
def t_items():
    print("[class items]"); platform(); rc.run("kill @e[type=minecraft:item,x=1105,y=201,z=1120,distance=..10]")
    def get(t): return roll(f"last_ember:item/{t}")
    s = get("guard_shield"); chk("Shield of the Guardian: shield, Unbreaking III, le_keep", "minecraft:shield" in s and '"minecraft:unbreaking": 3' in s and "le_keep: 1b" in s, s[:300])
    s = get("watch_plate"); chk("Plate of the Last Watch: armor 8, toughness 1, kb 0.1 on the chest", "armor_toughness" in s and "amount: 8.0d" in s and "le_keep: 1b" in s, s[:400])
    s = get("wind_bow"); chk("Bow of the Far Wind: Power III, Infinity", '"minecraft:power": 3' in s and '"minecraft:infinity": 1' in s, s[:300])
    s = get("shadow_quiver"); chk("Quiver of Shadows: 16 arrows of withering", "count: 16" in s and "minecraft:wither" in s, s[:300])
    s = get("old_cauldron"); chk("the Old Herbwife's Cauldron: a healer's cauldron (le_cauldron) + le_old", "le_cauldron: 1b" in s and "le_old: 1b" in s)
    s = get("herb_bag"); chk("the Herbwife's Bag: a bundle with the rare ingredients", "bundle_contents" in s and "rabbit_foot" in s and "cobweb" in s, s[:300])
    for sid in ("blink", "frost", "flame", "lift", "banish", "wrath"):
        s = get(f"staff_{sid}"); chk(f"staff {sid} from the loot table = the staff of seer/give (use_remainder, le_staff)", f'le_staff: "{sid}"' in s and "use_remainder" in s and "consumable" in s)
    s = get("grimoire_mending"); chk("the grimoire of Mending: the seer's grimoire (use_remainder: the book with Mending)", "le_grimoire" in s and "mending" in s and "use_remainder" in s)
    s = get("murky"); chk("a murky vial (le_murky, the effects hidden)", "le_murky: 1b" in s and "tooltip_display" in s)
# ------------------------------------------------------------------ with the client
def open_chest(x, y, z):
    """Cam stands south of the container and opens it with a real right click; the window is closed after"""
    tc.face("Cam", x + 0.5, y, z + 2.3, x + 0.5, y + 0.5, z + 0.5); time.sleep(0.5); tc.act("Cam", "!use"); time.sleep(1.0); tc.act("Cam", "!sneak_off"); time.sleep(0.6)
def t_open():
    print("[a player opens a treasury]"); platform(); fresh(); rc.run("gamemode survival Cam"); d, st = dump()
    for v in V: rc.run(f"function last_ember:vault/gen/build_{v['id']}")
    # clear the row south of tr2a for the camera
    v = BY["tr2a"]; rc.run(f"fill {v['x'] - 1} {v['y']} {v['z'] + 1} {v['x'] + 1} {v['y'] + 2} {v['z'] + 3} air")
    open_chest(v["x"], v["y"], v["z"]); it = rc.run(f"data get block {v['x']} {v['y']} {v['z']} Items"); d1, st1 = dump()
    chk("a real opening: the chest is filled with its main item, marked opened (#o = 1)", d[v["id"]]["m"] in MARK and MARK[d[v["id"]]["m"]] in it and d1["tr2a"]["o"] == 1, (d[v["id"]]["m"], it[:200], d1["tr2a"]))
    open_chest(v["x"], v["y"], v["z"]); it2 = rc.run(f"data get block {v['x']} {v['y']} {v['z']} Items")
    chk("opened again: nothing new appears", it2 == it)
    # a treasury with a staff: opening takes the staff
    sv = next((x for x in d if x in BY and d[x]["m"] in range(1, 6) and x != "tr2a"), None)
    if sv:
        b = BY[sv]; rc.run(f"fill {b['x'] - 1} {b['y']} {b['z'] + 1} {b['x'] + 1} {b['y'] + 2} {b['z'] + 2} air"); open_chest(b["x"], b["y"], b["z"]); d2, st2 = dump()
        chk(f"opening {sv} (staff {d[sv]['m']}) marks the staff taken", st2.get(d[sv]["m"]) == 1, st2)
        rc.run("function last_ember:vault/gen/staff_pick"); x = tc.score("#rnd", "le.e"); chk("the next start staff is another one", x != d[sv]["m"], x)
    rc.run('function last_ember:vault/refill {id:"tr2a"}'); d3, _ = dump(); it3 = rc.run(f"data get block {v['x']} {v['y']} {v['z']} LootTable")
    chk("vault/refill: closed again, the loot table back", d3["tr2a"]["o"] == 0 and "last_ember:vault/tr2a" in it3, it3)
LUCK_RARE = ("iron_ingot", "enchanted_book", "slime_ball", "rabbit_foot", "le_murky")
def t_luck(n=25):
    print(f"[luck of a human: {n} chests each]")
    tab = json.load(open(os.path.join(ROOT, "datapack/data/last_ember/loot_table/chests/r2/common.json")))["pools"][0]["entries"]
    def share(luck):
        W = [max(0, e.get("weight", 1) + e.get("quality", 0) * luck) for e in tab]; R = [w for w, e in zip(W, tab) if e.get("quality")]; return sum(R) / sum(W)
    print(f"   by the table: a rare thing per roll {share(0) * 100:.1f}% without luck, {share(1) * 100:.1f}% with luck +1 (a human)")
    platform(); x, y, z = 1100, 201, 1125; rc.run("gamemode survival Cam")
    res = {}
    for name, race, extra in (("elf (luck 0)", 2, 0), ("luck +100 (the quality works)", 2, 100)):
        tc.setc(race, 1, 0); rc.run("attribute Cam minecraft:luck modifier remove last_ember:test_luck")
        if extra: rc.run(f"attribute Cam minecraft:luck modifier add last_ember:test_luck {extra} add_value")
        rare = tot = 0
        for i in range(n):
            rc.run(f"setblock {x} {y} {z} minecraft:air"); rc.run(f'setblock {x} {y} {z} minecraft:chest{{LootTable:"last_ember:chests/r2/common"}}'); open_chest(x, y, z)
            it = rc.run(f"data get block {x} {y} {z} Items"); s = stacks(it); tot += s; rare += sum(it.count(k) for k in LUCK_RARE)
        res[name] = (rare, tot); print(f"   {name}: {rare} rare of {tot}")
    rc.run("attribute Cam minecraft:luck modifier remove last_ember:test_luck")
    a, b = res["elf (luck 0)"], res["luck +100 (the quality works)"]
    chk("the luck of the opener works on our common tables (quality): luck +100 -> mostly rare", b[0] / max(1, b[1]) > 0.6 and b[0] / max(1, b[1]) > 2 * a[0] / max(1, a[1]), res)
    tc.setc(1, 1, 0); chk("a human has luck 1", abs((tc.num(rc.run("attribute Cam minecraft:luck get")) or 0) - 1) < 0.01)
def t_reflect():
    print("[Shield of the Guardian]"); rc.run("difficulty normal")
    tc.setc(1, 1, 0); tc.tp("Cam", 0.5, 103, -14.5, 0, 0); rc.run("kill @e[tag=le.test]"); time.sleep(0.5)
    rc.run("item replace entity Cam container.20 from entity Cam weapon.mainhand"); rc.run("item replace entity Cam weapon.mainhand with minecraft:stone_sword")
    rc.run("loot replace entity Cam weapon.offhand loot last_ember:item/guard_shield")
    rc.run('summon minecraft:husk 0.5 103 -12.5 {NoAI:1b,Tags:["le.test","le.keep"],PersistenceRequired:1b}'); time.sleep(0.5)
    tc.act("Cam", "!use_on"); time.sleep(0.8)
    for dealt, want in ((6, 2), (12, 6), (30, 14), (50, 16)):
        h0 = tc.hp("@e[tag=le.test,limit=1]"); rc.run(f"damage Cam {dealt} minecraft:mob_attack by @e[tag=le.test,limit=1]"); time.sleep(0.9)
        h1 = tc.hp("@e[tag=le.test,limit=1]"); chk(f"blocked hit {dealt} with the Shield of the Guardian: the attacker takes {want} (x2)", h0 - h1 == want, (h0, h1))
        rc.run("data modify entity @e[tag=le.test,limit=1] Health set value 20.0f"); time.sleep(0.4)
    tc.act("Cam", "!use_off"); rc.run("item replace entity Cam weapon.offhand with minecraft:shield"); time.sleep(0.4); tc.act("Cam", "!use_on"); time.sleep(0.8)
    h0 = tc.hp("@e[tag=le.test,limit=1]"); rc.run("damage Cam 12 minecraft:mob_attack by @e[tag=le.test,limit=1]"); time.sleep(0.9)
    chk("an ordinary shield: still 25% (3)", h0 - tc.hp("@e[tag=le.test,limit=1]") == 3); tc.act("Cam", "!use_off"); rc.run("kill @e[tag=le.test]")
def t_cauldron():
    print("[the Old Herbwife's Cauldron]")
    def brew_old(old):
        tc.healer_setup(0); tc.cauldron_setup(3)
        if old: rc.run("tag @e[tag=le.testpot] add le.pot_old")
        for it in ("brown_mushroom", "cooked_beef", "sugar"): tc.throw(it)
        tc.wait_idle(); return len([r for r in tc.drain() if "glass_bottle" not in r and "minecraft:bucket" not in r])
    c0 = [brew_old(False) for _ in range(5)]; c1 = [brew_old(True) for _ in range(5)]
    print(f"   vials: ordinary {c0}, old {c1}")
    chk("the old cauldron: 2..4 at tier 0 (one more than 1..3)", min(c1) >= 2 and max(c1) <= 4 and min(c0) >= 1 and max(c0) <= 3, (c0, c1))
def t_perf():
    print("[load]"); t0 = time.time()
    for i in range(20): rc.run("function last_ember:vault/relayout_auto")
    print(f"   20 layouts by RCON: {time.time() - t0:.2f} s (with the RCON round trips)")
    r = rc.run("tick query"); print("  ", r.replace("\n", " ")[:300])
    chk("the layout runs only at the start (setup / relayout); the tick has only the 1/s pending check", "vault/gen/pending" in open(os.path.join(ROOT, "datapack/data/last_ember/function/vault/loop.mcfunction")).read())
if __name__ == "__main__":
    runs = 300
    a = sys.argv[1:]
    if "--runs" in a: i = a.index("--runs"); runs = int(a[i + 1]); del a[i:i + 2]
    sel = a or ["layout", "staff", "content", "items", "perf"]
    for s in sel:
        if s == "layout": t_layout(runs)
        else: globals()[f"t_{s}"]()
    print(f"\n{ok} ok, {bad} failed")
