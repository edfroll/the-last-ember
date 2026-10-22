#!/usr/bin/env python3
"""T-016 checks (server + dev clients Cam, Cam2): traps of 8 types on the test playground (traps/test_traps.txt at x 1000-1064, z 998-1007, floor y=199).
Usage: python3 tools/test_traps.py [build pit arrows plate gas collapse lava chest treasure multi perf]"""
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
def st(i): return score(f"#{i}_st", "le.tr")
def sc(i, k): return score(f"#{i}_{k}", "le.tr")
def build():
    rc.run("forceload add 990 985 1070 1012")
    for _ in range(60):
        time.sleep(0.5)
        if "passed" in rc.run("execute if loaded 995 200 990") and "passed" in rc.run("execute if loaded 1068 200 1010"): break
    rc.run("tp Cam 1005.5 200 1005.5"); rc.run("tp Cam2 1005.5 200 1007.5"); time.sleep(1.0)
    rc.run("fill 995 189 988 1070 198 1010 air"); rc.run("fill 995 199 988 1070 199 1010 stone"); rc.run("fill 995 200 988 1070 210 1010 air")
    # the pit lair
    rc.run("fill 999 189 999 1004 198 1003 stone"); rc.run("fill 1000 191 1000 1003 198 1002 air"); rc.run("fill 1000 190 1000 1002 190 1002 minecraft:hay_block"); rc.run("fill 1000 199 1000 1002 199 1002 minecraft:moss_block")
    rc.run("setblock 1003 191 1001 minecraft:chest")
    # the arrow wall
    rc.run("fill 1009 199 998 1009 203 1006 stone"); [rc.run(f"setblock 1009 200 {z} air") for z in (1000, 1002, 1004)]
    # the plate
    rc.run("setblock 1020 200 1000 minecraft:oak_pressure_plate")
    # the collapse floors and the ground below
    rc.run("fill 1030 199 1000 1032 199 1002 minecraft:cracked_stone_bricks"); rc.run("fill 1029 191 999 1033 191 1003 stone"); rc.run("fill 1030 192 1000 1032 198 1002 air")
    rc.run("fill 1061 199 1001 1063 199 1003 minecraft:cracked_stone_bricks"); rc.run("fill 1060 191 1000 1064 191 1004 stone"); rc.run("fill 1061 192 1001 1063 198 1003 air")
    # the lava corridor: troughs (floor level) on both sides
    rc.run("fill 1042 199 999 1045 199 999 air"); rc.run("fill 1042 199 1003 1045 199 1003 air"); rc.run("setblock 1052 200 1002 minecraft:chest")
    rc.run("function last_ember:trap/reset_all") if False else None
    for t in ("tt_pit", "tt_arrows", "tt_plate", "tt_gas", "tt_collapse", "tt_lava", "tt_chest", "tt_treasure", "tt_collapse2"): rc.run(f'function last_ember:trap/reset {{id:"{t}"}}')
    time.sleep(2.5)
def prep(p="Cam", race=1, hp_full=True):
    tc.setc(race, 1, 0, p); rc.run(f"gamemode survival {p}"); rc.run(f"clear {p}"); rc.run(f"effect clear {p}")
    if hp_full: rc.run(f"effect give {p} minecraft:instant_health 1 10"); time.sleep(0.4)
def away(): rc.run("tp Cam 1005.5 200 1006.5"); rc.run("tp Cam2 1007.5 200 1006.5")
def t_build():
    print("[build]"); build(); chk("the playground is built: every trap has its state registered, the lock is on the lair chest", st("tt_pit") == 0 and "passed" in rc.run("execute if block 1003 192 1001 minecraft:iron_block"), st("tt_pit"))
def t_pit():
    print("[pit]"); away(); prep("Cam", 1); prep("Cam2", 4); rc.run("tp Cam 1005.5 200 1006.5"); rc.run("tp Cam2 1007.5 200 1006.5"); time.sleep(0.5)
    chk("the cover is moss at the start, the chest is locked", "passed" in rc.run("execute if block 1001 199 1001 minecraft:moss_block") and "passed" in rc.run("execute if block 1003 192 1001 minecraft:iron_block"))
    rc.run("tp Cam2 1001.5 200 1001.5"); time.sleep(2.0)
    chk("a halfling on the cover: the pit does not fire (light step)", st("tt_pit") == 0 and "passed" in rc.run("execute if block 1001 199 1001 minecraft:moss_block"), st("tt_pit"))
    rc.run("tp Cam2 1007.5 200 1006.5"); time.sleep(0.5)
    h0 = tc.hp("Cam"); rc.run("tp Cam 1001.5 200 1001.5"); time.sleep(1.8)
    chk("a human on the cover: after ~0.5 s the cover is gone", "passed" in rc.run("execute if block 1001 199 1001 minecraft:air"), st("tt_pit"))
    time.sleep(1.5); y = (re.findall(r"(-?\d+\.?\d*)d", rc.run("data get entity Cam Pos")) or ["0", "0", "0"])[1]
    chk(f"he fell into the lair (y={float(y):.0f}) and lost no more than 8 points ({h0} -> {tc.hp('Cam')})", float(y) < 195 and h0 - tc.hp("Cam") <= 8.0 and tc.hp("Cam") >= 2.0, (y, h0, tc.hp("Cam")))
    chk("the master of the lair appears: one, named, tagged le.trap_owner and le.noelite", num(rc.run("execute store result score #q le.tr if entity @e[tag=le.trap_owner,tag=le.noelite]") and str(score("#q", "le.tr"))) == 1.0 and "Хозяин" in rc.run("data get entity @e[tag=le.trap_owner,limit=1] CustomName"), score("#q", "le.tr"))
    chk("the chest stays locked while the master lives", "passed" in rc.run("execute if block 1003 192 1001 minecraft:iron_block"))
    rc.run("kill @e[tag=le.trap_owner]"); time.sleep(2.0)
    chk("the master is dead: the lock is gone, the chest can be opened", "passed" in rc.run("execute if block 1003 192 1001 minecraft:air"))
    rc.run("tp Cam 1005.5 200 1006.5"); time.sleep(1.0)
    rc.run("scoreboard players set #tt_pit_t le.tr 1195"); time.sleep(2.5)
    chk("after 60 s with nobody in the pit and above: the cover is back", "passed" in rc.run("execute if block 1001 199 1001 minecraft:moss_block") and st("tt_pit") == 0, (st("tt_pit"), sc("tt_pit", "t")))
    rc.run("tp Cam 1001.5 200 1001.5"); time.sleep(2.5); rc.run("tp Cam 1005.5 200 1006.5")
    chk("the second firing: no second master (once)", score("#q", "le.tr") is not None and num(rc.run("execute store result score #q le.tr if entity @e[tag=le.trap_owner]") and str(score("#q", "le.tr"))) == 0.0)
    rc.run("function last_ember:trap/reset {id:\"tt_pit\"}"); rc.run("effect give Cam minecraft:instant_health 1 10")
def t_arrows():
    print("[arrows]"); away(); prep("Cam", 1); rc.run("function last_ember:trap/reset {id:\"tt_arrows\"}"); rc.run("scoreboard players set #tt_arrows_cd le.tr 0"); rc.run("tp Cam 1012.5 200 1002.5 -90 0"); time.sleep(0.3)
    h0 = tc.hp("Cam"); peak = 0
    for _ in range(14):
        time.sleep(0.25); rc.run("execute store result score #q le.tr if entity @e[type=minecraft:arrow,tag=le.trap_arrow]"); peak = max(peak, score("#q", "le.tr") or 0)
    time.sleep(1.0); h1 = tc.hp("Cam")
    chk(f"volleys fly from the holes (up to {peak} arrows at once, 3 volleys of 3 arrows)", peak >= 3, peak)
    chk(f"damage of one firing: {h0 - h1:.1f} points (at most 8) and not below one heart", h0 - h1 <= 8.0 + 0.01 and tc.hp("Cam") >= 2.0, (h0, h1))
    chk("the trap is on cooldown (10 s)", (sc("tt_arrows", "cd") or 0) > (score("#gt", "le.e") or 0), (sc("tt_arrows", "cd"), score("#gt", "le.e")))
    rc.run("kill @e[tag=le.trap_arrow]"); rc.run("effect give Cam minecraft:instant_health 1 10"); time.sleep(0.5)
    rc.run("tp Cam 1005.5 200 1006.5"); time.sleep(0.5); rc.run("tp Cam 1012.5 200 1002.5"); time.sleep(1.2); rc.run("execute store result score #q le.tr if entity @e[type=minecraft:arrow,tag=le.trap_arrow]")
    chk("within the cooldown no new volley", (score("#q", "le.tr") or 0) == 0, score("#q", "le.tr"))
    # low health: never below one heart
    rc.run("kill @e[tag=le.trap_arrow]"); rc.run("scoreboard players set #tt_arrows_cd le.tr 0"); rc.run("tp Cam 1005.5 200 1006.5"); rc.run("effect give Cam minecraft:instant_health 1 10"); time.sleep(0.5); rc.run("damage Cam 16 minecraft:generic"); time.sleep(0.4); lo = tc.hp("Cam")
    rc.run("tp Cam 1012.5 200 1002.5 -90 0"); time.sleep(5.0)
    chk(f"with {lo} points of health the volleys leave at least one heart ({tc.hp('Cam')})", tc.hp("Cam") >= 2.0 and tc.hp("Cam") > 0, tc.hp("Cam"))
    rc.run("kill @e[tag=le.trap_arrow]"); rc.run("tp Cam 1005.5 200 1006.5"); rc.run("effect give Cam minecraft:instant_health 1 10")
def fx(p="Cam"): return rc.run(f"data get entity {p} active_effects")
def t_plate():
    print("[plate -> gas]"); away(); prep("Cam", 1); prep("Cam2", 4); rc.run('function last_ember:trap/reset {id:"tt_gas"}'); rc.run('function last_ember:trap/reset {id:"tt_plate"}'); rc.run("kill @e[type=minecraft:area_effect_cloud]")
    rc.run("tp Cam2 1020.5 200 1000.5"); time.sleep(1.5)
    chk("a halfling on the plate: nothing (light step)", st("tt_gas") == 0, st("tt_gas"))
    rc.run("tp Cam2 1007.5 200 1006.5"); rc.run("tp Cam 1020.5 200 1000.5"); time.sleep(1.2)
    chk("a human on the plate fires the linked trap (gas)", st("tt_gas") == 1 and (sc("tt_gas", "cd") or 0) > 0, st("tt_gas"))
    rc.run("tp Cam 1007.5 200 1006.5"); time.sleep(1.0)
def t_gas():
    print("[gas]"); away(); prep("Cam", 1); rc.run('function last_ember:trap/reset {id:"tt_gas"}'); rc.run("kill @e[type=minecraft:area_effect_cloud]"); time.sleep(0.5)
    rc.run("tp Cam 1024.5 200 1001.5"); time.sleep(0.4); h0 = tc.hp("Cam")
    time.sleep(2.0); rc.run("execute store result score #q le.tr if entity @e[type=minecraft:area_effect_cloud]")
    chk("the vents give 2 clouds", score("#q", "le.tr") == 2, score("#q", "le.tr"))
    rc.run("tp Cam 1024.5 200 999.5"); time.sleep(2.5)
    chk("in the cloud: poison I", "poison" in fx(), fx()[:150])
    rc.run("tp Cam 1007.5 200 1006.5"); time.sleep(9.0); rc.run("execute store result score #q le.tr if entity @e[type=minecraft:area_effect_cloud]")
    chk("the cloud lives about 8 s", score("#q", "le.tr") == 0, score("#q", "le.tr")); chk("the poison does not kill (never below half a heart)", tc.hp("Cam") >= 1.0, tc.hp("Cam"))
    chk("cooldown 20 s: a second visit at once does not fire it again", st("tt_gas") == 0 and (sc("tt_gas", "cd") or 0) > (score("#gt", "le.e") or 0))
    rc.run("effect clear Cam")
def t_collapse():
    print("[collapse]"); away(); prep("Cam", 1); prep("Cam2", 4); rc.run('function last_ember:trap/reset {id:"tt_collapse"}'); time.sleep(0.5)
    rc.run("tp Cam2 1031.5 200 1001.5"); time.sleep(2.0); chk("a halfling on the cracked floor: it holds", "passed" in rc.run("execute if block 1031 199 1001 minecraft:cracked_stone_bricks") and st("tt_collapse") == 0)
    rc.run("tp Cam2 1007.5 200 1006.5"); h0 = tc.hp("Cam"); rc.run("tp Cam 1031.5 200 1001.5"); time.sleep(0.5)
    chk("a human: first the crack hint (the state runs), the floor is still there", st("tt_collapse") == 1 and "passed" in rc.run("execute if block 1031 199 1001 minecraft:cracked_stone_bricks"))
    time.sleep(1.6); chk("after 1 s the floor falls (air)", "passed" in rc.run("execute if block 1031 199 1001 minecraft:air"))
    time.sleep(2.0); y = float((re.findall(r"(-?\d+\.?\d*)d", rc.run("data get entity Cam Pos")) or ["0", "0", "0"])[1])
    chk(f"he is on the level below (y={y:.0f}), the fall hurt less than 8 ({h0} -> {tc.hp('Cam')})", y < 195 and h0 - tc.hp("Cam") <= 8.0 and tc.hp("Cam") >= 2.0, (y, h0, tc.hp("Cam")))
    chk("no stray falling blocks stay", "passed" not in rc.run("execute if entity @e[type=minecraft:falling_block,tag=le.trap_fb]") and "passed" not in rc.run("execute if block 1031 192 1001 minecraft:cracked_stone_bricks"))
    rc.run("tp Cam 1005.5 200 1006.5"); time.sleep(0.5); rc.run("scoreboard players set #tt_collapse_t le.tr 1240"); time.sleep(2.0)
    chk("after 60 s, nobody there: the floor is back", "passed" in rc.run("execute if block 1031 199 1001 minecraft:cracked_stone_bricks") and st("tt_collapse") == 0, st("tt_collapse"))
def t_lava():
    print("[lava]"); away(); prep("Cam", 1); rc.run('function last_ember:trap/reset {id:"tt_lava"}'); time.sleep(0.5)
    rc.run("tp Cam 1046.5 200 1001.5"); time.sleep(0.4); h0 = tc.hp("Cam"); time.sleep(2.2)
    chk("a second after entering: the side channels and the way back are lava", "passed" in rc.run("execute if block 1043 199 999 minecraft:lava") and "passed" in rc.run("execute if block 1040 200 1001 minecraft:lava"), "")
    chk("the player in the corridor (forward) is not burnt", tc.hp("Cam") >= h0 - 0.5 and "burn" not in rc.run("data get entity Cam Fire") , (h0, tc.hp("Cam")))
    rc.run("tp Cam 1007.5 200 1006.5"); rc.run("scoreboard players set #tt_lava_t le.tr 425"); time.sleep(10.0)
    chk("after 20 s the lava goes away", "passed" not in rc.run("execute if block 1043 199 999 minecraft:lava") and "passed" not in rc.run("execute if block 1040 200 1001 minecraft:lava"))
    chk("cooldown 60 s", st("tt_lava") == 0 and (sc("tt_lava", "cd") or 0) > (score("#gt", "le.e") or 0))
    # lava does not close the way while a player stands in the back box: it waits
    rc.run('function last_ember:trap/reset {id:"tt_lava"}'); rc.run("fill 1039 200 999 1047 202 1003 air replace minecraft:lava"); time.sleep(4.0); rc.run("effect clear Cam"); rc.run("effect give Cam minecraft:instant_health 1 10"); time.sleep(0.6); hb = tc.hp("Cam"); rc.run("tp Cam 1040.5 200 1001.5"); rc.run("tp Cam2 1046.5 200 1001.5"); time.sleep(0.3)
    time.sleep(2.5); chk("a player still stands in the way-back box: the lava waits, nobody burns", "passed" not in rc.run("execute if block 1040 200 1001 minecraft:lava") and tc.hp("Cam") >= hb - 0.5, (hb, tc.hp("Cam")))
    rc.run("tp Cam 1046.5 200 1002.5"); time.sleep(2.5); chk("he has gone on: the way back closes", "passed" in rc.run("execute if block 1040 200 1001 minecraft:lava"))
    rc.run('function last_ember:trap/reset {id:"tt_lava"}'); rc.run("tp Cam 1007.5 200 1006.5"); rc.run("tp Cam2 1007.5 200 1007.5")
def t_chest():
    print("[cursed chest]"); away(); prep("Cam", 1); prep("Cam2", 1); rc.run('function last_ember:trap/reset {id:"tt_chest"}'); rc.run("kill @e[type=minecraft:zombie]"); rc.run("kill @e[type=minecraft:zombie]"); time.sleep(0.5)
    rc.run("gamemode creative Cam"); rc.run("gamemode creative Cam2"); rc.run("tp Cam 1052.5 200 1005.5"); tc.face("Cam", 1052.5, 200, 1005.5, 1052.5, 200.5, 1002.5); rc.run("tp Cam2 1056.5 200 1005.5"); time.sleep(1.5)
    rc.run("scoreboard players add Cam le.chop 1"); time.sleep(1.2)
    rc.run("execute store result score #q le.tr if entity @e[type=minecraft:zombie]")
    chk("the first opening: 2 + 1 per player within 16 = 4 mobs", score("#q", "le.tr") == 4, score("#q", "le.tr"))
    rc.run("kill @e[type=minecraft:zombie]"); rc.run("scoreboard players add Cam le.chop 1"); time.sleep(1.2); rc.run("execute store result score #q le.tr if entity @e[type=minecraft:zombie]")
    chk("only once: a second opening calls nobody", score("#q", "le.tr") == 0, score("#q", "le.tr"))
    # an opening of another chest while looking away does not count
    rc.run('function last_ember:trap/reset {id:"tt_chest"}'); tc.face("Cam", 1052.5, 200, 1005.5, 1052.5, 200.5, 1010.5); time.sleep(0.4); rc.run("scoreboard players add Cam le.chop 1"); time.sleep(1.2); rc.run("execute store result score #q le.tr if entity @e[type=minecraft:zombie]")
    chk("a player who looks away from the chest (opens another one) does not wake it", score("#q", "le.tr") == 0, score("#q", "le.tr"))
    rc.run("kill @e[type=minecraft:zombie]"); rc.run("gamemode survival Cam"); rc.run("gamemode survival Cam2"); rc.run("tp Cam 1007.5 200 1006.5"); rc.run("tp Cam2 1007.5 200 1007.5")
def t_treasure():
    print("[false treasure]"); away(); prep("Cam", 1); prep("Cam2", 4); rc.run('function last_ember:trap/reset {id:"tt_treasure"}'); rc.run('function last_ember:trap/reset {id:"tt_collapse2"}'); time.sleep(2.0)
    chk("the treasure stands (a display and an interaction)", "passed" in rc.run("execute if entity @e[type=minecraft:item_display,tag=le.ftd]") and "passed" in rc.run("execute if entity @e[type=minecraft:interaction,tag=le.ft]"))
    rc.run("tp Cam2 1062.5 200 1004.5 0 0"); tc.face("Cam2", 1062.5, 200, 1004.5, 1062.5, 200.4, 1002.5); time.sleep(0.5); tc.act("Cam2", "!use"); time.sleep(1.5)
    chk("a halfling takes it: it does not fire the link (light step), the floor holds", "passed" in rc.run("execute if block 1062 199 1002 minecraft:cracked_stone_bricks") and st("tt_collapse2") == 0)
    rc.run("tp Cam2 1007.5 200 1006.5"); rc.run("tp Cam 1062.5 200 1004.5"); tc.face("Cam", 1062.5, 200, 1004.5, 1062.5, 200.4, 1002.5); time.sleep(0.5); tc.act("Cam", "!use"); time.sleep(0.8)
    chk("a human touches it: it crumbles to dust (the display is gone) and the link fires", "passed" not in rc.run("execute if entity @e[type=minecraft:item_display,tag=le.ftd]") and st("tt_collapse2") >= 1, (st("tt_collapse2"),))
    rc.run("tp Cam 1007.5 200 1006.5"); rc.run('function last_ember:trap/reset {id:"tt_treasure"}'); rc.run('function last_ember:trap/reset {id:"tt_collapse2"}')
def t_multi():
    print("[two players]"); away(); prep("Cam", 1); prep("Cam2", 1); rc.run('function last_ember:trap/reset {id:"tt_arrows"}'); rc.run("scoreboard players set #tt_arrows_cd le.tr 0"); rc.run("kill @e[tag=le.trap_arrow]")
    rc.run("tp Cam 1012.5 200 1001.5 -90 0"); rc.run("tp Cam2 1012.5 200 1003.5 -90 0"); h0 = (tc.hp("Cam"), tc.hp("Cam2")); peak = 0
    for _ in range(16):
        time.sleep(0.25); rc.run("execute store result score #q le.tr if entity @e[type=minecraft:arrow,tag=le.trap_arrow]"); peak = max(peak, score("#q", "le.tr") or 0)
    time.sleep(1.0)
    chk(f"both players in the area: one shared firing (3 points x 3 volleys, peak {peak} arrows), each took at most 8", peak <= 9 and h0[0] - tc.hp("Cam") <= 8.0 and h0[1] - tc.hp("Cam2") <= 8.0 and tc.hp("Cam") >= 2 and tc.hp("Cam2") >= 2, (peak, h0, tc.hp("Cam"), tc.hp("Cam2")))
    rc.run("kill @e[tag=le.trap_arrow]"); away()
def t_perf():
    print("[load]")
    def mspt():
        r = rc.run("tick query"); m = re.search(r"Average time per tick: ([0-9.]+)ms.*?P50: ([0-9.]+)ms P95: ([0-9.]+)ms", r, re.S); return tuple(map(float, m.groups()))
    away(); time.sleep(8); b = mspt(); print("   idle with the playground (9 traps): avg %.1f ms" % b[0])
    rc.run("tp Cam 1012.5 200 1002.5"); rc.run("tp Cam2 1031.5 200 1001.5"); time.sleep(8); a = mspt(); print("   players in two trap areas: avg %.1f ms" % a[0]); chk("tick does not grow noticeably (< +3 ms)", a[0] - b[0] < 3.0, (b, a)); away()
if __name__ == "__main__":
    want = sys.argv[1:] or ["build", "pit", "arrows", "plate", "gas", "collapse", "lava", "chest", "treasure", "multi", "perf"]
    for w in want: globals()["t_" + w]()
    print(f"\n{ok} ok, {bad} failed"); sys.exit(1 if bad else 0)
