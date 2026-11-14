#!/usr/bin/env python3
"""T-023 checks on the R1 world (tools/build/rebuild.sh): Altar I in the Circle of the Weepers, the event, the fade of the region,
altar/reset {chapter:1}, a restart. Clients Cam (carrier) and Cam2 in the game.
Usage: python3 tools/test_weepers.py [peds event fade reset restart zones perf]"""
import importlib.util, os, re, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
ok = bad = 0
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n, flush=True)
    else: bad += 1; print("  FAIL", n, e, flush=True)
score = tc.score
CX, Y, CZ = -420, 111, -180
PEDS = {"thread_labyrinth": (-414, -186), "tear_creaker": (-411, -180), "signet_king": (-414, -174), "crown_witches": (-420, -171)}
FADED = (2, 3, 4, 5, 7, 8, 9); KEPT = (6, 10)
def sto(path): return rc.run(f"data get storage last_ember:{path}")
def passed(cmd): return "passed" in rc.run(cmd)
def filled(): return score("#fill_weepers", "le.alt")
def hand_key(p, kid): rc.run(f"execute as {p} run function last_ember:altar/gen/hand_dispatch {{id:\"{kid}\"}}")
def hand(p, kid): return passed(f"execute if items entity {p} weapon.mainhand *[minecraft:custom_data~{{le_key:\"{kid}\"}}]")
def hand_empty(p): return not passed(f"execute if items entity {p} weapon.mainhand *")
def stand(kid, back=2.6):
    px, pz = PEDS[kid]; dx, dz = px - CX, pz - CZ; L = (dx * dx + dz * dz) ** 0.5
    return px + 0.5 + dx / L * back, pz + 0.5 + dz / L * back
def click(p, kid):
    px, pz = PEDS[kid]; sx, sz = stand(kid); tc.face(p, sx, Y, sz, px + 0.5, Y + 0.7, pz + 0.5); time.sleep(0.35); tc.act(p, "!use"); time.sleep(0.5)
def carrier(p="Cam"):
    for q in ("Cam", "Cam2"): rc.run(f"tag {q} remove le.carrier"); rc.run(f"clear {q} minecraft:trial_key")
    rc.run("data remove storage last_ember:ember carrier"); rc.run(f"execute as {p} run function last_ember:ember/give_to_me")
def wait(cond, t=10.0, step=0.5):
    t0 = time.time()
    while time.time() - t0 < t:
        if cond(): return True
        time.sleep(step)
    return cond()
def stage():
    rc.run(f"tp Cam {CX + 6}.5 {Y} {CZ + 12}.5"); rc.run(f"tp Cam2 {CX + 8}.5 {Y} {CZ + 12}.5")
    wait(lambda: passed(f"execute if loaded {CX - 30} {Y} {CZ - 30}") and passed(f"execute if loaded {CX + 30} {Y} {CZ + 30}"), 20)
    rc.run("difficulty normal"); rc.run("weather clear 100000"); rc.run("kill @e[type=item]")
    tc.setc(1, 1, 0, "Cam"); tc.setc(2, 2, 0, "Cam2")
    for p in ("Cam", "Cam2"): rc.run(f"gamemode survival {p}"); rc.run(f"effect give {p} minecraft:resistance infinite 4 true")
    rc.run("function last_ember:altar/reset {chapter:1}"); rc.run("function last_ember:altar/set_chapters {n:0}"); rc.run("scoreboard players set #tiersync le.alt 1")
    wait(lambda: not passed("execute if function last_ember:weepers/gen/probe_up") and score("#wpc", "le.alt") == 1, 8)
    for n in FADED + KEPT: rc.run(f"data modify storage last_ember:bonfires by.b{n} merge value {{state:1}}")   # as if lit on the way
    carrier()
CANDLES = []
def rc_candles(lit):
    """lit (or unlit) candles at the statues' feet: the cells are found once (ring r 10.5..17.5 at the floor), then only they are asked"""
    if not CANDLES:
        for x in range(CX - 18, CX + 19):
            for z in range(CZ - 18, CZ + 19):
                if 10.5 <= ((x - CX) ** 2 + (z - CZ) ** 2) ** 0.5 <= 17.5 and passed(f"execute if block {x} {Y + 1} {z} minecraft:candle"): CANDLES.append((x, z))
    return sum(passed(f"execute if block {x} {Y + 1} {z} minecraft:candle[lit={'true' if lit else 'false'}]") for x, z in CANDLES)
def lit(n): return "state: 1" in sto(f"bonfires by.b{n}")

def t_peds():
    print("[pedestals]"); stage(); give = lambda p, k: rc.run(f"execute as {p} run function last_ember:altar/give_key {{id:\"{k}\"}}")
    hand_key("Cam2", "tear_creaker"); click("Cam2", "signet_king")
    chk("a key of another pedestal is refused", filled() == 0 and hand("Cam2", "tear_creaker"), (filled(), hand("Cam2", "tear_creaker")))
    rc.run("clear Cam2"); hand_key("Cam2", "signet_king"); click("Cam2", "signet_king")
    chk("the right key stands on its pedestal", filled() == 1 and hand_empty("Cam2"), filled())
    click("Cam2", "signet_king"); chk("an empty hand takes it back", filled() == 0 and hand("Cam2", "signet_king"))
    # both players at once, different pedestals
    rc.run("clear Cam2"); hand_key("Cam", "thread_labyrinth"); hand_key("Cam2", "crown_witches")
    for p, k in (("Cam", "thread_labyrinth"), ("Cam2", "crown_witches")):
        px, pz = PEDS[k]; sx, sz = stand(k); tc.face(p, sx, Y, sz, px + 0.5, Y + 0.7, pz + 0.5)
    time.sleep(0.4); tc.act("Cam", "!use"); tc.act("Cam2", "!use"); time.sleep(0.8)
    chk("two players place two keys in the same tick", filled() == 2, filled())
    for k in ("thread_labyrinth", "crown_witches"): click("Cam" if k == "thread_labyrinth" else "Cam2", k)
    chk("taken back", filled() == 0)

def t_event():
    print("[the event]"); stage()
    rc.run("forceload add -680 -210 -630 -170")           # the west pass: the gate template is placed when its chunk is loaded
    G0 = {k: int(tc.num(sto(f"keys k.{k}.gen")) or 0) for k in PEDS}
    rc_candles(True)                                      # find the candle cells before the event
    rc.run(f"tp Cam {CX + 20}.5 120 {CZ + 30}.5")         # the carrier is away (> 10)
    for k in PEDS: hand_key("Cam2", k); time.sleep(0.2); click("Cam2", k)
    time.sleep(2.2)
    chk("4 keys, the carrier away: no event", filled() == 4 and "ev: -1" in sto("altars a.weepers") and score("#chapters", "le.alt") == 0, (filled(), sto("altars a.weepers")))
    rc.run(f"tp Cam {CX + 7}.5 {Y} {CZ + 3}.5"); t0 = time.time()
    chk("the carrier within 10: the event starts", wait(lambda: "ev: -1" not in sto("altars a.weepers"), 3), sto("altars a.weepers"))
    k = "signet_king"; click("Cam2", k); chk("keys cannot be taken during the event", filled() == 4)
    chk("tears are falling (tick 1..200)", wait(lambda: 5 < (score("#ev", "le.alt") or 0) < 200, 5))
    wait(lambda: 205 < (score("#ev", "le.alt") or 0) < 238, 14, 0.2)
    chk("candles out after tick 200", rc_candles(True) == 0, rc_candles(True))
    chk("the event ends: done, chapters 1", wait(lambda: "done: 1b" in sto("altars a.weepers"), 12) and score("#chapters", "le.alt") == 1, (sto("altars a.weepers"), score("#chapters", "le.alt")))
    print("     event length", round(time.time() - t0, 1), "s")
    chk("the Weepers lowered their hands (template 'down' everywhere)", not passed("execute if function last_ember:weepers/gen/probe_down"))
    chk("the core burns", passed(f"execute if block {CX} {Y + 5} {CZ} #last_ember:weepers_core_on"))
    chk("the candles are lit again", rc_candles(True) > 20 and rc_candles(False) == 0, (rc_candles(True), rc_candles(False)))
    chk("no vanilla lightning, no fire in the crown", not passed("execute if entity @e[type=lightning_bolt]") and not passed(f"execute positioned {CX} {Y + 28} {CZ} if block ~ ~ ~ fire"))
    time.sleep(1.5)
    chk("tier 1 for both players", score("Cam", "le.tier") == 1 and score("Cam2", "le.tier") == 1, (score("Cam", "le.tier"), score("Cam2", "le.tier")))
    chk("the keys stay for good, gen+1", all("st: 2" in sto(f"keys k.{k}") and int(tc.num(sto(f"keys k.{k}.gen"))) == G0[k] + 1 for k in PEDS))
    chk("the Ember has its first property", "Свет" in rc.run("data get entity Cam Inventory"))
    chk("the west pass is open", score("#gate_west_pass", "le.gate") == 1)
    chk("the region faded (flag)", score("#fade_r1", "le.alt") == 1)
    time.sleep(3); chk("no second event", score("#chapters", "le.alt") == 1 and "done: 1b" in sto("altars a.weepers"))

def t_fade():
    print("[the fade of R1]")
    if score("#fade_r1", "le.alt") != 1: t_event()
    chk("bonfires 2,3,4,5,7,8,9 out (state 0, faded)", all("state: 0" in sto(f"bonfires by.b{n}") and "faded: 1b" in sto(f"bonfires by.b{n}") for n in FADED), {n: sto(f"bonfires by.b{n}")[-120:] for n in FADED})
    chk("bonfires 6 and 10 are not touched", all("faded: 1b" not in sto(f"bonfires by.b{n}") for n in KEPT))
    chk("the Refuge bonfire is not touched", "faded: 1b" not in sto("bonfires by.b1") and "state: 1" in sto("bonfires by.b1"))
    # the look of a faded bonfire when its chunk loads: bonfire 2 (cemetery)
    b2 = re.findall(r"r[xyz]: (-?\d+)", sto("bonfires by.b2")); print("     b2", sto("bonfires by.b2")[:200])
    rc.run("tp Cam2 118 200 448"); time.sleep(4)
    chk("bonfire 2: built unlit when its chunk loaded (lv 0b, campfire out)", wait(lambda: "lv: 0b" in sto("bonfires by.b2"), 8) and passed("execute if block 118 192 448 minecraft:campfire[lit=false]"), (sto("bonfires by.b2")[-160:], rc.run("execute if block 118 192 448 minecraft:campfire")))
    # biomes: tiles come when loaded; the counter
    chk("the biome tiles near Cam2 are faded", wait(lambda: passed("execute if biome 140 120 450 last_ember:barrows_faded"), 6), rc.run("execute if biome 140 120 450 last_ember:barrows"))
    # a player bound to a faded bonfire respawns there; cannot rest / bind
    # a player bound to a faded bonfire: the binding stays (respawn there), resting does not bind/heal
    rc.run("scoreboard players set Cam2 le.sb 2"); time.sleep(1.2)
    chk("the binding to a faded bonfire stays", score("Cam2", "le.sb") == 2)
    # the carrier relights bonfire 2
    rc.run("tp Cam 118 193 451"); time.sleep(3)
    tc.face("Cam", 118.5, 193, 451.5, 118.5, 193.3, 448.5); time.sleep(0.4); tc.act("Cam", "!use"); time.sleep(1.0)
    chk("the carrier relights a faded bonfire", lit(2), sto("bonfires by.b2")[-160:])
    # the elite chance of R1 x1.5 once the region is passed: one roll of a zombie at the cemetery, day, surface
    rc.run("time set day"); rc.run("scoreboard players set #elitechance le.el 100")
    def roll():
        rc.run("kill @e[type=zombie,tag=le.wtest]"); rc.run("summon zombie 130 200 460 {Tags:[\"le.wtest\"],NoAI:1b}")
        rc.run("execute as @e[type=zombie,tag=le.wtest,limit=1] at @s run function last_ember:elite/roll"); r = (score("#rg", "le.el"), score("#ch", "le.el"))
        rc.run("execute as @e[type=zombie,tag=le.wtest] run function last_ember:elite/unmake"); rc.run("kill @e[type=zombie,tag=le.wtest]"); return r
    after = roll(); rc.run("scoreboard players set #chapters le.alt 0"); before = roll(); rc.run("scoreboard players set #chapters le.alt 1")
    chk("the elite chance in R1: x1.5 after the chapter (region 1)", after[0] == 1 and after[1] == before[1] * 3 // 2, (before, after))

def t_reset():
    print("[altar/reset {chapter:1}]")
    rc.run(f"tp Cam {CX + 6}.5 {Y} {CZ + 12}.5"); rc.run(f"tp Cam2 {CX + 8}.5 {Y} {CZ + 12}.5"); time.sleep(3)
    rc.run("function last_ember:altar/reset {chapter:1}"); time.sleep(2.5)
    chk("chapters back to 0, altar not done", score("#chapters", "le.alt") == 0 and "done: 0b" in sto("altars a.weepers"), sto("altars a.weepers"))
    chk("the Weepers raise their hands again, the core is dark", not passed("execute if function last_ember:weepers/gen/probe_up") and score("#wpc", "le.alt") == 1)
    chk("the bonfires are lit again", all(lit(n) for n in FADED), {n: sto(f"bonfires by.b{n}")[-80:] for n in FADED})
    chk("the biomes come back", score("#fade_chapter1", "le.bio") == 0)
    chk("the region flag is cleared, the gate is closed", score("#fade_r1", "le.alt") == 0 and score("#gate_west_pass", "le.gate") == 0)
    chk("the pedestals are empty", filled() == 0)

def t_restart():
    print("[restart]")
    if "done: 1b" not in sto("altars a.weepers") or score("#fade_r1", "le.alt") != 1: t_event()
    subprocess.run([os.path.join(ROOT, "tools/server.sh"), "stop"], capture_output=True); time.sleep(8)
    subprocess.Popen(f"cd {ROOT} && tools/server.sh start > server/console.out 2>&1", shell=True)
    for _ in range(90):
        time.sleep(2)
        try:
            if "players online" in rc.run("list"): break
        except Exception: pass
    # the dev clients do not rejoin by themselves: start them again
    subprocess.run("pkill -f net.minecraft.client.main.Main", shell=True); time.sleep(3)
    subprocess.Popen(f"cd {ROOT} && python3 -I tools/client_launch.py > server/client.out 2>&1", shell=True)
    subprocess.Popen(f"cd {ROOT} && python3 -I tools/client_launch.py --name Cam2 --dir server/client2 --mem 1500M --size 640x360 > server/client2.out 2>&1", shell=True)
    for _ in range(90):
        time.sleep(2)
        try:
            l = rc.run("list")
            if "Cam2" in l and re.search(r"\bCam(?!2)\b", l): break
        except Exception: pass
    time.sleep(6); rc.run(f"tp Cam {CX + 6}.5 {Y} {CZ + 12}.5"); time.sleep(4)
    chk("after a restart: chapters 1, altar done, pose down, core burning", score("#chapters", "le.alt") == 1 and "done: 1b" in sto("altars a.weepers")
        and not passed("execute if function last_ember:weepers/gen/probe_down") and score("#wpc", "le.alt") == 2)
    chk("after a restart: the faded bonfires stay out", all("state: 0" in sto(f"bonfires by.b{n}") for n in FADED if n != 2))

def t_zones():
    print("[zones]")
    chk("weepers zone registered (indestructible)", "weepers" in "".join(open(os.path.join(ROOT, "zones/zones.txt")).read().split()))
    rc.run("time set night"); rc.run("difficulty hard"); time.sleep(1)
    rc.run(f"summon zombie {CX + 4} {Y} {CZ + 4}"); time.sleep(2.5)
    chk("no_spawn in the circle removes a monster", not passed(f"execute positioned {CX} {Y} {CZ} if entity @e[type=zombie,distance=..14]"))
    rc.run("tp Cam2 -425.5 111 -180.5 90 30"); rc.run("gamemode survival Cam2"); time.sleep(1.5)
    chk("Cam2 in the zone is in adventure mode", "adventure" in rc.run("data get entity Cam2 playerGameType") or "2" in rc.run("data get entity Cam2 playerGameType"), rc.run("data get entity Cam2 playerGameType"))
    rc.run("time set day"); rc.run("difficulty normal")

def mspt():
    m = re.search(r"([0-9.]+)\s*ms", rc.run("tick query")); return float(m.group(1)) if m else None
def t_perf():
    """both players stand still at the circle for the whole run (no chunks or animals loaded in between): Cam2 places the keys,
    the Ember is given to Cam (already within 10) last; peaceful (no natural mobs piling up during the run)"""
    print("[perf]"); stage(); rc.run("difficulty peaceful"); rc.run("time set day")
    for q in ("Cam", "Cam2"): rc.run(f"tag {q} remove le.carrier"); rc.run(f"clear {q} minecraft:trial_key")
    rc.run("data remove storage last_ember:ember carrier")
    rc.run(f"tp Cam {CX + 7}.5 {Y} {CZ + 3}.5 90 0")
    def ents(): rc.run("execute store result score #n le.e if entity @e"); return score("#n", "le.e")
    time.sleep(40); n0 = ents(); idle = [mspt() for _ in range(4) if not time.sleep(2)]
    for k in PEDS: hand_key("Cam2", k); time.sleep(0.2); click("Cam2", k)
    rc.run("execute as Cam run function last_ember:ember/give_to_me"); wait(lambda: "ev: -1" not in sto("altars a.weepers"), 3)
    ev = []
    while "done: 1b" not in sto("altars a.weepers") and len(ev) < 40: ev.append(mspt()); time.sleep(0.7)
    time.sleep(2); after = [mspt() for _ in range(3) if not time.sleep(1.5)]
    time.sleep(60); after60 = [mspt() for _ in range(4) if not time.sleep(2)]; n1 = ents(); rc.run("difficulty normal")
    print(f"     mspt (average of the last 100 ticks): before {idle}, during the event {ev}, just after {after}, 60 s after {after60}; entities {n0} -> {n1}")
    chk("tick stays under 25 ms during the event", max(x for x in ev if x is not None) < 25, ev)
    chk("60 s after the event the tick is back (within 1 ms of before)", max(after60) <= max(idle) + 1.0, (idle, after60))

T = {"peds": t_peds, "event": t_event, "fade": t_fade, "reset": t_reset, "restart": t_restart, "zones": t_zones, "perf": t_perf}
for n in (sys.argv[1:] or ["peds", "event", "fade", "reset", "zones"]): T[n]()
print(f"\n{ok} ok, {bad} failed")
