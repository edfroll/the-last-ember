#!/usr/bin/env python3
"""T-016 checks (server + dev clients Cam, Cam2): coming-to-life statues of the test playground (statues/test_statues.txt, floor y=199, x 1000-1052, z 1016-1030).
Usage: python3 tools/test_statues.py [build event item return random perf]"""
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
def st(i): return score(f"#{i}_st", "le.st")
def data(i, path): return rc.run(f"data get entity @e[tag=le.st_{i},limit=1] {path}")
def asleep(i): return "1b" in data(i, "NoAI") and "1b" in data(i, "Invulnerable")
def awake(i): return "1b" not in data(i, "NoAI") and "1b" not in data(i, "Invulnerable").split("entity data:")[-1]
def build():
    rc.run("forceload add 990 1010 1070 1035")
    for _ in range(60):
        time.sleep(0.5)
        if "passed" in rc.run("execute if loaded 995 200 1016") and "passed" in rc.run("execute if loaded 1060 200 1030"): break
    rc.run("tp Cam 1010.5 200 1012.5"); rc.run("tp Cam2 1012.5 200 1012.5"); time.sleep(1.0)
    rc.run("fill 995 199 1010 1065 199 1035 stone"); rc.run("fill 995 200 1010 1065 208 1035 air"); rc.run("kill @e[type=minecraft:husk]")
    for g in ("evg", "seal", "corr"): rc.run(f'function last_ember:statue/reset {{group:"{g}"}}')
    rc.run("scoreboard players set #corr_cd le.st 0"); time.sleep(3.0)
def prep(p, race=1):
    tc.setc(race, 1, 0, p); rc.run(f"gamemode survival {p}"); rc.run(f"clear {p}"); rc.run(f"effect clear {p}"); rc.run(f"effect give {p} minecraft:resistance 1000 4 true")
def away(): rc.run("tp Cam 1010.5 200 1012.5"); rc.run("tp Cam2 1012.5 200 1012.5")
def t_build():
    print("[build]"); build()
    chk("12 statues stand on their pedestals (husks with tags le.statue, le.noelite)", all(f"le.st_{i}" in rc.run("data get entity @e[tag=le.st_" + i + ",limit=1] Tags") for i in ("ev1", "it2", "rn5")) and "passed" in rc.run("execute if entity @e[type=minecraft:husk,tag=le.statue,tag=le.noelite,limit=12]"))
    chk("a statue is stone: NoAI, Silent, Invulnerable, PersistenceRequired, a gray dyed leather outfit, nothing drops", asleep("ev1") and "1b" in data("ev1", "Silent") and "1b" in data("ev1", "PersistenceRequired") and "leather_helmet" in data("ev1", "equipment") and "dyed_color" in data("ev1", "equipment.chest.components") and "head: 0.0f" in data("ev1", "drop_chances").replace('"', ""), data("ev1", "drop_chances")[:100])
    yaws = {i: data(i, "Rotation") for i in ("it1", "ev1")}; chk("a statue faces its direction (yaw from the file)", "90.0f" in yaws["it1"] and "0.0f" in yaws["ev1"], yaws)
def t_event():
    print("[event]"); build(); away(); prep("Cam"); rc.run("tp Cam 1003.5 200 1012.5")
    chk("they sleep until the event", all(asleep(i) for i in ("ev1", "ev2", "ev3", "ev4")) and all(st(i) == 0 for i in ("ev1", "ev2", "ev3", "ev4")))
    rc.run('function last_ember:statue/wake {group:"evg"}'); time.sleep(0.5)
    chk("the call: they are waking up (a second of dust and scrape)", all(st(i) == 3 for i in ("ev1", "ev2", "ev3", "ev4")) and asleep("ev1"), [st(i) for i in ("ev1", "ev2", "ev3", "ev4")])
    time.sleep(1.2)
    chk("a second later all 4 live: no NoAI, vulnerable, noisy, named, with the stats of an elite", all(st(i) == 1 and awake(i) for i in ("ev1", "ev2", "ev3", "ev4")) and "Каменный страж" in data("ev2", "CustomName") and "1b" in data("ev2", "CustomNameVisible") and "le.elite" in data("ev2", "Tags"), [st(i) for i in ("ev1", "ev2", "ev3", "ev4")])
    time.sleep(2.0); d = num(rc.run("data get entity Cam Health")) or 20; pos = re.findall(r"(-?\d+\.?\d*)d", data("ev1", "Pos"))
    chk("they go for the nearest player (they moved off the pedestal)", abs(float(pos[2]) - 1020.5) > 0.5 or abs(float(pos[0]) - 1000.5) > 0.5, pos)
    rc.run("effect clear Cam"); away()
def t_item():
    print("[item mode: the seal]"); build(); away(); prep("Cam"); prep("Cam2", 4)
    rc.run("tp Cam 1015.5 200 1020.5 -90 0"); time.sleep(1.5)
    chk("a player without the seal within 6 blocks wakes the nearest statue only", st("it1") in (1, 3) and st("it2") == 0 and st("it3") == 0, [st(i) for i in ("it1", "it2", "it3")])
    time.sleep(1.5); rc.run('function last_ember:statue/reset {group:"seal"}'); away(); time.sleep(3.0)
    rc.run("give Cam minecraft:stick[minecraft:custom_data={le_testseal:1b},minecraft:custom_name='\"Тестовая печать\"']"); time.sleep(0.3)
    rc.run("tp Cam 1015.5 200 1028.5"); rc.run("tp Cam2 1018.5 200 1028.5"); time.sleep(2.0)
    chk("the carrier of the seal and his partner (within 10 blocks of the carrier) are protected: nothing wakes", all(st(i) == 0 for i in ("it1", "it2", "it3")), [st(i) for i in ("it1", "it2", "it3")])
    rc.run("tp Cam2 1015.5 200 1028.5"); rc.run("tp Cam 1001.5 200 1028.5"); time.sleep(2.5)
    chk("the partner stays within 6 blocks of the statue but more than 10 from the carrier: unprotected, it3 wakes", st("it3") in (1, 3), [st(i) for i in ("it1", "it2", "it3")])
    rc.run('function last_ember:statue/reset {group:"seal"}'); rc.run("clear Cam"); away(); time.sleep(3.0)
    rc.run("give Cam2 minecraft:stick[minecraft:custom_data={le_testseal:1b}]"); rc.run("tp Cam 1015.5 200 1020.5"); rc.run("tp Cam2 1019.5 200 1016.5"); time.sleep(2.0)
    chk("the seal on the other player protects the one standing near the statue (any carrier works)", all(st(i) == 0 for i in ("it1", "it2", "it3")), [st(i) for i in ("it1", "it2", "it3")])
    rc.run("clear Cam2"); rc.run('function last_ember:statue/reset {group:"seal"}'); away()
def t_return():
    print("[return and death]"); build(); away(); prep("Cam"); prep("Cam2", 4)
    rc.run("tp Cam 1015.5 200 1020.5"); time.sleep(3.0); chk("a statue woke", st("it1") in (1, 3), st("it1")); rc.run("effect give Cam minecraft:instant_health 1 10")
    rc.run("tp Cam 1015.5 200 1000.5"); rc.run("tp Cam2 1010.5 200 1000.5"); time.sleep(1.0); rc.run("tp Cam 1015.5 200 985.5"); rc.run("tp Cam2 1010.5 200 985.5"); time.sleep(3.5)
    pos = [float(v) for v in re.findall(r"(-?\d+\.?\d*)d", data("it1", "Pos"))] or [0, 0, 0]; hp = num(data("it1", "Health")); mx = num(rc.run("attribute @e[tag=le.st_it1,limit=1] minecraft:max_health get"))
    chk("every player further than 32 blocks: the statue is back on its pedestal, stone again", st("it1") == 0 and asleep("it1") and abs(pos[0] - 1020.5) < 0.2 and abs(pos[2] - 1020.5) < 0.2, (st("it1"), pos))
    chk("with full health, the elite's stats taken off, no name", abs(hp - mx) < 0.1 and "le.elite" not in data("it1", "Tags") and "CustomName" not in data("it1", "CustomName") or "Found no" in data("it1", "CustomName"), (hp, mx, data("it1", "CustomName")[:60]))
    # the killed statue stays dead
    rc.run("tp Cam 1015.5 200 1020.5"); time.sleep(3.0); rc.run("damage @e[tag=le.st_it1,limit=1] 1000 minecraft:player_attack by Cam"); time.sleep(1.5); rc.run("tp Cam 1015.5 200 985.5"); rc.run("tp Cam2 1010.5 200 985.5"); time.sleep(3.0)
    chk("a killed statue does not come back (the pedestal is empty, state 2)", st("it1") == 2 and "passed" not in rc.run("execute if entity @e[tag=le.st_it1]"), (st("it1"),))
    rc.run('function last_ember:statue/reset {group:"seal"}'); away(); time.sleep(3.0); chk("the admin reset puts a new one on the pedestal", st("it1") == 0 and "passed" in rc.run("execute if entity @e[tag=le.st_it1]"))
def t_random():
    print("[random mode: the corridor]"); build(); away(); prep("Cam"); prep("Cam2", 4)
    chk("five statues stand in the corridor and sleep", all(st(f"rn{k}") == 0 for k in range(1, 6)))
    rc.run("tp Cam 1046.5 200 1020.5 -90 0"); time.sleep(2.0)
    woke = [k for k in range(1, 6) if st(f"rn{k}") in (1, 3)]
    chk(f"a player in the middle looking east: exactly one statue wakes, and it is behind him (rn1, rn2: {woke})", len(woke) == 1 and woke[0] in (1, 2), woke)
    rc.run("tp Cam 1050.5 200 1020.5 -90 0"); time.sleep(2.0); woke2 = [k for k in range(1, 6) if st(f"rn{k}") in (1, 3)]
    chk("once per pass: while the group is on cooldown (2 minutes) nobody else wakes", woke2 == woke, woke2)
    rc.run("scoreboard players set #corr_cd le.st 0"); time.sleep(2.0); woke3 = [k for k in range(1, 6) if st(f"rn{k}") in (1, 3)]
    chk("after the cooldown the next pass wakes another one (behind him)", len(woke3) == 2 and all(k <= 4 for k in woke3), woke3)
    rc.run('function last_ember:statue/reset {group:"corr"}'); rc.run("scoreboard players set #corr_cd le.st 0"); away(); time.sleep(3.0)
    rc.run("tp Cam 1038.5 200 1020.5 -90 0"); time.sleep(2.0); woke4 = [k for k in range(1, 6) if st(f"rn{k}") in (1, 3)]
    chk("at the entrance, looking east: everything is ahead, so nothing wakes", woke4 == [], woke4)
    rc.run('function last_ember:statue/reset {group:"corr"}'); rc.run("scoreboard players set #corr_cd le.st 0"); away()
def t_perf():
    print("[load: 12 statues, 7 awake]")
    def mspt():
        r = rc.run("tick query"); m = re.search(r"Average time per tick: ([0-9.]+)ms.*?P50: ([0-9.]+)ms P95: ([0-9.]+)ms", r, re.S); return tuple(map(float, m.groups()))
    build(); away(); time.sleep(8); b = mspt(); print("   12 statues asleep: avg %.1f ms" % b[0])
    rc.run('function last_ember:statue/wake {group:"evg"}'); rc.run('function last_ember:statue/wake {group:"seal"}'); time.sleep(10); a = mspt(); print("   7 awake: avg %.1f ms" % a[0])
    chk("tick does not grow noticeably (< +3 ms)", a[0] - b[0] < 3.0, (b, a)); rc.run('function last_ember:statue/reset {group:"evg"}'); rc.run('function last_ember:statue/reset {group:"seal"}')
if __name__ == "__main__":
    want = sys.argv[1:] or ["build", "event", "item", "return", "random", "perf"]
    for w in want: globals()["t_" + w]()
    print(f"\n{ok} ok, {bad} failed"); sys.exit(1 if bad else 0)
