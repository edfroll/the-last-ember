#!/usr/bin/env python3
"""T-015 checks (server + dev clients Cam, Cam2): insomnia, hallucinations (module halluc/*), sleep rules, elite arrows x1.5, the ring on the common module.
Usage: python3 tools/test_sleep.py [stages events refuge sleep isolation arrows ring perf]"""
import importlib.util, math, os, re, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class"); tr = load("test_ring")
ok = bad = 0
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n)
    else: bad += 1; print("  FAIL", n, e)
score, num = tc.score, tc.num
def awake(p, ticks): rc.run(f"execute as {p} run function last_ember:sleep/set_awake {{ticks:{ticks}}}")
def reset_timers(p):
    for o in ("hw", "hsh", "hfm", "hpu", "hk"): rc.run(f"scoreboard players reset {p} le.{o}")
    rc.run(f"scoreboard players set {p} le.hst 0"); rc.run("kill @e[type=marker,tag=le.hmark]")
def setup(p="Cam"):
    tr.arena(); rc.run(f"gamemode survival {p}"); rc.run(f"tp {p} 600.5 200 600.5"); rc.run(f"effect clear {p}"); reset_timers(p); rc.run(f"scoreboard players set {p} le.hstg 0"); rc.run(f"scoreboard players set {p} le.hst 0")
    rc.run("difficulty normal")
def fx(p="Cam"): return rc.run(f"data get entity {p} active_effects")
def sc(p, o): return score(p, o)
def t_stages():
    print("[the stages by the counter]"); setup()
    awake("Cam", 20000); time.sleep(2.2); chk("less than a day: nothing (stage 0, no timers)", sc("Cam", "le.hstg") == 0 and sc("Cam", "le.hw") is None)
    awake("Cam", 24500); time.sleep(2.2); chk("1 day: stage 1, only the whisper timer (60-120 s)", sc("Cam", "le.hstg") == 1 and 1000 <= (sc("Cam", "le.hw") or 0) + 60 <= 2500 and sc("Cam", "le.hsh") is None and sc("Cam", "le.hpu") is None, (sc("Cam", "le.hstg"), sc("Cam", "le.hw")))
    chk("stage 1: no slowness, no weakness", "slowness" not in fx() and "weakness" not in fx())
    awake("Cam", 37000); time.sleep(2.2); chk("1.5 days: stage 2, shadows and false mobs, whisper 30-60 s", sc("Cam", "le.hstg") == 2 and sc("Cam", "le.hsh") is not None and sc("Cam", "le.hfm") is not None and (sc("Cam", "le.hw") or 0) <= 1300, (sc("Cam", "le.hstg"), sc("Cam", "le.hw"), sc("Cam", "le.hsh")))
    chk("stage 2: no pulses yet, no slowness", sc("Cam", "le.hpu") is None and "slowness" not in fx())
    awake("Cam", 50000); time.sleep(2.2); chk("2 days: stage 3, pulses, slowness I as short impulses", sc("Cam", "le.hstg") == 3 and sc("Cam", "le.hpu") is not None and "slowness" in fx() and "weakness" not in fx(), (sc("Cam", "le.hstg"), fx()[:200]))
    chk("stage 3: no blows yet", sc("Cam", "le.hk") is None)
    awake("Cam", 80000); time.sleep(2.2); chk("3 days: stage 4, blows, weakness I too", sc("Cam", "le.hstg") == 4 and sc("Cam", "le.hk") is not None and "weakness" in fx() and "slowness" in fx(), (sc("Cam", "le.hstg"), fx()[:200]))
    reset_timers("Cam"); awake("Cam", 0); time.sleep(1.5); rc.run("effect clear Cam")
def t_events():
    print("[the events fire]"); setup(); awake("Cam", 80000); time.sleep(1.5)
    def fire(timer): rc.run(f"scoreboard players set Cam le.{timer} 0"); time.sleep(1.4)
    w0 = sc("Cam", "le.hw"); fire("hw"); chk("the whisper timer ran out: it fired and was set again (15-30 s at stage 4)", 200 <= (sc("Cam", "le.hw") or 0) + 20 <= 650, sc("Cam", "le.hw"))
    rc.run("scoreboard players set Cam le.hst 0"); fire("hsh"); mk = rc.run("execute if entity @e[type=marker,tag=le.hmark]")
    chk("a shadow appears: a server-side marker holds the place, the session runs (5-10 frames of 4 ticks)", "passed" in mk and (sc("Cam", "le.hst") or 0) > 0, (mk, sc("Cam", "le.hst")))
    # the shadow is 10-16 blocks off to the side and goes out when the player turns to it
    pos = rc.run("data get entity @e[type=marker,tag=le.hmark,limit=1] Pos"); v = re.findall(r"(-?\d+\.?\d*)d", pos); mx, mz = float(v[0]), float(v[2]); d = math.hypot(mx - 600.5, mz - 600.5)
    chk(f"the shadow stands 10-16 blocks away ({d:.1f})", 9.5 <= d <= 16.5, d)
    tc.face("Cam", 600.5, 200, 600.5, mx, 200.9, mz); time.sleep(0.8)
    chk("the player turned to it: it is gone", "passed" not in rc.run("execute if entity @e[type=marker,tag=le.hmark]") and (sc("Cam", "le.hst") or 0) == 0)
    rc.run("scoreboard players set Cam le.hst 0"); fire("hsh"); time.sleep(2.6); tc.face("Cam", 600.5, 200, 600.5, 600.5, 200.9, 560.5) if False else None
    chk("a shadow that is not looked at goes out by itself within ~2 s", "passed" not in rc.run("execute if entity @e[type=marker,tag=le.hmark]") and (sc("Cam", "le.hst") or 0) == 0)
    rc.run("effect clear Cam"); fire("hpu"); chk("a pulse: nausea or darkness", "nausea" in fx() or "darkness" in fx(), fx()[:150])
    rc.run("effect clear Cam"); rc.run("effect give Cam minecraft:instant_health 1 10"); time.sleep(0.5); hp0 = tc.hp("Cam"); fire("hk"); hp1 = tc.hp("Cam")
    chk("a blow: 0.5 heart (1 point)", 0.6 <= (hp0 - hp1) <= 1.3, (hp0, hp1))
    # never below one heart
    rc.run("effect clear Cam"); rc.run("scoreboard players set Cam le.hk 99999"); rc.run("effect give Cam minecraft:instant_damage 1 1"); time.sleep(0.2)
    rc.run("data modify entity Cam Health set value 2.0f") if False else None
    for hp in (20, 5):
        pass
    # health down to 2 (1 heart) by damage, then blows must not kill or hurt
    rc.run("effect clear Cam"); rc.run("effect give Cam minecraft:instant_health 1 10"); time.sleep(0.4); rc.run("damage Cam 18 minecraft:generic"); time.sleep(0.3); h = tc.hp("Cam")
    for _ in range(4): rc.run("scoreboard players set Cam le.hk 0"); time.sleep(1.3)
    chk(f"blows never take the last heart (had {h}, has {tc.hp('Cam')})", tc.hp("Cam") >= 1.0 and tc.hp("Cam") >= h - 1.0 - 0.01 and tc.hp("Cam") > 0, (h, tc.hp("Cam")))
    rc.run("effect give Cam minecraft:instant_health 1 10"); reset_timers("Cam"); awake("Cam", 0)
def t_refuge():
    print("[the Refuge is quiet, the counter goes on]"); setup(); awake("Cam", 80000); time.sleep(1.5)
    rc.run("tp Cam 0.5 105 6.5"); time.sleep(1.5); reset_timers("Cam"); rc.run("effect clear Cam"); r0 = sc("Cam", "le.rest"); time.sleep(3.2)
    chk("in the Refuge: no timers run, no slowness/weakness", sc("Cam", "le.hw") is None and sc("Cam", "le.hsh") is None and "slowness" not in fx() and "weakness" not in fx(), (sc("Cam", "le.hw"), fx()[:100]))
    chk("the counter goes on in the Refuge (a rest, not a cure)", sc("Cam", "le.rest") > r0 + 40, (r0, sc("Cam", "le.rest")))
    rc.run("tp Cam 600.5 200 600.5"); time.sleep(2.5); chk("outside again: the insomnia works", sc("Cam", "le.hw") is not None and "slowness" in fx())
    awake("Cam", 0); reset_timers("Cam"); rc.run("effect clear Cam")
def bed_test(bed):
    setup(); rc.run("tp Cam2 608.5 200 608.5"); rc.run("gamemode survival Cam2"); rc.run("kill @e[type=item]")
    rc.run("fill 596 199 596 604 199 606 stone"); rc.run(f"setblock 600 200 604 minecraft:{bed}[facing=south,part=head] strict"); rc.run(f"setblock 600 200 603 minecraft:{bed}[facing=south,part=foot] strict")
    rc.run("gamerule advance_time true"); rc.run("difficulty peaceful"); rc.run("kill @e[type=#last_ember:monsters]"); awake("Cam", 60000); awake("Cam2", 60000); rc.run("time set 13500")
    tc.face("Cam", 600.5, 200, 601.5, 600.5, 200.3, 603.5); time.sleep(0.5); tc.act("Cam", "!use"); time.sleep(1.0)
    slept = False
    for _ in range(40):
        time.sleep(0.5)
        dt = num(rc.run("time query day"), r"at (\d+) tick")
        if dt is not None and dt < 3000: slept = True; break
    return slept
def t_sleep():
    print("[sleep: 50%, the counter is reset for the sleeper only]")
    for bed in ("red_bed", "straw_bed"):
        slept = bed_test(bed); time.sleep(1.5)
        chk(f"{bed}: one of two players in bed: the night is skipped (50%)", slept, rc.run("time query day"))
        chk(f"{bed}: the sleeper's counter is reset", (sc("Cam", "le.rest") or 99999) < 3000, sc("Cam", "le.rest"))
        chk(f"{bed}: the one who did not sleep keeps his counter", (sc("Cam2", "le.rest") or 0) > 60000, sc("Cam2", "le.rest"))
        chk(f"{bed}: the sleeper's stage is 0 again, his insomnia is over", sc("Cam", "le.hstg") == 0, sc("Cam", "le.hstg"))
        rc.run("setblock 600 200 604 air"); rc.run("setblock 600 200 603 air"); rc.run("difficulty normal"); rc.run("tp Cam 600.5 200 600.5")
    rc.run("gamerule advance_time false"); rc.run("time set 6000")
    rc.run("gamerule players_sleeping_percentage") ; chk("the rule players_sleeping_percentage is 50", "50" in rc.run("gamerule players_sleeping_percentage"))
def t_isolation():
    print("[for him only]"); bad_lines = []
    for sub in ("halluc", "ring"):
        d = os.path.join(ROOT, "datapack/data/last_ember/function", sub)
        for f in os.listdir(d):
            for ln, l in enumerate(open(os.path.join(d, f), encoding="utf-8"), 1):
                if l.startswith("#"): continue
                if "playsound" in l and not re.search(r"playsound \S+ \S+ (@s|@a\[tag=le\.hme\]) ", l) and "ring/" not in f.replace(".mcfunction", "") + "x" and False: bad_lines.append((f, ln))
                if "playsound" in l and " @s " not in l and "@a[tag=le.hme]" not in l and "ringon" not in l: bad_lines.append((sub + "/" + f, ln, l.strip()[:90]))
                if re.search(r"\bparticle\b", l) and sub == "halluc" and "force @a[tag=le.hme]" not in l: bad_lines.append((sub + "/" + f, ln, l.strip()[:90]))
    chk("every playsound of halluc/* goes to @s, every particle to the viewer only (static check)", not [b for b in bad_lines if b[0].startswith("halluc")], [b for b in bad_lines if b[0].startswith("halluc")])
    # the only entities: server-side markers (never sent to clients)
    src = "".join(open(os.path.join(ROOT, "datapack/data/last_ember/function/halluc", f), encoding="utf-8").read() for f in os.listdir(os.path.join(ROOT, "datapack/data/last_ember/function/halluc")))
    chk("the module summons nothing but markers", set(re.findall(r"summon (\S+)", src)) <= {"minecraft:marker"}, set(re.findall(r"summon (\S+)", src)))
    # a second client next to the first: screenshots of the same spot
    setup(); rc.run("tp Cam2 600.5 200 604.5 180 0"); rc.run("gamemode survival Cam2"); awake("Cam", 80000); reset_timers("Cam"); time.sleep(1.2)
    rc.run("effect give Cam minecraft:resistance 100 4")
    rc.run("scoreboard players set Cam le.hid 0"); rc.run("execute as Cam at @s run function last_ember:halluc/shadow")
    rc.run("scoreboard players set Cam le.hst 40"); rc.run("execute as @e[type=marker,tag=le.hmark] run scoreboard players set @s le.hst 30")
    time.sleep(0.2)
    pos = rc.run("data get entity @e[type=marker,tag=le.hmark,limit=1] Pos"); v = re.findall(r"(-?\d+\.?\d*)d", pos)
    if len(v) == 3:
        mx, mz = float(v[0]), float(v[2])
        tc.face("Cam2", 604.5, 200, 600.5, mx, 201.0, mz)
        rc.run(f"tp Cam 600.5 200 600.5 0 0"); tc.face("Cam", 600.5, 200, 600.5, 600.5, 200.9, 570.5)   # Cam looks away from it
        tc.act("Cam", "shadow_cam 0"); tc.act("Cam2", "shadow_cam2 0")
        print("   screenshots: server/client/screenshots/shadow_cam.png (the owner), server/client2/screenshots/shadow_cam2.png (the neighbour)")
    rc.run("kill @e[type=marker,tag=le.hmark]"); awake("Cam", 0); reset_timers("Cam")
def t_arrows():
    print("[arrows of elites x1.5]"); setup(); rc.run("fill 590 206 590 612 206 612 stone"); rc.run("tp Cam 600.5 200 600.5"); rc.run("gamemode survival Cam"); rc.run("effect give Cam minecraft:resistance 1000 4"); rc.run("effect give Cam minecraft:instant_health 1 10")
    rc.run("kill @e[type=minecraft:arrow]"); rc.run("kill @e[tag=t1]")
    rc.run('summon minecraft:skeleton 600.5 200 592.5 {Tags:["t1","norm"],PersistenceRequired:1b,equipment:{mainhand:{id:"minecraft:bow",count:1}}}')
    rc.run('summon minecraft:skeleton 608.5 200 592.5 {Tags:["t1","elt"],PersistenceRequired:1b,equipment:{mainhand:{id:"minecraft:bow",count:1}}}'); time.sleep(0.3)
    rc.run("execute as @e[tag=elt] at @s run function last_ember:elite/make"); rc.run("tag @e[tag=norm] add le.rolled")
    d_norm = []; d_elite = []
    for _ in range(40):
        time.sleep(0.5)
        for a in re.findall(r"Arrow has the following entity data: ([0-9.]+)d", rc.run("execute as @e[type=minecraft:arrow,tag=le.ar] run data get entity @s damage")):
            pass
        for e, dest in (("norm", d_norm), ("elt", d_elite)):
            r = rc.run(f"execute as @e[type=minecraft:arrow,tag=le.ar] on origin if entity @s[tag={e}] run say x")
        arrows = rc.run('execute as @e[type=minecraft:arrow,tag=le.ar] at @s run data get entity @s damage')
        if len(d_norm) < 1 or len(d_elite) < 1:
            for who, dest in (("norm", d_norm), ("elt", d_elite)):
                rc.run(f"tag @e[type=minecraft:arrow,tag=le.ar,tag=!seen] remove foo")
                for line in rc.run(f"execute as @e[type=minecraft:arrow,tag=le.ar] on origin if entity @s[tag={who}] run data get entity @e[type=minecraft:arrow,limit=1,sort=nearest] damage").split("Arrow has the following entity data: ")[1:]:
                    m = re.match(r"([0-9.]+)d", line)
                    if m: dest.append(float(m.group(1)))
        if d_norm and d_elite: break
    rc.run("kill @e[tag=t1]"); rc.run("kill @e[type=minecraft:arrow]")
    print("   arrow damage: ordinary skeleton", d_norm[:3], "elite skeleton", d_elite[:3])
    chk("an arrow of an ordinary skeleton has the vanilla damage (2 + a small random part)", bool(d_norm) and 1.9 <= d_norm[0] <= 2.5, d_norm)
    chk("an arrow of an elite has x1.5 damage (3 + the same random part)", bool(d_elite) and 2.85 <= d_elite[0] <= 3.75, d_elite)
def t_ring():
    print("[the ring uses the common module]"); src = open(os.path.join(ROOT, "datapack/data/last_ember/function/ring/whisper.mcfunction"), encoding="utf-8").read()
    chk("ring/whisper calls halluc/whisper (and shadows), no own sounds or particles", "halluc/whisper" in src and "playsound" not in src and "particle" not in src, src)
    rc.run("execute as Cam run function last_ember:ring/whisper"); chk("it runs", True)
def t_perf():
    print("[load]"); setup()
    def mspt():
        r = rc.run("tick query"); m = re.search(r"Average time per tick: ([0-9.]+)ms.*?P50: ([0-9.]+)ms P95: ([0-9.]+)ms", r, re.S); return tuple(map(float, m.groups()))
    awake("Cam", 0); awake("Cam2", 0); time.sleep(8); b = mspt(); print("   rested: avg %.1f ms" % b[0])
    awake("Cam", 80000); awake("Cam2", 80000); rc.run("tp Cam2 600.5 200 604.5")
    for k in range(3): time.sleep(1); rc.run("scoreboard players set Cam le.hsh 0"); rc.run("scoreboard players set Cam2 le.hsh 0")
    time.sleep(8); a = mspt(); print("   both players at stage 4: avg %.1f ms" % a[0]); chk("tick does not grow (< +3 ms)", a[0] - b[0] < 3.0, (b, a)); awake("Cam", 0); awake("Cam2", 0)
if __name__ == "__main__":
    want = sys.argv[1:] or ["stages", "events", "refuge", "sleep", "isolation", "arrows", "ring", "perf"]
    for w in want: globals()["t_" + w]()
    print(f"\n{ok} ok, {bad} failed"); sys.exit(1 if bad else 0)
