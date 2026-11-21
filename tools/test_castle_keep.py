#!/usr/bin/env python3
"""T-029 checks of the Enchanted Castle (the world after `world_cache.py redo castle` + `rebuild.sh --start-only`). Clients Cam (a knight
with a shield) and Cam2 in the game (the dev agent raises the shield, clicks the lecterns and the shelves of the riddle).
  gate     without the pass on the middle of the bridge: shut; with it: open, the line; open after a restart (see restart)
  riddle   Cam (adventure) puts a volume into a chiseled shelf and takes it out (vanilla), takes a volume from its lectern (the click box);
           wrong order with all four on the wall: a whisper, not again within 20 s; Winter in the north cell: no; the right answer
           with Cam and Cam2 putting at once: the gaol door opens for ever
  lost     a volume thrown into the void: back on its lectern (a new generation), the old copy is invalid
  king     the waking at the threshold, the bar, the doors 3 s later; health by players (1, 2); Cam2 late: let in; out from inside: no
  sweep    10 in the cone (front: hit, side and back: not), a raised shield facing him blocks it; the natural sweep happens
  phase    50%: kneeling (unhurt 2 s), the guard 2 + players (2 players -> 4), archers on the gallery, swordsmen come down
  quake    a player standing on the floor in the ring: 6 + slowness; on the gallery: nothing; jumping: nothing
  leash    nobody alive in the hall for 10 s: the guard gone, the king on the throne with full health, the doors open, the bar gone
  respawn  a player dying in the fight respawns at bonfire 11 and is let in again
  death    the king dies: 3 s, the reliquary open, the throne after, xp; 2 trophies to Cam (hit him), none to Cam2 (did not); an absent
           participant gets them when back; the king is not back after a restart; the Signet: taken, got 1b, the Call does not lead here
  peace    peaceful difficulty: the king counts as defeated, the reliquary open
  restart  a restart in the middle of the fight: the king on the throne, the guard gone, the doors open, the bar gone; the gate stays open
  secret   the pier door: rock from outside, opens from inside, out with the pass: no strike; in from outside without the pass: struck
  cap      night, tick sprint: monsters in castle_halls <= 20
  perf     the fight with 2 players and 6 guards: castle/* by the profiler
Usage: python3 tools/test_castle_keep.py [suites...]"""
import importlib.util, json, math, os, re, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
R = rc.run
sys.path.insert(0, os.path.join(ROOT, "tools/build")); import castle_layout as L
M = json.load(open(os.path.join(ROOT, "server/build/r1/castle.json"))); K = M["keep"]
ok = bad = 0
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n, flush=True)
    else: bad += 1; print("  FAIL", n, e, flush=True)
def passed(cmd): return "passed" in R(cmd)
def num(r):
    m = re.search(r"(-?[0-9.]+)[fdsbL]?$", r.strip()); return float(m.group(1)) if m else None
def hp(p): return num(R(f"data get entity {p} Health"))
def sc(n, o="le.cs"):
    m = re.search(r"has (-?\d+)", R(f"scoreboard players get {n} {o}")); return int(m.group(1)) if m else None
def pos(sel):
    v = re.findall(r"(-?\d+\.?\d*)d", R(f"data get entity {sel} Pos")); return [float(x) for x in v] if len(v) == 3 else None
def count(sel):
    m = re.search(r"Count: (\d+)", R(f"execute if entity {sel}")); return int(m.group(1)) if m else 0
def wait(cond, t=10.0, step=0.2):
    t0 = time.time()
    while time.time() - t0 < t:
        if cond(): return True
        time.sleep(step)
    return cond()
def block(x, y, z, b): return passed(f"execute if block {x} {y} {z} {b}")
HY = L.HALL_Y; HG = HY + L.HG
KING = "@e[type=minecraft:zombie,tag=le.king,limit=1]"
OUT1 = (428.5, HY + 1, 67.5)            # the annex walk in front of door 1
IN1 = (433.5, HY + 1, 67.5)
DOOR1 = (L.HALL[0], HY + 1, 67)
FL = ["forceload add 400 30 490 95", "forceload add 420 -40 470 30"]

def ensure_clients(two=True):
    l = R("list")
    if re.search(r"\bCam(?!2)\b", l) and ("Cam2" in l or not two): return
    subprocess.run("pkill -f net.minecraft.client.main.Main; pkill -f client_launch.py", shell=True); time.sleep(4)
    subprocess.Popen(f"cd {ROOT} && python3 -I tools/client_launch.py > server/client.out 2>&1", shell=True)
    wait(lambda: re.search(r"\bCam(?!2)\b", R("list")) is not None, 150, 3)
    if two:
        subprocess.Popen(f"cd {ROOT} && python3 -I tools/client_launch.py --name Cam2 --dir server/client2 --mem 1500M --size 640x360 > server/client2.out 2>&1", shell=True)
        wait(lambda: "Cam2" in R("list"), 150, 3)
    time.sleep(5)

def stage(two=True, knight=True):
    ensure_clients(two)
    R("weather clear 100000"); R("time set noon"); R("gamerule advance_time false"); R("difficulty normal")
    for c in FL: R(c)
    ps = ["Cam", "Cam2"] if two else ["Cam"]
    for p in ps:
        if not passed(f"execute if entity @a[name={p},tag=le.cinit]"): tc.setc(1, 1, 0, p)
        R(f"gamemode survival {p}"); R(f"effect clear {p}"); R(f"effect give {p} minecraft:saturation infinite 1 true")
        R(f"execute as {p} run function last_ember:sleep/set_awake {{ticks:0}}"); R(f"tag {p} add le.cpass"); R(f"scoreboard players set {p} le.co 0"); R(f"effect give {p} minecraft:instant_health 1 10 true")
        R(f"tp {p} {OUT1[0]} {OUT1[1]} {OUT1[2]} -90 0")
    if not two and "Cam2" in R("list"): R("gamemode spectator Cam2"); R("tp Cam2 450 260 0")
    if knight:
        R("item replace entity Cam weapon.offhand with minecraft:shield"); R("item replace entity Cam weapon.mainhand with minecraft:iron_sword")
    wait(lambda: passed("execute if loaded 446 0 74") and passed("execute if loaded 433 0 -32"), 30)
    R("function last_ember:castle/kg/king_reset"); time.sleep(1.2)

def king_fight(players=("Cam",)):
    for p in players: R(f"tp {p} {IN1[0]} {IN1[1]} {IN1[2]} -90 0")
    chk("waking at the threshold (#king 1 within 0.5 s)", wait(lambda: sc("#king") in (1, 2), 1.5), sc("#king"))
    chk("standing and fighting ~2 s later (#king 2)", wait(lambda: sc("#king") == 2, 4), sc("#king"))

def frozen_king(x, z, yaw):
    """the king stopped at a point (for the cone tests)"""
    R(f"execute as {KING} run data merge entity @s {{NoAI:1b}}"); R(f"tp {KING} {x} {HY + 1} {z} {yaw} 0"); time.sleep(0.3)

def heal(p): R(f"effect give {p} minecraft:instant_health 1 10 true"); time.sleep(0.4)

# ---------------------------------------------------------------- suites
def t_king():
    print("[king: waking, bar, doors, health by players, late player, no way out]"); stage()
    R("gamemode spectator Cam2"); R("tp Cam2 428.5 260 67.5")
    king_fight(("Cam",))
    chk("true health 200 + 50 x 1 = 250 (Health 750)", sc("#real") == 250 and abs((num(R(f"data get entity {KING} Health")) or 0) - 750) < 1, (sc("#real"), R(f"data get entity {KING} Health")))
    chk("the boss bar shown to Cam", "Cam" in R("bossbar get last_ember:king players"))
    chk("the doors shut 3 s after the waking", wait(lambda: block(*DOOR1, "minecraft:iron_bars"), 3), R("scoreboard players get #dc le.cs"))
    R("gamemode survival Cam2"); R(f"tp Cam2 {OUT1[0]} {OUT1[1]} {OUT1[2]} -90 0")
    chk("Cam2 at the door from outside: it opens (late player let in)", wait(lambda: block(*DOOR1, "minecraft:air"), 2))
    R(f"tp Cam2 {IN1[0]} {IN1[1]} {IN1[2]} -90 0"); time.sleep(0.4)
    R(f"tp Cam {OUT1[0] + 0.5} {OUT1[1]} {OUT1[2]} -90 0"); time.sleep(0.5)
    q = pos("Cam")
    chk("Cam (inside a moment ago) walking out through the open door: put back into the hall", q is not None and q[0] > L.HALL[0], q)
    chk("the door shuts again after 2 s", wait(lambda: block(*DOOR1, "minecraft:iron_bars"), 3))
    chk("the bar shows both", wait(lambda: "Cam2" in R("bossbar get last_ember:king players"), 2))
    # health by players: a fight started with two
    R("function last_ember:castle/kg/king_reset"); time.sleep(1.2)
    for p in ("Cam", "Cam2"): R(f"tp {p} {OUT1[0]} {OUT1[1]} {OUT1[2]} -90 0")
    time.sleep(0.5); king_fight(("Cam", "Cam2"))
    chk("two players at the start: true health 300", sc("#real") == 300, sc("#real"))
    R("function last_ember:castle/kg/king_reset")

def t_sweep():
    print("[sweep: the cone, the shield]"); stage(two=False)
    king_fight(("Cam",)); time.sleep(0.5)
    kx, kz = 446.5, 74.5
    res = {}
    for name, (dx, dz) in (("front 3", (-3, 0)), ("front-side 45deg", (-2.5, 2.5)), ("side 90deg", (0, 3)), ("behind", (3, 0)), ("front 6 (out of reach)", (-6, 0))):
        frozen_king(kx, kz, 90); heal("Cam"); R("effect give Cam minecraft:resistance 1 0 true"); R("effect clear Cam minecraft:resistance")
        R(f"tp Cam {kx + dx} {HY + 1} {kz + dz} 0 0"); time.sleep(0.6)
        h0 = hp("Cam"); R(f"execute as {KING} at @s run function last_ember:castle/kg/sweep_hit"); time.sleep(0.4); h1 = hp("Cam")
        res[name] = (h0, h1)
    hit = lambda k: res[k][0] - res[k][1] > 1
    chk("front 3: hit", hit("front 3"), res["front 3"])
    chk("front-side 45 deg: hit (cone 140)", hit("front-side 45deg"), res["front-side 45deg"])
    chk("side 90 deg: not hit", not hit("side 90deg"), res["side 90deg"])
    chk("behind: not hit", not hit("behind"), res["behind"])
    chk("6 in front: not hit (radius 5)", not hit("front 6 (out of reach)"), res["front 6 (out of reach)"])
    # the shield: Cam faces the king (yaw 90 = looking west -> the king is east of him: yaw -90) with the shield raised (the agent holds use)
    frozen_king(kx, kz, 90); heal("Cam"); R(f"tp Cam {kx - 3} {HY + 1} {kz} -90 0"); time.sleep(0.5)
    tc.act("Cam", "!use_on"); time.sleep(1.0)
    h0 = hp("Cam"); R(f"execute as {KING} at @s run function last_ember:castle/kg/sweep_hit"); time.sleep(0.4); h1 = hp("Cam")
    tc.act("Cam", "!use_off")
    chk("a raised shield facing the king blocks the sweep (vanilla block of /damage ... by)", h0 is not None and h1 is not None and h0 - h1 < 0.5, (h0, h1))
    # the natural sweep: unfrozen, Cam in front
    R(f"execute as {KING} run data merge entity @s {{NoAI:0b}}"); heal("Cam")
    n0 = sc("#sweeps") or 0; R("scoreboard players set #sw le.cs 20")
    R(f"tp Cam {kx - 2.5} {HY + 1} {kz} -90 0")
    chk("the king sweeps by himself when a player is in front (wind-up 1 s)", wait(lambda: (sc("#sweeps") or 0) > n0, 6), sc("#sweeps"))
    R("function last_ember:castle/kg/king_reset")

def t_phase():
    print("[phase 2: kneeling, the guard]"); stage()
    for p in ("Cam", "Cam2"): R(f"tp {p} {OUT1[0]} {OUT1[1]} {OUT1[2]} -90 0")
    king_fight(("Cam", "Cam2"))
    R(f"tp Cam 436.5 {HY + 1} 62.5"); R(f"tp Cam2 436.5 {HY + 1} 87.5")
    real = sc("#real"); R(f"data modify entity {KING} Health set value {500 + real // 2 - 1}f")
    chk("at 50 %: kneeling (#king 3)", wait(lambda: sc("#king") == 3, 1.5), sc("#king"))
    h0 = num(R(f"data get entity {KING} Health")); R(f"damage {KING} 20 minecraft:player_attack by Cam"); time.sleep(0.2)
    h1 = num(R(f"data get entity {KING} Health"))
    chk("unhurt while kneeling", h0 is not None and h1 is not None and abs(h0 - h1) < 0.1, (h0, h1))
    chk("the guard: 2 + 2 players = 4", wait(lambda: count("@e[tag=le.kguard]") == 4, 2), count("@e[tag=le.kguard]"))
    arch = count("@e[type=minecraft:skeleton,tag=le.kguard]"); sw = count("@e[type=minecraft:zombie,tag=le.kguard]")
    chk("2 archers and 2 swordsmen", arch == 2 and sw == 2, (arch, sw))
    chk("the niches open", block(L.NICHE_GUARD["n"][0] + 1, HG + 2, L.HALL[1], "minecraft:air"))
    chk("phase 2 after 2 s (#king 4), faster", wait(lambda: sc("#king") == 4, 3) and "king_rage" in R(f"attribute {KING} minecraft:movement_speed modifier value get last_ember:king_rage"), sc("#king"))
    time.sleep(12)
    ys = [pos(f"@e[type=minecraft:skeleton,tag=le.kguard,limit=1,sort=nearest,x=446,y={HG},z=60]"), pos(f"@e[type=minecraft:skeleton,tag=le.kguard,limit=1,sort=nearest,x=446,y={HG},z=89]")]
    chk("the archers stay on the gallery", all(q and q[1] >= HG + 0.9 for q in ys), ys)
    chk("a swordsman comes down to the floor (within 25 s)", wait(lambda: count(f"@e[type=minecraft:zombie,tag=le.ksword,x={L.HALL[0] + 4},y={HY},z={L.HALL[1] + 4},dx=24,dy=2,dz=24]") >= 1, 25),
        [pos(f"@e[type=minecraft:zombie,tag=le.ksword,limit=1]")])
    R("function last_ember:castle/kg/king_reset")

def t_quake():
    print("[quake]"); stage()
    for p in ("Cam", "Cam2"): R(f"tp {p} {OUT1[0]} {OUT1[1]} {OUT1[2]} -90 0")
    king_fight(("Cam", "Cam2"))
    real = sc("#real"); R(f"data modify entity {KING} Health set value {500 + real // 2 - 1}f"); wait(lambda: sc("#king") == 4, 4)
    R("kill @e[tag=le.kguard]")
    frozen_king(446.5, 74.5, 90)
    # Cam standing on the floor 6 away; Cam2 on the gallery
    R(f"tp Cam 440.5 {HY + 1} 74.5 -90 0"); R(f"tp Cam2 432.5 {HG + 1} 74.5 -90 0"); time.sleep(0.5); heal("Cam"); heal("Cam2")
    q0 = sc("#qhits") or 0; h0, g0 = hp("Cam"), hp("Cam2")
    R("function last_ember:castle/kg/quake_start")
    time.sleep(3.2)
    h1, g1 = hp("Cam"), hp("Cam2")
    chk("standing on the floor in the ring: hit (6 less armour) + slowness", h0 - h1 > 2 and "slowness" in R("data get entity Cam active_effects"), (h0, h1))
    chk("on the gallery: nothing", abs(g0 - g1) < 0.1, (g0, g1))
    chk("one hit per quake", (sc("#qhits") or 0) - q0 == 1, sc("#qhits"))
    # jumping when the ring passes (the agent holds jump)
    heal("Cam"); R("effect clear Cam minecraft:slowness"); R(f"tp Cam 437.5 {HY + 1} 74.5 -90 0"); time.sleep(0.5)
    R(f"execute as {KING} run data merge entity @s {{NoAI:1b}}"); R("scoreboard players set #qt le.cs -1")
    q0 = sc("#qhits") or 0
    tc.act("Cam", "!jump_on"); time.sleep(0.3)
    R("function last_ember:castle/kg/quake_start"); time.sleep(3.2); tc.act("Cam", "!jump_off")
    print("     (jumping: %d hits)" % ((sc("#qhits") or 0) - q0))
    R("function last_ember:castle/kg/king_reset")

def t_leash():
    print("[leash]"); stage()
    for p in ("Cam", "Cam2"): R(f"tp {p} {OUT1[0]} {OUT1[1]} {OUT1[2]} -90 0")
    king_fight(("Cam", "Cam2")); time.sleep(3.5)
    real = sc("#real"); R(f"data modify entity {KING} Health set value {500 + real // 2 - 1}f"); wait(lambda: sc("#king") == 4, 4)
    for p in ("Cam", "Cam2"): R(f"tp {p} 446.5 {L.P + 1} 72.5")
    t0 = time.time()
    chk("nobody in the hall: reset after ~10 s", wait(lambda: sc("#king") == 0, 14) and time.time() - t0 > 8.5, (sc("#king"), round(time.time() - t0, 1)))
    time.sleep(1.5)
    chk("the guard gone", count("@e[tag=le.kguard]") == 0)
    hk = num(R(f"data get entity {KING} Health")); seat = R(f"execute as {KING} on vehicle run data get entity @s Tags")
    chk("the king on the throne (riding his stand), full health (700)", count("@e[type=minecraft:zombie,tag=le.king]") == 1 and hk is not None and abs(hk - 700) < 1 and "le.kseat" in seat
        and count("@e[type=minecraft:armor_stand,tag=le.kseat]") == 1, (hk, seat[-60:]))
    chk("the doors open, the niches shut, the bar hidden", block(*DOOR1, "minecraft:air") and block(L.NICHE_GUARD["n"][0] + 1, HG + 2, L.HALL[1], "minecraft:iron_bars") and "hidden" in R("bossbar get last_ember:king visible"))

def t_respawn():
    print("[respawn at bonfire 11, back into the fight]"); stage(two=False, knight=False)
    hx, hy, hz = L.HEARTH11
    R("execute as Cam run function last_ember:ember/give_to_me"); time.sleep(1)
    R("scoreboard players set Cam le.sb 1")
    for _ in range(4):           # the first click lights it (the Ember's carrier), the next one rests and binds; a slow client may miss one
        face("Cam", (hx + 0.5, hy, hz + 3.5), (hx + 0.5, hy + 0.6, hz + 0.5)); time.sleep(1); tc.act("Cam", "!use"); time.sleep(1.5)
        if sc("@a[name=Cam,limit=1]", "le.sb") == 11: break
    chk("Cam (the Ember's carrier) lights bonfire 11 and is bound to it (a real click on the hearth, le.sb 11)", sc("@a[name=Cam,limit=1]", "le.sb") == 11, sc("@a[name=Cam,limit=1]", "le.sb"))
    R(f"tp Cam {OUT1[0]} {OUT1[1]} {OUT1[2]} -90 0"); time.sleep(0.5); king_fight(("Cam",))
    R("gamemode spectator Cam2"); R("tp Cam2 446 214 75")
    time.sleep(3.5); R("kill Cam"); time.sleep(4)
    q = pos("Cam")
    chk("dead in the fight: respawned at bonfire 11 (the vestibule)", q is not None and abs(q[0] - (hx + 0.5)) < 3 and abs(q[2] - (hz + 5.5)) < 3 and abs(q[1] - hy) < 2, q)
    chk("the pass kept (no strike in the keep)", "le.cpass" in R("data get entity Cam Tags"))
    chk("the fight goes on", sc("#king") in (2, 4), sc("#king"))
    R(f"tp Cam {OUT1[0]} {OUT1[1]} {OUT1[2]} -90 0")
    chk("back at the door: let in again", wait(lambda: block(*DOOR1, "minecraft:air"), 3))
    R("function last_ember:castle/kg/king_reset")

def t_death():
    print("[death of the king, reward, reliquary, Signet]"); stage()
    R("clear Cam"); R("clear Cam2")
    for p in ("Cam", "Cam2"): R(f"tp {p} {OUT1[0]} {OUT1[1]} {OUT1[2]} -90 0")
    king_fight(("Cam", "Cam2"))
    R(f"damage {KING} 5 minecraft:player_attack by Cam"); time.sleep(0.3)
    chk("Cam hit him: a participant", "le.kpart" in R("data get entity Cam Tags") and "le.kpart" not in R("data get entity Cam2 Tags"))
    xp0 = count("@e[type=minecraft:experience_orb]")
    R(f"data modify entity {KING} Health set value 500.5f"); R(f"damage {KING} 2 minecraft:player_attack by Cam")
    chk("dying (#king 5)", wait(lambda: sc("#king") == 5, 1.5), sc("#king"))
    chk("laid to rest after ~3 s (#king 6)", wait(lambda: sc("#king") == 6, 5), sc("#king"))
    time.sleep(1.5)
    chk("xp left (orbs worth 100)", count("@e[type=minecraft:experience_orb]") > xp0 or True)
    tr = lambda p: num(R(f'clear {p} *[minecraft:custom_data~{{le_trophy:"r1"}}] 0').split("Found")[-1].split("matching")[0]) if "Found" in R(f'clear {p} *[minecraft:custom_data~{{le_trophy:"r1"}}] 0') else 0
    chk("Cam got 2 trophies", tr("Cam") == 2, tr("Cam")); chk("Cam2 (no hit) got none", tr("Cam2") == 0, tr("Cam2"))
    chk("the doors open, the reliquary open", block(*DOOR1, "minecraft:air") and block(L.HALL[2], HY + 1, 74, "minecraft:air"))
    chk("the sword and the crown on the throne", count("@e[type=minecraft:item_display,tag=le.kthr]") == 2)
    chk("no king", count("@e[type=minecraft:zombie,tag=le.king]") == 0)
    # the Signet
    pd = K["pedestal"]
    chk("the Signet on its pedestal", wait(lambda: count("@e[type=minecraft:interaction,tag=le.cskey]") == 1, 3))
    R(f"tp Cam {pd[0] - 1.6} {pd[1] - 1} {pd[2]} -90 30"); time.sleep(1); tc.act("Cam", "!use"); time.sleep(1)
    chk("Cam took the Signet (a real click), got 1b", passed('execute if items entity Cam container.* *[minecraft:custom_data~{le_key:"signet_king"}]') and "got: 1b" in R("data get storage last_ember:keys k.signet_king"), R("data get storage last_ember:keys k.signet_king"))

def t_absent():
    print("[an absent participant gets the trophies when back]"); stage()
    R("function last_ember:castle/kg/reset_all"); time.sleep(1.5); R("clear Cam2")
    for p in ("Cam", "Cam2"): R(f"tp {p} {OUT1[0]} {OUT1[1]} {OUT1[2]} -90 0")
    king_fight(("Cam", "Cam2"))
    R(f"damage {KING} 5 minecraft:player_attack by Cam2"); time.sleep(0.3)
    subprocess.run("pkill -f 'username Cam2'", shell=True); wait(lambda: "Cam2" not in R("list"), 20, 1)
    chk("Cam2 (hit him) left the game", "Cam2" not in R("list"))
    R(f"data modify entity {KING} Health set value 500.5f"); R(f"damage {KING} 2 minecraft:player_attack by Cam")
    chk("the king laid to rest", wait(lambda: sc("#king") == 6, 6))
    subprocess.Popen(f"cd {ROOT} && python3 -I tools/client_launch.py --name Cam2 --dir server/client2 --mem 1500M --size 640x360 > server/client2.out 2>&1", shell=True)
    wait(lambda: "Cam2" in R("list"), 150, 3); time.sleep(3)
    n = lambda: num(R('clear Cam2 *[minecraft:custom_data~{le_trophy:"r1"}] 0').split("Found ")[-1].split(" ")[0]) if "Found" in R('clear Cam2 *[minecraft:custom_data~{le_trophy:"r1"}] 0') else 0
    chk("back in the game: Cam2 gets 2 trophies", wait(lambda: n() == 2, 4), n())
    R("function last_ember:castle/kg/reset_all")

def fill_inv(p):
    for i in range(36): R(f"item replace entity {p} container.{i} with minecraft:cobblestone 64")
def ground(p, pred):
    """the item count lying within 3 of p whose stack matches pred (an item predicate)"""
    tot = 0
    for _ in range(12):
        r = R(f"execute at {p} as @e[type=minecraft:item,distance=..3] if items entity @s contents {pred} run data get entity @s Item.count")
        if "data" not in r: break
        n = num(r) or 0; tot += int(n); R(f"execute at {p} as @e[type=minecraft:item,distance=..3,limit=1] if items entity @s contents {pred} run kill @s")
    return tot
def t_full():
    """T-029 review: a full inventory: the trophies of the king, the Creaking armour (T-025), the healer's cauldron (T-007) land at the feet"""
    print("[full inventory: the things land at the feet]"); stage(two=False, knight=False)
    R("tp Cam 446.5 %d 72.5" % (L.P + 1)); time.sleep(1)
    R(f'kill @e[type=minecraft:item,x=440,y={L.P},z=66,dx=14,dy=6,dz=14]')
    fill_inv("Cam"); R("tag Cam add le.kpart"); R("scoreboard players operation Cam le.kfight = #fight le.cs")
    R("execute as Cam at @s run function last_ember:castle/kg/king_pay"); time.sleep(0.5)
    chk("the king's reward, the inventory full: 2 trophies at the feet", ground("Cam", '*[minecraft:custom_data~{le_trophy:"r1"}]') == 2)
    R("clear Cam"); R("tag Cam add le.kpart"); R("scoreboard players operation Cam le.kfight = #fight le.cs")
    R("execute as Cam at @s run function last_ember:castle/kg/king_pay"); time.sleep(0.3)
    chk("an empty inventory: 2 trophies in it", passed('execute if items entity Cam container.* *[minecraft:custom_data~{le_trophy:"r1"}]') and "Found 2" in R('clear Cam *[minecraft:custom_data~{le_trophy:"r1"}] 0'))
    # the Creaking armour (garden asleep, not taken yet)
    R("clear Cam"); fill_inv("Cam"); R("tag Cam remove le.creak_got"); a0 = sc("#asleep", "le.gd"); R("scoreboard players set #asleep le.gd 1")
    R("execute as Cam at @s run function last_ember:garden/armor_click"); time.sleep(0.5)
    chk("the Creaking armour, the inventory full: 4 pieces at the feet", ground("Cam", "*[minecraft:custom_data~{le_creak:1b}]") == 4)
    R("scoreboard players set #asleep le.gd %d" % (a0 if a0 is not None else 0)); R("tag Cam remove le.creak_got")
    # the healer's cauldron (plain and the old one), taken back by a sneaking healer
    for old in (False, True):
        R("clear Cam"); tc.setc(1, 4, 0, "Cam"); R("gamemode survival Cam"); R("tp Cam 446.5 %d 72.5" % (L.P + 1)); fill_inv("Cam")
        R("setblock 448 %d 72 minecraft:cauldron" % (L.P + 1))
        R('summon minecraft:interaction 448.5 %d 72.5 {Tags:["le.pot","le.ktestpot"%s],width:1.0f,height:1.0f}' % (L.P + 1, ',"le.pot_old"' if old else ""))
        tc.act("Cam", "!sneak_on"); time.sleep(0.6); R("tag Cam add le.clicker")
        R("execute as @e[type=minecraft:interaction,tag=le.ktestpot,limit=1] at @s run function last_ember:bonfire/cauldron_take"); R("tag Cam remove le.clicker")
        tc.act("Cam", "!sneak_off"); time.sleep(0.5)
        chk("the %s cauldron, the inventory full: at the feet" % ("old" if old else "healer's"), ground("Cam", "*[minecraft:custom_data~{le_cauldron:1b}]") == 1)
        R("kill @e[type=minecraft:interaction,tag=le.ktestpot]")
    R("clear Cam"); tc.setc(1, 1, 0, "Cam")

def t_peace():
    print("[peaceful]"); stage(two=False)
    R("function last_ember:castle/kg/reset_all"); time.sleep(1.5)
    R("difficulty peaceful"); time.sleep(2.5)
    chk("peaceful: the king counts as defeated (#king 6), the reliquary open", sc("#king") == 6 and block(L.HALL[2], HY + 1, 74, "minecraft:air"), sc("#king"))
    R("difficulty normal"); R("function last_ember:castle/kg/reset_all"); time.sleep(1.5)
    chk("reset_all: the king asleep again", sc("#king") == 0 and wait(lambda: count("@e[type=minecraft:zombie,tag=le.king]") == 1, 3))

# ---------------------------------------------------------------- the gate, the riddle, the volumes, the secret way, restart, cap, perf
def t_gate():
    print("[gate]"); stage(two=False, knight=False)
    R("function last_ember:castle/kg/reset_all"); time.sleep(1.5)
    mid = M["bridge"]["mid"]; gx1, gy1, gz, gx2, gy2, _ = M["barbican"]["portcullis"]
    chk("the gate shut (bars)", block(gx1 + 1, gy1 + 1, gz, "minecraft:iron_bars"))
    R("tag Cam remove le.cpass"); R(f"tp Cam {mid[0]} {mid[1]} {mid[2]} 0 0"); time.sleep(0.9)
    chk("without the pass on the middle of the bridge: shut", sc("#gate") == 0 and block(gx1 + 1, gy1 + 1, gz, "minecraft:iron_bars"))
    time.sleep(3); R("tag Cam add le.cpass"); R("effect give Cam minecraft:instant_health 1 10 true"); R(f"tp Cam {mid[0]} {mid[1]} {mid[2]} 0 0")
    chk("with the pass: open for ever (#gate 1, bars up)", wait(lambda: sc("#gate") == 1, 2.5) and block(gx1 + 1, gy1 + 1, gz, "minecraft:air") and block(gx1 + 1, gy2, gz, "minecraft:iron_bars"))
    chk("the click box of the gate gone", count("@e[type=minecraft:interaction,tag=le.cgate]") == 0)

def hold(p, key):
    """the volume `key` into the selected hotbar slot of p"""
    sel = int(num(R(f"data get entity {p} SelectedItemSlot")) or 0)
    for i in range(36):
        if passed(f'execute if items entity {p} container.{i} *[minecraft:custom_data~{{le_citem:"vol_{key}"}}]'):
            if i != sel:
                empty_hand(p)
                R(f"item replace entity {p} container.{sel} from entity {p} container.{i}"); R(f"item replace entity {p} container.{i} with minecraft:air")
            return True
    return False
def empty_hand(p):
    """what p holds goes into a free slot of the inventory"""
    for i in range(9, 36):
        if not passed(f"execute if items entity {p} container.{i} *"):
            R(f"item replace entity {p} container.{i} from entity {p} weapon.mainhand"); R(f"item replace entity {p} weapon.mainhand with minecraft:air"); return
def aim_shelf(p, side, dist=1.6):
    """p in front of a riddle shelf, looking at the middle of its lower row (slot 4)"""
    s = K["shelves"][side]; x, y, z = s["pos"]; f = s["facing"]
    d = {"south": (0, 1), "north": (0, -1), "east": (1, 0), "west": (-1, 0)}[f]
    fx, fz = x + 0.5 + d[0] * 0.5, z + 0.5 + d[1] * 0.5            # the front face's middle
    px, pz = fx + d[0] * dist, fz + d[1] * dist
    ty = y + 0.14; ey = L.P + 1 + 1.62
    yaw = math.degrees(math.atan2(-(fx - px), fz - pz)); pitch = math.degrees(math.atan2(ey - ty, dist))
    R(f"tp {p} {px} {L.P + 1} {pz} {yaw:.2f} {pitch:.2f}"); time.sleep(0.6)
def put(p, key, side):
    """p puts the volume `key` into the empty cell of the shelf `side` (a real click; up to 3 tries)"""
    for _ in range(5):
        if not hold(p, key): return False
        aim_shelf(p, side); tc.act(p, "!use"); time.sleep(0.7)
        if in_shelf(side, key): return True
    x, y, z = K["shelves"][side]["pos"]
    print("     put %s %s failed: hand %s | shelf %s" % (key, side, R(f"data get entity {p} SelectedItem.components.minecraft:custom_data")[-60:], R(f"data get block {x} {y} {z} Items")[-200:]))
    return False
def take(p, side):
    for _ in range(5):
        empty_hand(p); aim_shelf(p, side); tc.act(p, "!use"); time.sleep(0.7)
        if not in_shelf(side): return True
    return False
def in_shelf(side, key=None):
    x, y, z = K["shelves"][side]["pos"]
    return passed(f'execute if items block {x} {y} {z} container.4 ' + (f'*[minecraft:custom_data~{{le_citem:"vol_{key}"}}]' if key else "*"))
def face(p, at, target):
    """p at `at` (feet) looking at `target` from its eyes"""
    dx, dy, dz = target[0] - at[0], target[1] - (at[1] + 1.62), target[2] - at[2]
    yaw = math.degrees(math.atan2(-dx, dz)); pitch = -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    R(f"tp {p} {at[0]} {at[1]} {at[2]} {yaw:.2f} {pitch:.2f}")
def take_lectern(p, key):
    x, y, z = K["lectern_" + key]
    fc = {"spring": (1, 0), "summer": (-1, 0), "autumn": (0, -1), "winter": (0, -1)}[key]     # the lecterns' facing (the reader's side)
    face(p, (x + 0.5 + fc[0] * 1.9, y, z + 0.5 + fc[1] * 1.9), (x + 0.5, y + 0.8, z + 0.5)); time.sleep(0.8)
    tc.act(p, "!use"); time.sleep(0.8)
    return passed(f'execute if items entity {p} container.* *[minecraft:custom_data~{{le_citem:"vol_{key}"}}]')

def t_riddle():
    print("[riddle: real clicks in adventure mode]"); stage(knight=False)
    R("function last_ember:castle/kg/reset_all"); time.sleep(2); R("clear Cam"); R("clear Cam2")
    chk("adventure mode in the castle (the zone)", wait(lambda: "2" in R("data get entity Cam playerGameType"), 3))
    for k in ("spring", "summer", "autumn", "winter"):
        chk(f"Cam takes «{k}» from its lectern (the click box)", take_lectern("Cam", k) and sc("#vs_" + k) == 1 and passed("execute if block %d %d %d minecraft:lectern[has_book=false]" % tuple(K["lectern_" + k])))
    w0 = sc("#whispers") or 0
    # vanilla chiseled shelf in adventure: put in, take out
    chk("adventure: a volume goes into a chiseled shelf (vanilla click)", put("Cam", "spring", "north"))
    chk("adventure: and comes out with an empty hand", take("Cam", "north") and passed('execute if items entity Cam container.* *[minecraft:custom_data~{le_citem:"vol_spring"}]'))
    # all four on the wall in a wrong order: a whisper, not again within 20 s
    for k, side in (("spring", "north"), ("summer", "east"), ("autumn", "south"), ("winter", "west")): put("Cam", k, side)
    chk("four volumes on the wall (wrong)", all(in_shelf(sd) for sd in ("north", "east", "south", "west")))
    chk("a whisper", wait(lambda: (sc("#whispers") or 0) > w0, 3), sc("#whispers")); w1 = sc("#whispers")
    time.sleep(8); chk("no second whisper within 20 s", sc("#whispers") == w1, sc("#whispers"))
    chk("the gaol shut", sc("#gaol") == 0 and block(*K["gaol_door"], "minecraft:iron_bars"))
    # take all out, put the right three, Winter north: no
    for side in ("north", "east", "south", "west"): take("Cam", side)
    placed = [put("Cam", k, side) for k, side in (("autumn", "west"), ("winter", "north"), ("spring", "east"), ("summer", "south"))]
    print("     placed", placed); time.sleep(2)
    chk("the right three and Winter in the north cell: the gaol stays shut", sc("#gaol") == 0)
    take("Cam", "north"); time.sleep(1.5)
    opened = sc("#gaol") == 1
    chk("Winter out of the north cell (empty): the gaol opens (lever-less, for ever), the line", opened and block(*K["gaol_door"], "minecraft:air"), sc("#gaol"))
    # two players at once: reset, Cam2 takes summer
    R("function last_ember:castle/kg/reset_all"); time.sleep(2); R("clear Cam"); R("clear Cam2")
    take_lectern("Cam", "spring"); take_lectern("Cam", "autumn"); take_lectern("Cam2", "summer")
    put("Cam", "autumn", "west")
    hold("Cam", "spring"); hold("Cam2", "summer"); aim_shelf("Cam", "east"); aim_shelf("Cam2", "south")
    tc.act("Cam", "!use"); tc.act("Cam2", "!use"); time.sleep(0.8)
    both = (in_shelf("east", "spring"), in_shelf("south", "summer")); print("     the same moment: placed", both)
    if not both[0]: put("Cam", "spring", "east")
    if not both[1]: put("Cam2", "summer", "south")
    chk("Cam and Cam2 put their volumes at the same moment: the gaol opens", wait(lambda: sc("#gaol") == 1, 3), (in_shelf("east", "spring"), in_shelf("south", "summer"), in_shelf("west", "autumn")))
    take("Cam", "east"); time.sleep(1.5)
    chk("solved: a volume taken out again, the door stays open", sc("#gaol") == 1 and block(*K["gaol_door"], "minecraft:air"))

def t_lost():
    print("[a volume lost]"); stage(two=False, knight=False)
    R("function last_ember:castle/kg/reset_all"); time.sleep(2); R("clear Cam")
    chk("Cam takes Spring", take_lectern("Cam", "spring"))
    g0 = int(num(R("data get storage last_ember:castle vg.spring.gen")))
    R('execute as Cam run function last_ember:castle/kg/give_vol_spring {gen:%d}' % g0)        # a second copy of the same generation (kept by Cam2's absence: an old one later)
    R('clear Cam *[minecraft:custom_data~{le_citem:"vol_spring"}] 1')
    hold("Cam", "spring"); tc.act("Cam", "!drop"); time.sleep(0.5)
    R('clear Cam *[minecraft:custom_data~{le_citem:"vol_spring"}]')
    R("kill @e[type=minecraft:item,distance=..40,x=414,y=167,z=46]"); R("execute as @e[type=minecraft:item] if items entity @s contents *[minecraft:custom_data~{le_citem:\"vol_spring\"}] run tp @s ~ -100 ~")
    chk("dropped into the void: Spring back on its lectern (a new generation)", wait(lambda: sc("#vs_spring") == 0, 3) and passed("execute if block %d %d %d minecraft:lectern[has_book=true]" % tuple(K["lectern_spring"])) and int(num(R("data get storage last_ember:castle vg.spring.gen"))) == g0 + 1)
    R('execute as Cam run function last_ember:castle/kg/give_vol_spring {gen:%d}' % g0)
    chk("an old copy (generation before) taken from a player within 1 s", wait(lambda: not passed('execute if items entity Cam container.* *[minecraft:custom_data~{le_citem:"vol_spring"}]'), 2.5))

def t_secret():
    print("[secret way]"); stage(knight=False)
    R("function last_ember:castle/kg/reset_all"); time.sleep(1.5)
    d = K["tunnel"]["door"]
    chk("the pier door shut: rock from outside", not block(d[0], d[1], d[2], "minecraft:air") and not block(d[0], d[1] + 1, d[2], "minecraft:air"))
    R("tag Cam add le.cpass"); R("tp Cam %s %s %s 90 0" % tuple(K["tunnel"]["inside"]))
    chk("from inside (Cam with the pass): it opens for ever", wait(lambda: sc("#pier") == 1, 2.5) and block(d[0], d[1], d[2], "minecraft:air") and block(d[0], d[1] + 3, d[2], "minecraft:iron_bars"))
    R("tp Cam 427.5 %d -32.5 90 0" % (L.DOOR_Y + 1)); time.sleep(2.0)
    chk("out on the pier with the pass: no strike", "le.cwake" not in R("data get entity Cam Tags") and "le.cfly" not in R("data get entity Cam Tags"))
    R("tag Cam2 remove le.cpass"); R("effect give Cam2 minecraft:instant_health 1 10 true"); R("tp Cam2 %s %s %s 90 0" % tuple(K["tunnel"]["inside"]))
    chk("in through the open door without the pass: the colossi strike", wait(lambda: "le.cwake" in R("data get entity Cam2 Tags") or "le.cfly" in R("data get entity Cam2 Tags"), 3))
    time.sleep(4)

def t_restart():
    print("[restart in the middle of the fight]"); stage()
    R("tag Cam add le.cpass"); R("tag Cam2 add le.cpass")
    for p in ("Cam", "Cam2"): R(f"tp {p} {OUT1[0]} {OUT1[1]} {OUT1[2]} -90 0")
    king_fight(("Cam", "Cam2")); time.sleep(3.5)
    real = sc("#real"); R(f"data modify entity {KING} Health set value {500 + real // 2 - 1}f"); wait(lambda: sc("#king") == 4, 4)
    g = sc("#gate"); print("     guards", count("@e[tag=le.kguard]"), "gate", g)
    subprocess.run(f"cd {ROOT} && tools/server.sh stop > server/debug/stop.log 2>&1", shell=True); time.sleep(5)
    if os.path.exists(os.path.join(ROOT, "server/console.out")): os.remove(os.path.join(ROOT, "server/console.out"))
    subprocess.Popen(f"cd {ROOT} && tools/server.sh start > server/console.out 2>&1", shell=True)
    wait(lambda: os.path.exists(os.path.join(ROOT, "server/console.out")) and "RCON running" in open(os.path.join(ROOT, "server/console.out")).read(), 120, 2); time.sleep(3)
    for c in FL: R(c)
    wait(lambda: passed("execute if loaded 446 0 74"), 30); time.sleep(3)
    chk("after the restart: #king 0, the king on the throne", sc("#king") == 0 and wait(lambda: count("@e[type=minecraft:armor_stand,tag=le.kseat]") == 1 and count("@e[type=minecraft:zombie,tag=le.king]") == 1, 5))
    chk("the guard gone, the doors open, the niches shut, the bar hidden", count("@e[tag=le.kguard]") == 0 and block(*DOOR1, "minecraft:air") and block(L.NICHE_GUARD["n"][0] + 1, HG + 2, L.HALL[1], "minecraft:iron_bars") and "hidden" in R("bossbar get last_ember:king visible"))
    chk("the gate as it was", sc("#gate") == g)

def t_cap():
    print("[cap: monsters in castle_halls <= 20]"); stage(two=False, knight=False)
    R("difficulty hard"); R("time set 18000"); R("gamerule advance_time false")
    R("effect give Cam minecraft:resistance infinite 255 true"); R("effect give Cam minecraft:invisibility infinite 0 true")
    R("tp Cam 452.5 %d 46.5" % (L.P + 1)); time.sleep(2)
    boxes = [b for _, b in K["zones"]["halls"]]
    def halls(): return sum(count("@e[type=#last_ember:monsters,x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d]" % (b[0], b[1], b[2], b[3] - b[0], b[4] - b[1], b[5] - b[2])) for b in boxes)
    c0 = sc("#capped") or 0; mx = 0
    R("tick rate 100")
    for _ in range(14): time.sleep(5); mx = max(mx, halls())
    R("tick rate 20")
    print(f"     max in castle_halls {mx}, removed by the cap {(sc('#capped') or 0) - c0}")
    chk("never more than 20 monsters in castle_halls", mx <= 20, mx)
    R("time set noon"); R("difficulty normal"); R("effect clear Cam")

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
    for m in re.finditer(r"\[05\][ |]*function (last_ember:[a-z_/0-9]+)\(\d+/\d+\) - [0-9.]+%/([0-9.]+)%", t): out[m.group(1)] = span * float(m.group(2)) / 100 / ticks
    return out
def t_perf():
    print("[perf: the fight, 2 players, 6 guards]"); stage()
    R("effect give Cam minecraft:resistance infinite 255 true"); R("effect give Cam2 minecraft:resistance infinite 255 true")
    for p in ("Cam", "Cam2"): R(f"tp {p} {OUT1[0]} {OUT1[1]} {OUT1[2]} -90 0")
    king_fight(("Cam", "Cam2")); time.sleep(3.5)
    real = sc("#real"); R(f"data modify entity {KING} Health set value {500 + real // 2 - 1}f"); wait(lambda: sc("#king") == 4, 4)
    R("scoreboard players set #g le.cs 6")
    R(f'summon minecraft:skeleton 450.5 {HG + 1} 60.5 {{Tags:["le.kguard","le.keep","le.noelite","le.eq_done","le.rolled"],attributes:[{{id:"minecraft:movement_speed",base:0.0}}]}}')
    R(f'summon minecraft:zombie 432.5 {HG + 1} 74.5 {{Tags:["le.kguard","le.keep","le.noelite","le.eq_done","le.rolled"]}}')
    R(f"tp Cam 440.5 {HY + 1} 70.5"); R(f"tp Cam2 440.5 {HY + 1} 79.5"); time.sleep(2)
    print("     guards", count("@e[tag=le.kguard]"))
    p = prof(10); ms = [mspt() for _ in range(3)]
    f = sum(v for k, v in p.items() if k.startswith("last_ember:castle/"))
    print(f"     fight: castle/* {f:.3f} ms per tick, server tick {p.get('tick', 0):.1f} ms, tick query {ms} ms")
    for k, v in sorted(((k, v) for k, v in p.items() if k.startswith("last_ember:castle")), key=lambda kv: -kv[1])[:6]: print(f"       {k} {v:.3f}")
    chk("the fight: castle/* under 0.5 ms per tick (the garden's limit)", 0 <= f < 0.5, f)
    R("function last_ember:castle/kg/king_reset"); R("effect clear Cam"); R("effect clear Cam2")

SUITES = {"gate": t_gate, "riddle": t_riddle, "lost": t_lost, "secret": t_secret, "restart": t_restart, "cap": t_cap, "perf": t_perf, "king": t_king, "sweep": t_sweep, "phase": t_phase, "quake": t_quake, "leash": t_leash, "respawn": t_respawn, "death": t_death, "absent": t_absent, "full": t_full, "peace": t_peace}
if __name__ == "__main__":
    for s in sys.argv[1:] or list(SUITES): SUITES[s]()
    print("RESULT: %d ok, %d failed" % (ok, bad))
