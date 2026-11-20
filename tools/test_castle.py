#!/usr/bin/env python3
"""T-028 checks on the R1 world (tools/build/rebuild.sh): the approaches to the Enchanted Castle, the colossi. Clients Cam and Cam2 in the
game (survival; the dev agent clicks the gate).
  build    the biome castle_dream at the lake, the colossi, the stair and the table; the eyes asleep; the gate's click box; the zones
  alone    Cam without the seal on the pier: the warning, the strike leaves 1 heart (2.0), the flight into the knock zone, no fall damage,
           3 s of grace, the eyes lit and asleep again 3 s after
  both     Cam and Cam2 on the pier together: both struck, at different knock points; one after the other
  armour   diamond armour with Protection IV + the knight's Resistance II + absorption: 1 heart, no absorption left
  boat     Cam in a boat in the channel: off the boat, the boat stays, the flight
  leave    in the trigger and out within the second of the warning: no strike
  seal     the seal at Cam, Cam2 within 10: both through (le.cpass), «know the seal» (the eyes dim); Cam2 at 15: only Cam2 struck; the seal
           in the ender chest / on the ground: both struck
  bypass   tp onto the stair, the bridgehead, the table, the rift without the pass: struck and thrown into the lake; bound to bonfire 8 and
           at it: the pass, no strike; the pass kept over a rejoin on the rock; lost after 5 s off the rock
  ambush   one player on the rest platform: a skeleton out of each niche; two players: 2 each; ready again after 10 minutes without players
           within 32 (tick sprint)
  gate     a real click on the gate: the line (counter), the gate stays shut
  night    midnight, normal: the drowned come up in the lake; no monster on the lit pier, stair, bridgehead, bridge
  fade     region/gen/fade_r1 and unfade_r1: the swamp (water W-1..W, mud under), the broken arm, the empty sockets, no strike without
           the seal; back: the lake, the arm, the eyes asleep, the strike again
  restart  the world frozen in the middle of the warning, the server restarted: the warning goes on (struck, thrown), nothing hangs; the
           pass of a player on the rock survives
  perf     two players at the pier (one waking the colossi in turns, one with the pass): castle/* by the profiler
Usage: python3 tools/test_castle.py [build alone both armour boat leave seal bypass ambush gate night fade restart perf]"""
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
M = json.load(open(os.path.join(ROOT, "server/build/r1/castle.json")))
sys.path.insert(0, os.path.join(ROOT, "tools/build")); import castle_plan as P
W = P.W
def passed(cmd): return "passed" in R(cmd)
def num(r):
    m = re.search(r"(-?[0-9.]+)[fdsbL]?$", r.strip()); return float(m.group(1)) if m else None
def hp(p): return num(R(f"data get entity {p} Health"))
def absorb(p): return num(R(f"data get entity {p} AbsorptionAmount"))
def pos(sel):
    v = re.findall(r"(-?\d+\.?\d*)d", R(f"data get entity {sel} Pos")); return [float(x) for x in v] if len(v) == 3 else None
def sc(n, o="le.cas"): return tc.score(n, o)
def tags(p): return R(f"data get entity {p} Tags")
def wait(cond, t=10.0, step=0.2):
    t0 = time.time()
    while time.time() - t0 < t:
        if cond(): return True
        time.sleep(step)
    return cond()
def count(sel):
    m = re.search(r"Count: (\d+)", R(f"execute if entity {sel}")); return int(m.group(1)) if m else 0
PIER = (426.5, W + 2, -33.5); PIER2 = (428.5, W + 2, -35.5)
KX1, KZ1, KX2, KZ2 = P.KNOCK
def in_knock(p):
    q = pos(p); return q is not None and KX1 - 0.5 <= q[0] <= KX2 + 1.5 and KZ1 - 0.5 <= q[2] <= KZ2 + 1.5 and q[1] <= W + 1
FLA = ["forceload add 370 -60 470 10", "forceload add 400 0 490 100"]
def stage(p2=True):
    for p in ("Cam", "Cam2"):
        if not passed(f"execute if entity @a[name={p},tag=le.cinit]"): tc.setc(1, 2, 0, p)
    R("weather clear 100000"); R("time set noon"); R("gamerule advance_time false"); R("difficulty easy")
    for c in FLA: R(c)
    for p in ("Cam", "Cam2"):
        R(f"gamemode survival {p}"); R(f"effect clear {p}"); R(f"effect give {p} minecraft:saturation infinite 1 true")
        R(f"execute as {p} run function last_ember:sleep/set_awake {{ticks:0}}"); R(f"clear {p}")
        R(f"tp {p} 400.5 {W + 2} -52.5 -90 0")
    if not p2: R("gamemode spectator Cam2"); R("tp Cam2 400 200 100")
    wait(lambda: passed("execute if loaded 420 0 -50") and passed("execute if loaded 424 0 -23") and passed("execute if loaded 450 0 60"), 40)
    R("function last_ember:castle/reset"); time.sleep(1.5)
def full(p):
    R(f"effect give {p} minecraft:instant_health 1 10 true"); time.sleep(0.4)
def unstage():
    for c in FLA: R(c.replace("add", "remove"))
def strike_ok(p, label, extra=None):
    """the warning (le.cwake), then 1 heart, the flight, the knock zone, no fall damage"""
    chk(f"{label}: the warning (le.cwake) within 0.5 s", wait(lambda: "le.cwake" in tags(p) or "le.cfly" in tags(p), 1.5))
    chk(f"{label}: the eyes lit", wait(lambda: passed("execute if block %d %d %d minecraft:pearlescent_froglight" % tuple(M["dp"]["eyes"][0])), 1.5))
    got = wait(lambda: "le.cfly" in tags(p), 2.5)
    h = hp(p); a = absorb(p)
    chk(f"{label}: struck after ~1 s, 1 heart left (2.0, absorption 0)", got and h is not None and abs(h - 2.0) < 0.6 and (a or 0) == 0, (h, a))
    land = wait(lambda: "le.cfly" not in tags(p), 3)
    q = pos(p); h2 = hp(p)
    chk(f"{label}: landed in the water of the knock zone after ~1.2 s, no fall damage", land and in_knock(p) and h2 is not None and h2 >= h - 0.01, (q, h, h2))
    return q

# ---------------------------------------------------------------- suites
def t_build():
    print("[build]"); stage()
    for (x, y, z) in ((400, 112, -20), (425, 140, -46), (440, 150, -34), (450, 170, 60)):
        chk(f"biome castle_dream at {(x, y, z)}", passed(f"execute if biome {x} {y} {z} last_ember:castle_dream"))
    chk("the eyes asleep (8 sockets)", all(passed("execute if block %d %d %d minecraft:polished_blackstone" % tuple(e)) for e in M["dp"]["eyes"]))
    chk("the click box of the gate", count("@e[type=minecraft:interaction,tag=le.cgate]") == 1)
    chk("the pier deck, the causeway, the bridge deck", passed(f"execute unless block 425 {W + 1} -34 minecraft:air") and passed(f"execute unless block 395 {W + 1} -52 minecraft:air") and passed("execute unless block 451 162 17 minecraft:air"))
    chk("the portcullis shut", passed("execute if block 451 165 31 minecraft:iron_bars"))
    chk("the sword's sign", "Короли не узнали" in R("data get block %d %d %d front_text" % tuple(M["sword"]["sign"])))
    chk("the mid of the bridge in storage for the castle task", "pos" in R("data get storage last_ember:r1 m.castle_bridge_mid"))
    unstage()

def t_alone():
    print("[alone: Cam without the seal on the pier]"); stage(p2=False); full("Cam")
    R("tp Cam %s %s %s 90 0" % PIER); t0 = time.time()
    strike_ok("Cam", "alone")
    chk("3 s of grace: no new warning while swimming back towards the channel", not wait(lambda: "le.cwake" in tags("Cam"), 2.0))
    chk("the eyes asleep again ~3 s after the strike", wait(lambda: passed("execute if block %d %d %d minecraft:polished_blackstone" % tuple(M["dp"]["eyes"][0])), 6))
    R("tp Cam 400.5 %d -52.5" % (W + 2)); unstage()

def t_both():
    print("[both on the pier at once, then one after the other]"); stage(); full("Cam"); full("Cam2")
    R("tp Cam %s %s %s 90 0" % PIER); R("tp Cam2 %s %s %s 90 0" % PIER2)
    wait(lambda: "le.cfly" in tags("Cam") and "le.cfly" in tags("Cam2"), 3)
    h1, h2 = hp("Cam"), hp("Cam2")
    chk("both struck to 1 heart", abs(h1 - 2) < 0.6 and abs(h2 - 2) < 0.6, (h1, h2))
    wait(lambda: "le.cfly" not in tags("Cam") and "le.cfly" not in tags("Cam2"), 3); time.sleep(0.2)
    a, b = pos("Cam"), pos("Cam2")
    chk("both in the knock zone, at different points (>= 3 apart)", in_knock("Cam") and in_knock("Cam2") and math.hypot(a[0] - b[0], a[2] - b[2]) >= 3, (a, b))
    time.sleep(3.5); R("tp Cam2 400.5 %d -52.5" % (W + 2)); full("Cam"); R("tp Cam %s %s %s 90 0" % PIER)
    strike_ok("Cam", "one after the other: Cam")
    R("tp Cam 400.5 %d -52.5" % (W + 2)); full("Cam2"); time.sleep(3.5); R("tp Cam2 %s %s %s 90 0" % PIER)
    strike_ok("Cam2", "then Cam2"); R("tp Cam2 400.5 %d -52.5" % (W + 2)); unstage()

def t_armour():
    print("[armour, Protection IV, the knight's Resistance, absorption]"); stage(p2=False)
    tc.setc(1, 1, 6, "Cam"); R("gamemode survival Cam"); R("effect give Cam minecraft:saturation infinite 1 true")
    for sl, it in (("armor.head", "diamond_helmet"), ("armor.chest", "diamond_chestplate"), ("armor.legs", "diamond_leggings"), ("armor.feet", "diamond_boots")):
        R(f'item replace entity Cam {sl} with minecraft:{it}[minecraft:enchantments={{"minecraft:protection":4}}]')
    R("effect give Cam minecraft:absorption 60 1 true"); full("Cam"); time.sleep(1.5)
    res = R("data get entity Cam active_effects"); print("     effects:", ", ".join(re.findall(r'id: "minecraft:([a-z_]+)"', res)), "absorption", absorb("Cam"))
    chk("the knight has Resistance, absorption on", "resistance" in res and (absorb("Cam") or 0) > 0)
    R("tp Cam %s %s %s 90 0" % PIER); strike_ok("Cam", "armour + Resistance + absorption")
    R("clear Cam"); R("effect clear Cam"); tc.setc(1, 2, 0, "Cam"); R("tp Cam 400.5 %d -52.5" % (W + 2)); unstage()

def t_boat():
    print("[a boat in the channel]"); stage(p2=False); full("Cam")
    R("kill @e[type=minecraft:oak_boat,tag=le.ctest]")
    R("summon minecraft:oak_boat 413.5 %d -33.5 {Tags:[\"le.ctest\"],Rotation:[-90f,0f]}" % W); time.sleep(0.5)
    R("tp Cam 413.5 %d -33.5" % (W + 1)); R("ride Cam mount @e[type=minecraft:oak_boat,tag=le.ctest,limit=1]")
    inb = lambda: passed("execute as Cam on vehicle if entity @s[type=minecraft:oak_boat,tag=le.ctest]")
    chk("Cam in the boat", wait(inb, 2))
    strike_ok("Cam", "boat")
    chk("off the boat, the boat stays in the channel", not inb() and count("@e[type=minecraft:oak_boat,tag=le.ctest,x=400,y=100,z=-45,dx=32,dy=30,dz=24]") == 1)
    R("kill @e[type=minecraft:oak_boat,tag=le.ctest]"); R("tp Cam 400.5 %d -52.5" % (W + 2)); unstage()

def t_leave():
    print("[out of the trigger within the second of the warning]"); stage(p2=False); full("Cam"); h0 = hp("Cam")
    R("tp Cam %s %s %s 90 0" % PIER)
    chk("the warning", wait(lambda: "le.cwake" in tags("Cam"), 1.5))
    R("tp Cam 400.5 %d -52.5" % (W + 2)); time.sleep(2)
    chk("no strike, no flight", "le.cfly" not in tags("Cam") and "le.cwake" not in tags("Cam") and hp("Cam") >= h0 - 0.01, hp("Cam")); unstage()

def give_seal(p): R(f'execute as {p} run function last_ember:cemetery/give {{key:"seal"}}'); time.sleep(0.4)
def t_seal():
    print("[the seal]"); stage(); full("Cam"); full("Cam2")
    give_seal("Cam"); chk("Cam carries the seal (le.sealh)", wait(lambda: "le.sealh" in tags("Cam"), 2))
    R("scoreboard players set #recog le.cas 0")
    R("tp Cam %s %s %s 90 0" % PIER); R("tp Cam2 %s %s %s 90 0" % PIER2)
    chk("both let through (le.cpass), nobody waking", wait(lambda: "le.cpass" in tags("Cam") and "le.cpass" in tags("Cam2"), 2) and "le.cwake" not in tags("Cam2"))
    chk("«the colossi know the seal»: the eyes dim, the line not again within 60 s", passed("execute if block %d %d %d minecraft:crying_obsidian" % tuple(M["dp"]["eyes"][0])) and sc("#recog") > sc("#gt") + 1000)
    chk("the eyes asleep again after 2 s", wait(lambda: passed("execute if block %d %d %d minecraft:polished_blackstone" % tuple(M["dp"]["eyes"][0])), 4))
    time.sleep(2); chk("nobody struck", hp("Cam") > 15 and hp("Cam2") > 15 and "le.cfly" not in tags("Cam2"))
    # Cam2 at 15 from the carrier
    R("tp Cam 400.5 %d -52.5" % (W + 2)); R("tp Cam2 400.5 %d -50.5" % (W + 2)); time.sleep(6.5)
    chk("the pass lost after 5 s off the rock and the trigger", "le.cpass" not in tags("Cam") and "le.cpass" not in tags("Cam2"))
    R("tp Cam 412.5 %d -24.5" % (W + 1)); R("tp Cam2 %s %s %s 90 0" % PIER2)
    strike_ok("Cam2", "Cam2 15 from the carrier: struck")
    chk("the carrier (out of the trigger) not struck", "le.cfly" not in tags("Cam") and hp("Cam") > 15)
    # the seal in the ender chest / on the ground
    R("tp Cam 400.5 %d -52.5" % (W + 2)); R("tp Cam2 400.5 %d -50.5" % (W + 2)); time.sleep(3.5); full("Cam"); full("Cam2")
    R('clear Cam *[minecraft:custom_data~{le_citem:"seal"}]')
    R('item replace entity Cam enderchest.0 with minecraft:stick[minecraft:custom_data={le_citem:"seal",le_keep:1b,gen:1}]')
    time.sleep(0.5); chk("the seal in the ender chest: no carrier", "le.sealh" not in tags("Cam"))
    R("tp Cam %s %s %s 90 0" % PIER); time.sleep(0.1); R("tp Cam2 %s %s %s 90 0" % PIER2)
    wait(lambda: "le.cfly" in tags("Cam") and "le.cfly" in tags("Cam2"), 3)
    chk("seal in the ender chest: both struck", abs(hp("Cam") - 2) < 0.6 and abs(hp("Cam2") - 2) < 0.6, (hp("Cam"), hp("Cam2")))
    wait(lambda: "le.cfly" not in tags("Cam") and "le.cfly" not in tags("Cam2"), 3); time.sleep(3.5)
    R("item replace entity Cam enderchest.0 with minecraft:air"); full("Cam"); full("Cam2")
    R('summon minecraft:item 426.5 %d -32.5 {Tags:["le.ctest"],PickupDelay:32767,Item:{id:"minecraft:stick",count:1,components:{"minecraft:custom_data":{le_citem:"seal",le_keep:1b,gen:1}}}}' % (W + 2))
    R("tp Cam %s %s %s 90 0" % PIER); time.sleep(0.1); R("tp Cam2 %s %s %s 90 0" % PIER2)
    wait(lambda: "le.cfly" in tags("Cam") and "le.cfly" in tags("Cam2"), 3)
    chk("seal on the ground (on the pier): both struck", abs(hp("Cam") - 2) < 0.6 and abs(hp("Cam2") - 2) < 0.6, (hp("Cam"), hp("Cam2")))
    R("kill @e[type=minecraft:item,tag=le.ctest]"); R("function last_ember:cemetery/reset"); time.sleep(3.5)
    R("tp Cam 400.5 %d -52.5" % (W + 2)); R("tp Cam2 400.5 %d -50.5" % (W + 2)); unstage()

def t_bypass():
    print("[the bypass]"); stage(p2=False)
    st = [c for c in P.stair()[0]]
    f3 = [c for c in st if c[3] == 146][0]
    from scanio import Scan
    S = Scan(os.path.join(ROOT, "server/build/r1/castle_post.bin"))
    def gy(x, z): return int(S.ground[int(z) - S.z0, int(x) - S.x0]) + 1
    for name, (x, y, z) in (("the stair (F3)", (f3[0] + 0.5, f3[3] + 1, f3[1] + 1.5)), ("the bridgehead", (455.5, P.PRED_Y + 1, -30.5)),
                            ("the table", (450.5, M["P"] + 1, 60.5)), ("the rift floor", (470.5, None, 18.5)), ("the peak", (472.5, None, -62.5))):
        full("Cam")
        R(f"tp Cam {x} {y if y is not None else gy(x, z)} {z}")
        strike_ok("Cam", f"tp onto {name} without the pass")
        time.sleep(3.2)
    # bound to bonfire 8, at it: the pass
    full("Cam"); R("scoreboard players set Cam le.sb 8"); R("tp Cam 440.5 163 -12.5")
    chk("bound to bonfire 8 and at it: the pass, no strike", wait(lambda: "le.cpass" in tags("Cam"), 2) and not wait(lambda: "le.cwake" in tags("Cam"), 2))
    R("tp Cam 455.5 163 -30.5"); time.sleep(2); chk("walking the bridgehead with the pass: no strike", "le.cwake" not in tags("Cam") and "le.cfly" not in tags("Cam"))
    # a rejoin on the rock keeps the pass
    R("kick Cam"); time.sleep(3)
    subprocess.Popen(f"cd {ROOT} && python3 -I tools/client_launch.py > server/client.out 2>&1", shell=True)
    chk("Cam back", wait(lambda: re.search(r"\bCam(?!2)\b", R("list")) is not None, 120, 2)); time.sleep(3); R("gamemode survival Cam")
    time.sleep(4); chk("the pass kept over the rejoin on the rock, no strike", "le.cpass" in tags("Cam") and not wait(lambda: "le.cwake" in tags("Cam"), 2))
    R("tp Cam 400.5 %d -52.5" % (W + 2)); time.sleep(6)
    chk("the pass lost after 5 s off the rock", "le.cpass" not in tags("Cam"))
    R("scoreboard players set Cam le.sb 7"); unstage()

def t_ambush():
    print("[the ambush]"); stage()
    R("kill @e[type=minecraft:skeleton,tag=le.camb]"); R("difficulty easy"); R("scoreboard players set #amb le.cas 0")
    rest = M["dp"]["rest"]
    R("tag Cam add le.cpass"); R("tag Cam2 add le.cpass"); R("gamemode spectator Cam2"); R("tp Cam2 400 200 100")
    R("tp Cam %.1f %d %.1f" % (rest[0], rest[1], rest[2]))
    chk("one player on the platform: a skeleton out of each niche (2)", wait(lambda: count("@e[type=minecraft:skeleton,tag=le.camb]") == 2, 3), count("@e[type=minecraft:skeleton,tag=le.camb]"))
    time.sleep(2); sk = [pos(f"@e[type=minecraft:skeleton,tag=le.camb,limit=1,sort=nearest,x={rest[0]},y={rest[1]},z={rest[2]}]")]
    chk("they jump down onto the platform", sk[0] is not None and abs(sk[0][1] - rest[1]) < 1.5 and P.REST[0] - 1.5 <= sk[0][0] <= P.REST[2] + 1.5, sk)
    time.sleep(2); chk("not again while the ambush is spent", count("@e[type=minecraft:skeleton,tag=le.camb]") <= 2 and sc("#amb") == 1)
    R("kill @e[type=minecraft:skeleton,tag=le.camb]"); R("scoreboard players set #amb le.cas 0")
    R("gamemode survival Cam2"); R("tp Cam %.1f %d %.1f" % (rest[0] + 30, P.PRED_Y + 1, rest[2] + 10)); R("tp Cam2 %.1f %d %.1f" % (rest[0] + 30, P.PRED_Y + 1, rest[2] + 12)); time.sleep(1)
    R("tp Cam2 436.5 137 -31.5"); R("tp Cam %.1f %d %.1f" % (rest[0], rest[1], rest[2]))      # Cam2 in the tunnel of F2, 8 from the platform
    chk("two players within 16: two out of each niche (4)", wait(lambda: count("@e[type=minecraft:skeleton,tag=le.camb]") == 4, 3), count("@e[type=minecraft:skeleton,tag=le.camb]"))
    R("kill @e[type=minecraft:skeleton,tag=le.camb]")
    R("tp Cam 400.5 %d -52.5" % (W + 2)); R("tp Cam2 300 200 200"); R("tp Cam 300 200 205")       # nobody within 32
    R("scoreboard players set #ambt le.cas 0"); R("tick sprint 12100")
    chk("10 minutes without players within 32: the ambush ready again", wait(lambda: sc("#amb") == 0, 120, 1), (sc("#amb"), sc("#ambt")))
    R("tick sprint stop"); R("tp Cam %.1f %d %.1f" % (rest[0], rest[1], rest[2]))
    chk("and it springs again", wait(lambda: count("@e[type=minecraft:skeleton,tag=le.camb]") >= 2, 3))
    R("kill @e[type=minecraft:skeleton,tag=le.camb]"); R("tag Cam remove le.cpass"); R("tag Cam2 remove le.cpass"); R("tp Cam 400.5 %d -52.5" % (W + 2)); R("tp Cam2 400.5 %d -50.5" % (W + 2)); unstage()

def t_gate():
    print("[the gate of the barbican]"); stage(p2=False)
    g = M["barbican"]["gate"]; R("tag Cam add le.cpass")
    R("tp Cam %.1f %d %.1f 0 0" % (g[0], g[1], g[2] - 3)); time.sleep(1.5)
    R("execute as Cam at @s anchored eyes run tp @s ~ ~ ~ facing %.1f %.1f %.1f" % (g[0], g[1] + 1.5, g[2] + 0.6)); time.sleep(0.6)
    n0 = sc("#gates") or 0
    for _ in range(3):
        time.sleep(1.0); tc.act("Cam", "!use")
        if wait(lambda: (sc("#gates") or 0) > n0, 2): break
    chk("a real click: the line (counter +1)", (sc("#gates") or 0) == n0 + 1, (n0, sc("#gates")))
    chk("the gate stays shut", passed("execute if block 451 165 31 minecraft:iron_bars"))
    R("tag Cam remove le.cpass"); R("tp Cam 400.5 %d -52.5" % (W + 2)); unstage()

def lake_faded():
    x, z = 384, -10
    fl = int(M["checks"]["W"]) - 4
    return passed(f"execute if block {x} {W - 2} {z} minecraft:mud") and not passed(f"execute if block {x} {W - 3} {z} minecraft:water")
def t_fade():
    print("[the fade of R1: the lake]"); stage(p2=False)
    R("function last_ember:region/gen/fade_r1"); time.sleep(3)
    chk("the swamp: mud under W-1, water W-1..W", wait(lake_faded, 6) and passed(f"execute if block 384 {W} -10 minecraft:water"))
    arm = M["colossi"]["s"]["arm"]; pa = arm[len(arm) // 2]
    chk("the raised arm of the south colossus broken off (air), lying in the water", passed("execute if block %d %d %d minecraft:air" % tuple(pa)) and passed(f"execute unless block 410 {W} -28 minecraft:water"))
    chk("the sockets empty", all(passed("execute if block %d %d %d minecraft:air" % tuple(e)) for e in M["dp"]["eyes"]))
    full("Cam"); R("tp Cam %s %s %s 90 0" % PIER)
    chk("the colossi asleep for good: no warning without the seal", not wait(lambda: "le.cwake" in tags("Cam") or "le.cfly" in tags("Cam"), 2.5) and hp("Cam") > 15)
    R("tp Cam 455.5 163 -30.5"); chk("on the rock without the pass: nothing", not wait(lambda: "le.cwake" in tags("Cam"), 2))
    R("tp Cam 400.5 %d -52.5" % (W + 2))
    R("function last_ember:region/gen/unfade_r1"); time.sleep(3)
    chk("back: the lake (water at W-3), the arm, the eyes asleep", wait(lambda: passed(f"execute if block 384 {W - 3} -10 minecraft:water"), 6) and passed("execute unless block %d %d %d minecraft:air" % tuple(pa))
        and wait(lambda: passed("execute if block %d %d %d minecraft:polished_blackstone" % tuple(M["dp"]["eyes"][0])), 4))
    full("Cam"); R("tp Cam %s %s %s 90 0" % PIER); strike_ok("Cam", "after the unfade the colossi wake again")
    R("tp Cam 400.5 %d -52.5" % (W + 2)); unstage()

def t_restart():
    print("[restart in the middle of the warning (the world frozen first) and after the passage]"); stage()
    R("tag Cam2 add le.cpass"); R("tp Cam2 455.5 163 -30.5")
    full("Cam"); R("tp Cam %s %s %s 90 0" % PIER); wait(lambda: "le.cwake" in tags("Cam"), 1.5); time.sleep(0.3); R("tick freeze")
    cw = sc("Cam", "le.cw"); print("     frozen with", cw, "ticks of the warning left")
    chk("frozen in the middle of the warning", "le.cwake" in tags("Cam") and cw is not None and 0 < cw < 20, cw)
    restart(); stage_light(); R("gamemode survival Cam"); R("gamemode survival Cam2")
    chk("after the restart the warning goes on: struck, thrown, nothing hangs", wait(lambda: "le.cwake" not in tags("Cam") and "le.cfly" not in tags("Cam"), 15)
        and in_knock("Cam") and wait(lambda: passed("execute if block %d %d %d minecraft:polished_blackstone" % tuple(M["dp"]["eyes"][0])), 8), (tags("Cam"), pos("Cam")))
    chk("the pass of Cam2 on the rock survived", "le.cpass" in tags("Cam2") and "le.cfly" not in tags("Cam2"))
    full("Cam"); R("tp Cam 400.5 %d -52.5" % (W + 2)); time.sleep(4)
    R("tp Cam %s %s %s 90 0" % PIER)
    strike_ok("Cam", "after the restart the colossi work")
    R("tag Cam2 remove le.cpass"); R("tp Cam 400.5 %d -52.5" % (W + 2)); R("tp Cam2 400.5 %d -50.5" % (W + 2)); unstage()
def stage_light():
    R("weather clear 100000"); R("time set noon"); R("gamerule advance_time false")
    for c in FLA: R(c)
    wait(lambda: passed("execute if loaded 420 0 -50") and passed("execute if loaded 424 0 -23"), 40)
def restart():
    subprocess.run([os.path.join(ROOT, "tools/server.sh"), "stop"], capture_output=True); time.sleep(8)
    subprocess.Popen(f"cd {ROOT} && tools/server.sh start > server/console.out 2>&1", shell=True)
    for _ in range(90):
        time.sleep(2)
        try:
            if "players online" in R("list"): break
        except Exception: pass
    subprocess.run("pkill -f net.minecraft.client.main.Main", shell=True); time.sleep(3)
    subprocess.Popen(f"cd {ROOT} && python3 -I tools/client_launch.py > server/client.out 2>&1", shell=True)
    subprocess.Popen(f"cd {ROOT} && python3 -I tools/client_launch.py --name Cam2 --dir server/client2 --mem 1500M --size 640x360 > server/client2.out 2>&1", shell=True)
    for _ in range(90):
        time.sleep(2)
        try:
            l = R("list")
            if "Cam2" in l and re.search(r"\bCam(?!2)\b", l): break
        except Exception: pass
    time.sleep(6)
def mspt():
    m = re.search(r"([0-9.]+)\s*ms", R("tick query")); return float(m.group(1)) if m else None
def prof(sec=10):
    import glob, zipfile
    before = set(glob.glob(os.path.join(ROOT, "server/debug/profiling/*.zip"))); R("perf start")
    time.sleep(sec + 1); R("perf stop"); new = []
    for _ in range(40):
        new = sorted(set(glob.glob(os.path.join(ROOT, "server/debug/profiling/*.zip"))) - before)
        if new: break
        time.sleep(0.5)
    if not new: return {}
    time.sleep(1.0); t = zipfile.ZipFile(new[-1]).read("server/profiling.txt").decode()
    span = float(re.search(r"Time span: (\d+) ms", t).group(1)); ticks = float(re.search(r"Tick span: (\d+) ticks", t).group(1))
    out = {"tick": span / ticks}
    for m in re.finditer(r"\[05\][ |]*function (last_ember:[a-z_/]+)\(\d+/\d+\) - [0-9.]+%/([0-9.]+)%", t): out[m.group(1)] = span * float(m.group(2)) / 100 / ticks
    return out
def t_perf():
    print("[perf: two players at the pier (the pass, Cam2 with the seal): the background; then Cam thrown again and again]"); stage()
    give_seal("Cam2"); R("tp Cam %s %s %s 90 0" % PIER); R("tp Cam2 428.5 %d -31.5" % (W + 2)); time.sleep(3)
    p0 = prof(10); ms = [mspt() for _ in range(3)]
    f = sum(v for k, v in p0.items() if k.startswith("last_ember:castle/"))
    print(f"     background: castle/* {f:.3f} ms per tick, server tick {p0.get('tick', 0):.1f} ms, tick query {ms} ms")
    for k, v in sorted(((k, v) for k, v in p0.items() if k.startswith("last_ember:castle")), key=lambda kv: -kv[1])[:5]: print(f"       {k} {v:.3f}")
    chk("background (2 players at the pier): castle/* under 0.5 ms per tick (the garden's limit), the tick keeps up", 0 <= f < 0.5 and ms[0] is not None and max(ms) < 50, (f, ms))
    R('clear Cam2 *[minecraft:custom_data~{le_citem:"seal"}]'); R("tag Cam2 add le.cpass"); R("tag Cam remove le.cpass")
    import threading
    stop = [False]; n = [0]
    def loop():
        while not stop[0]:
            full("Cam"); R("scoreboard players set Cam le.cg 0"); R("tp Cam %s %s %s 90 0" % PIER); n[0] += 1; time.sleep(3.2)
    th = threading.Thread(target=loop); th.start()
    time.sleep(2); p1 = prof(10); stop[0] = True; th.join()
    f1 = sum(v for k, v in p1.items() if k.startswith("last_ember:castle/"))
    print(f"     thrown every 3.2 s: castle/* {f1:.3f} ms per tick on average, about {f1 * 200 / (10 / 3.2):.1f} ms per throw (24 teleports of the player)")
    for k, v in sorted(((k, v) for k, v in p1.items() if k.startswith("last_ember:castle")), key=lambda kv: -kv[1])[:5]: print(f"       {k} {v:.3f}")
    chk("a throw costs under 60 ms in all (mostly the teleports of the player)", f1 * 200 / (10 / 3.2) < 60, f1)
    R("function last_ember:cemetery/reset"); R("tag Cam2 remove le.cpass"); R("tp Cam 400.5 %d -52.5" % (W + 2)); R("tp Cam2 400.5 %d -50.5" % (W + 2)); unstage()

def t_night():
    print("[night: the drowned at the causeway, nothing on the lit pier / stair / bridgehead / bridge]"); stage(p2=False)
    R("difficulty normal"); R("time set 18000"); R("kill @e[type=#last_ember:monsters,x=330,y=60,z=-130,dx=250,dy=200,dz=260]")
    R("tag Cam add le.cpass"); R("effect give Cam minecraft:resistance infinite 255 true"); R("effect give Cam minecraft:invisibility infinite 0 true")
    R("tp Cam 396.5 %d -52.5" % (W + 2)); time.sleep(2); R("tick rate 100"); time.sleep(70); R("tick rate 20")
    lit = {"the pier": (P.PIER[0], W, P.PIER[1], P.PIER[2], W + 5, P.PIER[3]),
           "the stair and the rest platform": (P.REST[0] - 1, W + 1, P.LANE_A[0] - 1, P.FACE_X + 15, P.PRED_Y + 3, P.LANE_B[1] + 1),
           "the bridgehead": (P.PRED[0], P.PRED_Y + 1, P.PRED[1], P.PRED[2], P.PRED_Y + 6, P.PRED[3]),
           "the bridge": (P.BRIDGE_X[0], P.PRED_Y + 1, P.RIFT[1], P.BRIDGE_X[1], P.PRED_Y + 6, P.RIFT[3])}
    dr = count("@e[type=minecraft:drowned,x=370,y=100,z=-58,dx=62,dy=20,dz=64]")
    print("     monsters around:", R("execute if entity @e[type=#last_ember:monsters,x=330,y=60,z=-130,dx=250,dy=200,dz=260]"), " drowned in the lake:", dr)
    chk("the drowned come up in the lake at night", dr >= 1, dr)
    for name, (x1, y1, z1, x2, y2, z2) in lit.items():
        n = count("@e[type=#last_ember:monsters,x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d]" % (x1, y1, z1, x2 - x1, y2 - y1, z2 - z1))
        chk(f"no monsters on {name} (lit)", n == 0, n)
    R("kill @e[type=#last_ember:monsters,x=330,y=60,z=-130,dx=250,dy=200,dz=260]"); R("effect clear Cam"); R("tag Cam remove le.cpass")
    R("time set noon"); R("difficulty easy"); unstage()

SUITES = dict(build=t_build, alone=t_alone, both=t_both, armour=t_armour, boat=t_boat, leave=t_leave, seal=t_seal, bypass=t_bypass,
              ambush=t_ambush, gate=t_gate, night=t_night, fade=t_fade, restart=t_restart, perf=t_perf)
if __name__ == "__main__":
    for a in sys.argv[1:] or list(SUITES):
        SUITES[a]()
    print(f"castle: {ok} ok, {bad} failed")
