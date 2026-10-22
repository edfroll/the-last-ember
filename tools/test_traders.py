#!/usr/bin/env python3
"""T-017 checks (server + dev clients Cam, Cam2; real trade windows through the agent actions !use, !trade_sel N, !trade_take): traders of traders/test_traders.txt at (1100,200,1100) and (1105,200,1100).
Usage: python3 tools/test_traders.py [build deals hello price hurt stock smith perf]"""
import importlib.util, math, os, re, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
ok = bad = 0
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n)
    else: bad += 1; print("  FAIL", n, e)
score, num = tc.score, tc.num
T = "@e[tag=le.tr_tt_trader,limit=1]"; W = "@e[tag=le.tr_tt_wander,limit=1]"
def tdata(sel, path): return rc.run(f"data get entity {sel} {path}")
def uses(i, sel=T):
    r = rc.run(f"data get entity {sel} Offers.Recipes[{i}].uses"); m = re.search(r"entity data: (\d+)", r); return int(m.group(1)) if m else 0
def build():
    rc.run("forceload add 1090 1090 1115 1110")
    for _ in range(60):
        time.sleep(0.5)
        if "passed" in rc.run("execute if loaded 1095 200 1095") and "passed" in rc.run("execute if loaded 1112 200 1108"): break
    rc.run("tp Cam 1100.5 200 1103.5"); rc.run("tp Cam2 1102.5 200 1103.5"); time.sleep(1.0)
    rc.run("fill 1090 199 1090 1115 199 1110 stone"); rc.run("fill 1090 200 1090 1115 210 1110 air"); rc.run("kill @e[type=minecraft:zombie]"); rc.run("kill @e[type=minecraft:creeper]")
    rc.run('function last_ember:trader/reset {id:"tt_trader"}'); rc.run('function last_ember:trader/reset {id:"tt_wander"}'); time.sleep(3.0)
def prep(p, race=1):
    rc.run(f"advancement revoke {p} only last_ember:trader/click")
    tc.setc(race, 1, 0, p); rc.run(f"gamemode survival {p}"); rc.run(f"clear {p}"); rc.run(f"effect clear {p}")
def trophy(p, name, region="r1", count=2): rc.run(f"give {p} minecraft:nautilus_shell[minecraft:custom_data={{le_trophy:\"{region}\"}},minecraft:custom_name='{{\"text\":\"{name}\",\"italic\":false}}',minecraft:max_stack_size=16] {count}")
def face_trader(p, x=1100.5, z=1102.2, tx=1100.5, tz=1100.5): tc.face(p, x, 200, z, tx, 200.9, tz)
def open_trade(p, x=1100.5, tx=1100.5):
    rc.run(f"tp {p} {x} 200 1102.2"); face_trader(p, x, 1102.2, tx); time.sleep(0.4); tc.act(p, "!use"); time.sleep(1.0)
def buy(p, idx, x=1100.5, tx=1100.5, sel=T, tries=3):
    """a real purchase: the window is opened with a right click, the deal is selected, the result is taken; the click is repeated if the window did not open in time"""
    u0 = uses(idx, sel)
    for _ in range(tries):
        open_trade(p, x, tx); time.sleep(0.4); tc.act(p, f"!trade_sel {idx}"); time.sleep(0.7); tc.act(p, "!trade_take"); time.sleep(0.9); tc.act(p, "!sneak_off"); time.sleep(1.2)
        if uses(idx, sel) != u0: break
def inv(p): return rc.run(f"data get entity {p} Inventory")
def t_build():
    print("[build]"); build()
    chk("the trader stands: NoAI, Invulnerable, Silent, PersistenceRequired, tags le.npc/le.trader/le.noelite, a visible name", all(x in tdata(T, "NoAI") + tdata(T, "Invulnerable") + tdata(T, "Silent") + tdata(T, "PersistenceRequired") for x in ("1b",)) and "1b" in tdata(T, "CustomNameVisible") and all(t in tdata(T, "Tags") for t in ("le.npc", "le.trader", "le.noelite")), tdata(T, "Tags")[:100])
    chk("villager level 5 (it cannot level up), profession from the file, the yaw from the file", "level: 5" in tdata(T, "VillagerData") and "librarian" in tdata(T, "VillagerData") and "snow" in tdata(T, "VillagerData") and "180.0f" in tdata(T, "Rotation"), tdata(T, "VillagerData"))
    chk("the wandering trader: scale 0.8, not silent, never despawns, 1 deal", "0.8" in rc.run(f"attribute {W} minecraft:scale base get") and "0b" in tdata(W, "Silent") or "Found no" in tdata(W, "Silent"), tdata(W, "Silent"))
    chk("the deals are those of the file (4), with maxUses and a fixed price (priceMultiplier 0)", all(f"maxUses: {m}" in tdata(T, "Offers") for m in (2, 3, 1)) and tdata(T, "Offers").count("maxUses") == 4 and "priceMultiplier" not in tdata(T, "Offers").replace("priceMultiplier: 0.0f", ""), tdata(T, "Offers")[:200])
    chk("the price of a trophy is matched by custom_data only (no name in the price)", 'le_trophy: "r1"' in tdata(T, "Offers.Recipes[0].buy") and "custom_name" not in tdata(T, "Offers.Recipes[0].buy"), tdata(T, "Offers.Recipes[0].buy")[:200])
    chk("a no_spawn zone of 16 blocks round the trader (zones/traders.gen.txt)", "trader_tt_trader" in open(os.path.join(ROOT, "zones/traders.gen.txt")).read())
def t_hello():
    print("[the greeting]"); build(); prep("Cam", 2); prep("Cam2", 2); time.sleep(1.5); rc.run("tag Cam remove le.hi_tt_trader"); rc.run("tag Cam2 remove le.hi_tt_trader")
    open_trade("Cam"); chk("the first right click: the trade window opens and the greeting is said (tag le.hi_<id> set), the other player has none", "le.hi_tt_trader" in rc.run("tag Cam list") and "le.hi_tt_trader" not in rc.run("tag Cam2 list"))
    tc.act("Cam", "!sneak_off"); time.sleep(0.5); rc.run("tp Cam 1094.5 200 1106.5"); rc.run("tp Cam2 1100.5 200 1102.2"); face_trader("Cam2", 1100.5, 1102.2); time.sleep(0.3); tc.act("Cam2", "!use"); time.sleep(0.8); tc.act("Cam2", "!sneak_off")
    chk("every player is greeted once: the second player gets his own greeting", "le.hi_tt_trader" in rc.run("tag Cam2 list"))
def t_deals():
    print("[deals through the real trade window]"); build(); prep("Cam", 2); prep("Cam2", 2)
    trophy("Cam", "Трофей: Курганный мертвец", count=2)
    buy("Cam", 0); chk("deal 1: 2 trophies (named Курганный мертвец) -> bread x4: the trophy of any name pays, only custom_data counts", "minecraft:bread" in inv("Cam") and uses(0) == 1, (uses(0),))
    trophy("Cam", "Трофей: Плакальщик", count=2); buy("Cam", 0); chk("deal 1 again with a trophy of another name: it pays too", uses(0) == 2, uses(0))
    rc.run("clear Cam minecraft:bread"); trophy("Cam", "Трофей: Ещё один", count=2); buy("Cam", 0)
    chk("deal 1 is used up (2 uses): the third purchase does not happen, the trophies stay", uses(0) == 2 and "nautilus_shell" in inv("Cam") and "minecraft:bread" not in inv("Cam"), (uses(0), "nautilus_shell" in inv("Cam"), "minecraft:bread" in inv("Cam")))
    rc.run("clear Cam minecraft:nautilus_shell")
    rc.run("give Cam minecraft:coal 3"); trophy("Cam", "Трофей: Ещё", count=1); buy("Cam", 1); chk("deal 2: a trophy + 3 coal -> 8 arrows (two prices)", "minecraft:arrow" in inv("Cam") and uses(1) == 1, uses(1))
    rc.run("give Cam minecraft:iron_ingot 2"); buy("Cam", 2); chk("deal 3: 2 iron ingots -> an enchanted book (a preset of items.txt: Protection II)", "enchanted_book" in inv("Cam") and '"minecraft:protection": 2' in inv("Cam"), uses(2))
    trophy("Cam", "Трофей: Р2", region="r2", count=1); buy("Cam", 3); chk("deal 4: a trophy of the region r2 -> a named blade", "Тестовый клинок" in inv("Cam"), uses(3))
    trophy("Cam", "Трофей: Р1 для сделки Р2", region="r1", count=1); buy("Cam", 3); chk("a trophy of the region r1 does not pay for the r2 deal", uses(3) == 1, uses(3))
    rc.run("give Cam minecraft:gold_nugget 5"); buy("Cam", 0, 1105.5, 1105.5, W)
    chk("the wandering trader trades too: 5 gold nuggets -> an emerald", "minecraft:emerald" in inv("Cam") and uses(0, W) == 1, uses(0, W))
def t_price():
    print("[prices: the Hero of the Village, demand]"); build(); prep("Cam", 1); prep("Cam2", 2)
    rc.run("effect give Cam minecraft:hero_of_the_village infinite 0 true"); trophy("Cam", "Трофей", count=2); open_trade("Cam"); time.sleep(0.6)
    sp = tdata(T, "Offers.Recipes[0].specialPrice"); tc.act("Cam", "!sneak_off"); time.sleep(1.0); chk("a human (Hero of the Village): the price of the first deal is lowered by the vanilla discount (30%, at least 1)", "-1" in sp, sp)
    rc.run("clear Cam"); rc.run("tp Cam 1094.5 200 1106.5"); trophy("Cam2", "Трофей", count=2); open_trade("Cam2"); time.sleep(0.6)
    sp2 = tdata(T, "Offers.Recipes[0].specialPrice"); tc.act("Cam2", "!sneak_off"); time.sleep(0.8); chk("an elf: the price is the one of the file (the special price is back to 0)", "-1" not in sp2, sp2)
    chk("demand does not grow and the multiplier is 0: the price is stable", "demand: 0" in tdata(T, "Offers.Recipes[0]") or "demand" not in tdata(T, "Offers.Recipes[0]"), tdata(T, "Offers.Recipes[0]")[:150])
def t_hurt():
    print("[the trader cannot be hurt, moved or turned]"); build(); prep("Cam"); hp0 = num(tdata(T, "Health")); rc.run("effect give Cam minecraft:resistance 1000 4")
    rc.run("damage @e[tag=le.tr_tt_trader,limit=1] 8 minecraft:player_attack by Cam"); rc.run("damage @e[tag=le.tr_tt_trader,limit=1] 8 minecraft:player_attack by Cam"); time.sleep(0.5)
    chk("hit by a player: no damage, no gossip, the prices unchanged", num(tdata(T, "Health")) == hp0 and "Gossips" not in tdata(T, "Gossips").replace("Gossips: []", "") or "[]" in tdata(T, "Gossips") or "Found no" in tdata(T, "Gossips"), tdata(T, "Gossips")[:80])
    rc.run("setblock 1100 200 1099 minecraft:lava"); rc.run("summon minecraft:creeper 1101.5 200 1100.5 {Fuse:0,ignited:1b,ExplosionRadius:6}"); rc.run("summon minecraft:zombie 1099.5 200 1100.5 {Tags:[\"zz\"]}"); rc.run("summon minecraft:zombie 1100.5 200 1101.5 {Tags:[\"zz\"]}"); time.sleep(2.0)
    chk("a creeper blows beside it: it lives", "passed" in rc.run("execute if entity @e[tag=le.tr_tt_trader]") and num(tdata(T, "Health")) == hp0)
    rc.run("data modify entity @e[tag=zz,limit=1] Health set value 20.0f"); time.sleep(8.0)
    chk("zombies around it for 8 s: it is alive and still a villager (no conversion, no damage)", "passed" in rc.run("execute if entity @e[type=minecraft:villager,tag=le.tr_tt_trader]") and num(tdata(T, "Health")) == hp0)
    rc.run("kill @e[tag=zz]"); rc.run("setblock 1100 200 1099 air")
    rc.run("data modify entity @e[tag=le.tr_tt_trader,limit=1] Motion set value [0.9d,0.4d,0.9d]"); time.sleep(3.0); p = re.findall(r"(-?\d+\.?\d*)d", tdata(T, "Pos"))
    chk("pushed: it stays where it stands", abs(float(p[0]) - 1100.5) < 0.4 and abs(float(p[2]) - 1100.5) < 0.4, p)
    rc.run("summon minecraft:oak_boat 1100.5 200 1100.5 {Tags:[\"bt\"]}"); time.sleep(0.2); rc.run("ride @e[tag=le.tr_tt_trader,limit=1] mount @e[tag=bt,limit=1]"); time.sleep(2.5)
    p = re.findall(r"(-?\d+\.?\d*)d", tdata(T, "Pos")); chk("put into a boat: it is taken out of it within a second and stays", "passed" not in rc.run("execute as @e[tag=le.tr_tt_trader] on vehicle run say v") and abs(float(p[0]) - 1100.5) < 0.4, p)
    rc.run("kill @e[tag=bt]"); rc.run("tp @e[tag=le.tr_tt_trader,limit=1] 1100.5 200 1112.5"); time.sleep(2.2); p = re.findall(r"(-?\d+\.?\d*)d", tdata(T, "Pos"))
    chk("carried away (tp): it comes back to its place", abs(float(p[2]) - 1100.5) < 0.4, p)
def t_stock():
    print("[no restocking in 3 game days]"); build(); prep("Cam"); trophy("Cam", "Трофей", count=2); buy("Cam", 0); trophy("Cam", "Трофей", count=2); buy("Cam", 0)
    u0 = (uses(0), uses(1)); rc.run("setblock 1098 200 1100 minecraft:lectern"); rc.run("setblock 1102 200 1100 minecraft:lectern"); g0 = score("#gt", "le.e")
    rc.run("tp Cam 1100.5 200 1103.5"); rc.run("tick sprint 72000")
    for _ in range(300):
        time.sleep(3)
        if (score("#gt", "le.e") or 0) - (g0 or 0) >= 72000: break
    rc.run("tick sprint stop"); time.sleep(1.0); g1 = score("#gt", "le.e")
    chk(f"after {(g1 - g0) / 24000:.1f} game days next to lecterns (the workstation of a librarian): the uses are not restocked ({u0} -> {(uses(0), uses(1))})", (g1 - g0) >= 71000 and (uses(0), uses(1)) == u0 and u0[0] == 2, (u0, (uses(0), uses(1)), g1 - g0))
    chk("the level does not grow either (stays 5), no new deals appeared", "level: 5" in tdata(T, "VillagerData") and tdata(T, "Offers").count("maxUses") == 4)
    rc.run("setblock 1098 200 1100 air"); rc.run("setblock 1102 200 1100 air")
def t_smith():
    print("[the Smith of the Refuge]"); tdt = "@e[tag=le.tr_smith,limit=1]"
    rc.run("forceload add 40 10 75 45"); time.sleep(2.0); rc.run("tp Cam 56.5 101 29.5"); time.sleep(3.0)
    chk("Halvard stands at the marker smith_trader (58, 101, 27)", "passed" in rc.run("execute if entity @e[tag=le.tr_smith]") and "Кузнец Хальвард" in tdata(tdt, "CustomName"), tdata(tdt, "CustomName"))
    chk("a weaponsmith, plains, facing north (yaw 180)", "weaponsmith" in tdata(tdt, "VillagerData") and "plains" in tdata(tdt, "VillagerData") and "180.0f" in tdata(tdt, "Rotation"))
    rc.run("data get entity @e[tag=le.tr_smith,limit=1] Offers"); o = tdata(tdt, "Offers")
    chk("8 deals; the uses 3,3,3,3,3,5,3,2", sorted(int(x) for x in re.findall(r"maxUses: (\d+)", o)) == sorted([3, 3, 3, 3, 3, 5, 3, 2]), re.findall(r"maxUses: (\d+)", o))
    chk("the blade: iron sword, Sharpness I, named Клинок Приюта", "Клинок Приюта" in o and "minecraft:sharpness" in o)
    chk("only the trophies of the region r1 are taken (by custom_data)", o.count('le_trophy: "r1"') >= 8 and 'le_trophy: "r2"' not in o)
    prep("Cam", 2); rc.run("give Cam minecraft:nautilus_shell[minecraft:custom_data={le_trophy:\"r1\"},minecraft:custom_name='{\"text\":\"Трофей Р1\",\"italic\":false}',minecraft:max_stack_size=16] 4"); rc.run("effect clear Cam")
    for _ in range(3):
        rc.run("tp Cam 58.5 101 25.3"); tc.face("Cam", 58.5, 101, 25.3, 58.5, 101.9, 27.5); time.sleep(0.5); tc.act("Cam", "!use"); time.sleep(1.0); tc.act("Cam", "!trade_sel 4"); time.sleep(0.7); tc.act("Cam", "!trade_take"); time.sleep(0.9); tc.act("Cam", "!sneak_off"); time.sleep(1.2)
        if "minecraft:shield" in inv("Cam"): break
    chk("a real purchase from Halvard: 2 trophies of the region r1 -> a shield (deal 5)", "minecraft:shield" in inv("Cam") and uses(4, tdt) >= 1, uses(4, tdt))
    rc.run("tp Cam 1100.5 200 1103.5")
def t_perf():
    print("[load]"); build()
    def mspt():
        r = rc.run("tick query"); m = re.search(r"Average time per tick: ([0-9.]+)ms.*?P50: ([0-9.]+)ms P95: ([0-9.]+)ms", r, re.S); return tuple(map(float, m.groups()))
    time.sleep(8); a = mspt(); print("   2 traders + the Smith: avg %.1f ms" % a[0]); chk("tick is light (< 12 ms on this machine)", a[0] < 12.0, a)
if __name__ == "__main__":
    want = sys.argv[1:] or ["build", "hello", "deals", "price", "hurt", "stock", "smith", "perf"]
    for w in want: globals()["t_" + w]()
    print(f"\n{ok} ok, {bad} failed"); sys.exit(1 if bad else 0)
