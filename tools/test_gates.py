#!/usr/bin/env python3
"""T-021 checks (server + dev clients Cam, Cam2): region borders, chapter gates, shortcuts.
Before (fresh world with the Refuge, see docs/reports/T-021-report.md):
  python3 tools/gen_gates.py gates/test_gates.txt && python3 tools/gen_zones.py
  python3 tools/gen_contracts.py contracts/test_contracts.txt contracts/test_gate_contracts.txt
  server STOPPED: tools/borders.sh apply t_axis t_joint (the test border over the vanilla terrain at x -280, z 440..660)
  tools/server.sh sync, RESTART the server (dialogs), clients Cam and Cam2.
Usage: python3 tools/test_gates.py [build border gate shortcut multi pets ember board perf shots]
Frames go to docs/reports/T-021/ (section shots)."""
import importlib.util, math, os, re, shutil, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
OUT = os.path.join(ROOT, "docs/reports/T-021")
ok = bad = 0
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n)
    else: bad += 1; print("  FAIL", n, e)
score = tc.score
def R(c): return rc.run(c)
def G(k): return score(k, "le.gate")
def pos(sel):
    v = re.findall(r"(-?\d+\.?\d*)d", R(f"data get entity {sel} Pos")); return [float(x) for x in v] if len(v) == 3 else None
def rot(sel):
    v = re.findall(r"(-?\d+\.?\d*)f", R(f"data get entity {sel} Rotation")); return [float(x) for x in v] if len(v) == 2 else None
def dist(a, b): return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5
def has(sel): return "passed" in R(f"execute if entity {sel}")
def count(sel): m = re.search(r"Count: (\d+)", R(f"execute if entity {sel}")); return int(m.group(1)) if m else 0
def block(x, y, z, b): return "passed" in R(f"execute if block {x} {y} {z} {b}")
def wait(cond, t=10.0, step=0.25):
    end = time.time() + t
    while time.time() < end:
        if cond(): return True
        time.sleep(step)
    return cond()
def safe(p, mode="survival"):
    R(f"gamemode {mode} {p}"); R(f"effect clear {p}")
    R(f"effect give {p} minecraft:resistance infinite 4 true"); R(f"effect give {p} minecraft:regeneration infinite 3 true"); R(f"effect give {p} minecraft:saturation infinite 0 true")
def shot(name, p="Cam"):
    tc.act(p, f"{name} 0")
    src = os.path.join(ROOT, tc.DIR[p], "screenshots", f"{name}.png")
    for _ in range(80):
        if os.path.exists(src): break
        time.sleep(0.1)
    if os.path.exists(src): os.makedirs(OUT, exist_ok=True); shutil.move(src, os.path.join(OUT, name + ".png"))
def walk(p, secs, jump=False):
    tc.act(p, "!fwd_on");
    if jump: tc.act(p, "!jump_on")
    time.sleep(secs); tc.act(p, "!fwd_off")
    if jump: tc.act(p, "!jump_off")

# ---- the test layout (gates/test_gates.txt)
AX = -280                                                   # the test border axis x = -280 (z 440..660), gap z 500..502
HUB_R1_EXIT = (26.5, 103, -25.5); HUB_R1_TRIG = (28.8, 103, -27.8)          # T-008 gate of r1 (45 deg): exit and the trigger centre
HUB_R2_EXIT = (-36.5, 103, 0.5); HUB_R2_TRIG = (-39.5, 103, 0.5)            # gate of r2 (270 deg)
DOOR1 = (1520, 201, 1540); DOOR1_EXIT = (1520.5, 201, 1537.5); DOOR1_TRIG = (1520.5, 201, 1533.5)   # faces south (yaw 0)
DOOR2 = (1600, 201, 1520); DOOR2_EXIT = (1597.5, 201, 1520.5); DOOR2_TRIG = (1593.5, 201, 1520.5)   # faces east (yaw 270)
TGATE = (1558, 201, 1600); TFAR = (2600, 201, 2600)
def ground(x, z):
    """y of the floor at x z (the column is loaded): the player is dropped there and its y read back"""
    R(f"tp Cam {x} 250 {z}"); time.sleep(0.3)
    for _ in range(40):
        p = pos("Cam")
        if p and "OnGround: 1b" in R("data get entity Cam OnGround"): return p[1]
        time.sleep(0.25)
    return pos("Cam")[1]

def t_build():
    print("[build: the test platform, closed gates and shortcuts]")
    R("gamerule send_command_feedback false"); R("gamerule advance_time false"); R("time set noon"); R("weather clear"); R("difficulty peaceful")
    R("forceload add 1490 1490 1630 1630"); wait(lambda: "passed" in R("execute if loaded 1630 200 1630"), 30, 0.5)
    for z in range(1490, 1631, 40):
        R(f"fill 1490 199 {z} 1630 200 {min(z + 39, 1630)} minecraft:stone"); R(f"fill 1490 201 {z} 1630 206 {min(z + 39, 1630)} minecraft:air")
    for g in ("t_gate", "t_far", "west_pass", "watch_gates"): R(f'function last_ember:gate/close {{id:"{g}"}}')
    R("scoreboard players set #gatev_t_gate le.gate -1"); R("scoreboard players set #gatev_t_far le.gate -1")
    for r in ("r1", "r2"): R(f'function last_ember:gate/sc_close {{r:"{r}"}}'); R(f"scoreboard players set #scb_{r} le.gate 0")
    R("scoreboard players set #chapters le.alt 0"); R("kill @e[type=minecraft:wolf]"); R("kill @e[type=minecraft:horse]")
    for p in ("Cam", "Cam2"): safe(p); R(f"scoreboard players reset {p} le.sccd")
    R("tp Cam 1540.5 201 1580.5"); R("tp Cam2 1542.5 201 1580.5")
    time.sleep(3)
    chk("the region doors are placed from their templates (r1 facing south, r2 facing east), locked",
        block(*DOOR1, "minecraft:dark_oak_door[facing=south,half=lower,open=false]") and block(*DOOR2, "minecraft:dark_oak_door[facing=east,half=lower,open=false]") and G("#scb_r1") == 1)
    chk("the test gate shows its closed template", block(TGATE[0] + 2, TGATE[1] + 1, TGATE[2], "minecraft:iron_bars"))

def t_border():
    print("[border: the axis x -280 cannot be crossed except in its gap]")
    R("save-all flush"); time.sleep(2)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools/borders_check.py"), "holes", "t_axis", "t_joint"], capture_output=True, text=True)
    chk("borders_check: every column of both axes closed from -64 to 319 (outside the gap)", r.returncode == 0 and "passable" not in r.stdout, r.stdout)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools/borders_check.py"), "walk", "-330", "440", "-230", "660", "-260,550", "-300,445", "-300,550"], capture_output=True, text=True)
    chk("borders_check: the T-joint splits the area into three parts (gap walled up), the gap joins east and south-west", r.returncode == 0 and "from (-260, 550) reaches [(-300, 550)]" in r.stdout, r.stdout)
    safe("Cam"); R("gamemode spectator Cam2"); R("tp Cam2 -300 140 520")
    def cross(name, x, z, y=None, secs=3.5, jump=False, swim=False, west=True):
        gy = y if y is not None else ground(x, z)
        R(f"tp Cam {x} {gy} {z} -90 0"); time.sleep(0.6)
        walk("Cam", secs, jump)
        p = pos("Cam")
        if west: chk(f"{name}: Cam stays west of the axis (x {p[0]:.2f})", p[0] < AX, p)
        return p
    cross("on the ground, walking and jumping into it", -284.5, 520.5, jump=True)
    cross("on the ground at the T-joint", -283.5, 452.5, jump=True)
    cross("in the dug tunnel under the hill (y 92)", -286.5, 470.5, y=92)
    cross("swimming on the lake", -284.5, 620.5, y=62.2, secs=5)
    cross("under water on the lake floor", -284.5, 620.5, y=48, secs=4)
    p = cross("in the gap (z 500..502): passes", -284.5, 501.5, secs=4, jump=True, west=False)
    chk("in the gap Cam is east of the axis", p[0] > AX + 1, p)
    # the ender pearl: thrown at the wall, and thrown high over the end of the world
    gy = ground(-284.5, 520.5); R(f"tp Cam -284.5 {gy} 520.5 -90 -35"); R("clear Cam"); R("item replace entity Cam weapon.mainhand with minecraft:ender_pearl 4"); time.sleep(0.5)
    tc.act("Cam", "!use"); time.sleep(4); p = pos("Cam"); chk(f"an ender pearl thrown at the barrier: Cam lands on his side (x {p[0]:.2f})", p[0] < AX, p)
    R("setblock -284 317 520 minecraft:glass"); R("tp Cam -283.5 318 520.5 -90 -5"); time.sleep(0.8); tc.act("Cam", "!use"); time.sleep(3)
    p = pos("Cam"); chk(f"an ender pearl thrown over the axis at the top of the world (y 320): killed, Cam stays (x {p[0]:.2f})", p[0] < AX and count("@e[type=minecraft:ender_pearl]") == 0, p)
    R("setblock -284 317 520 minecraft:air")
    # flying over the end of the world (elytra): crossing above y 316 is undone
    R("tp Cam -283.5 330 530.5 -90 0"); time.sleep(0.6); R("tp Cam -276.5 330 530.5 -90 0"); time.sleep(0.8)
    p = pos("Cam"); chk(f"crossing the axis above the world (y 330, elytra): back on his side (x {p[0]:.2f})", p[0] < AX, p)
    R("tp Cam -283.5 330 501.5 -90 0"); time.sleep(0.6); R("tp Cam -276.5 330 501.5 -90 0"); time.sleep(0.8)
    p = pos("Cam"); chk(f"... but above the gap it is allowed (x {p[0]:.2f})", p[0] > AX, p)
    # the Staff of Blink (T-011): barrier counts as solid
    tc.setc(1, 3, 6, "Cam"); safe("Cam"); R('execute as Cam run function last_ember:seer/give {staff:"blink"}')
    R("scoreboard players set Cam le.cd1 0")
    gy = ground(-284.5, 540.5); R(f"tp Cam -284.5 {gy} 540.5 -90 0"); time.sleep(0.5)
    R("item replace entity Cam weapon.mainhand from entity Cam hotbar.0") if False else None
    slot = R("data get entity Cam SelectedItem.components.\"minecraft:custom_data\"")
    tc.act("Cam", "!use_on"); time.sleep(0.4); tc.act("Cam", "!use_off"); time.sleep(1.0)
    p = pos("Cam"); chk(f"the Staff of Blink aimed through the barrier: Cam stays on the near side (x {p[0]:.2f})", p[0] < AX, (p, slot))
    # the ash trail never lands inside the barrier
    R("clear Cam"); R("item replace entity Cam inventory.0 with minecraft:dirt 5"); R(f"tp Cam -280.65 {gy} 540.5"); time.sleep(0.4); R("scoreboard players set Cam le.ash 0"); R("effect clear Cam"); R("kill Cam")
    # (Cam respawns far away and the chunk with the trail unloads: read the trail from storage)
    def trail_x():
        m = re.search(r"le.ash\]: ([1-9]\d*)", R("scoreboard players list Cam")); n = m and m.group(1)
        v = n and re.search(r"(-?\d+)$", R(f"data get storage last_ember:ash t.t{n}.x").strip())
        return int(v.group(1)) if v else None
    wait(lambda: trail_x() is not None, 8, 0.5); ax = trail_x()
    chk(f"the ash trail of a death against the barrier is not inside it (block x {ax})", ax is not None and ax != AX, R("data get storage last_ember:ash")[:300])
    R(f"tp Cam -284.5 {gy} 540.5"); time.sleep(2); R("kill @e[tag=le.ashclick]"); R("kill @e[tag=le.ash_disp]"); R("scoreboard players set Cam le.ash 0")
    R("data remove storage last_ember:ash t")
    safe("Cam"); tc.setc(1, 1, 0, "Cam"); safe("Cam")
    R("tp Cam 1540.5 201 1580.5"); R("tp Cam2 1542.5 201 1580.5"); safe("Cam2")

def t_gate():
    print("[gate: the chapter hooks open the gates, set the path flags, place the templates (also in a chunk loaded later)]")
    for g in ("t_gate", "t_far", "west_pass", "watch_gates"): R(f'function last_ember:gate/close {{id:"{g}"}}')
    R("scoreboard players set #gatev_t_far le.gate -1"); time.sleep(1.5)
    chk("before: #open_r2 = 0, #open_r3 = 0, #open_r1 = 1", G("#open_r2") == 0 and G("#open_r3") == 0 and G("#open_r1") == 1)
    R("tp Cam 1558.5 201 1590.5 0 0"); time.sleep(1.5)
    chk("the test gate is closed (bars)", block(TGATE[0] + 2, TGATE[1] + 1, TGATE[2], "minecraft:iron_bars"))
    R("function last_ember:altar/set_chapters {n:1}"); R("function last_ember:altar/hook/chapter_1"); time.sleep(1.6)
    chk("chapter 1: the gates of chapter 1 open (west_pass, t_gate), #open_r2 = 1, storage", G("#gate_west_pass") == 1 and G("#gate_t_gate") == 1 and G("#open_r2") == 1
        and "open: 1b" in R("data get storage last_ember:gates g.t_gate"))
    chk("the open template is placed (the bars are gone)", block(TGATE[0] + 2, TGATE[1] + 1, TGATE[2], "minecraft:air") and G("#gatev_t_gate") == 1)
    chk("the gate of chapter 2 stays closed", G("#gate_watch_gates") == 0 and G("#gate_t_far") == 0 and G("#open_r3") == 0)
    R(f"setblock {TGATE[0] + 2} {TGATE[1] + 1} {TGATE[2]} minecraft:glass")
    R("function last_ember:altar/hook/chapter_1"); R('function last_ember:gate/open {id:"t_gate"}'); time.sleep(1.6)
    chk("a repeat of the hook changes nothing (the template is not placed again)", block(TGATE[0] + 2, TGATE[1] + 1, TGATE[2], "minecraft:glass") and G("#gate_t_gate") == 1)
    R(f"setblock {TGATE[0] + 2} {TGATE[1] + 1} {TGATE[2]} minecraft:air")
    # chapter 2 while the far gate's chunk is not loaded: the template comes when it loads
    chk("the far gate's chunk is not loaded", "passed" not in R(f"execute if loaded {TFAR[0]} {TFAR[1]} {TFAR[2]}"))
    R("function last_ember:altar/set_chapters {n:2}"); R("function last_ember:altar/hook/chapter_2"); time.sleep(1.5)
    chk("chapter 2: t_far and watch_gates open, #open_r3 = 1; the template is pending", G("#gate_t_far") == 1 and G("#open_r3") == 1 and G("#gatev_t_far") == -1)
    R("gamemode spectator Cam2"); R(f"tp Cam2 {TFAR[0] + 2} {TFAR[1] + 3} {TFAR[2] - 6}"); wait(lambda: G("#gatev_t_far") == 1, 15, 0.5)
    chk("a player comes near: the chunk loads, the open template is placed", G("#gatev_t_far") == 1 and block(TFAR[0], TFAR[1], TFAR[2], "minecraft:cobblestone")
        and block(TFAR[0] + 2, TFAR[1] + 1, TFAR[2], "minecraft:air"))
    R("tp Cam2 1542.5 201 1580.5"); safe("Cam2")
    R("function last_ember:altar/set_chapters {n:0}")

def hub_closed(r):
    h = {"r1": (22, 103, -22), "r2": (-31, 103, 0)}[r]
    return block(*h, "minecraft:iron_bars")
def t_shortcut():
    print("[shortcut: locked from the Refuge, opened from inside the region (near / click), the transfer both ways]")
    for r in ("r1", "r2"): R(f'function last_ember:gate/sc_close {{r:"{r}"}}')
    R("tp Cam 22.5 103 -10.5 135 0"); R("tp Cam2 -20.5 103 0.5 -90 0"); time.sleep(2)
    chk("from the Refuge: r1 and r2 locked (portcullis down, no banner, dark)", hub_closed("r1") and hub_closed("r2") and G("#sc_r1") == 0 and block(21, 112, -21, "minecraft:air"))
    R("tp Cam 18.5 103 -18.5 -135 0"); time.sleep(0.6); tc.act("Cam", "!use"); time.sleep(1)
    chk("a click on the locked portcullis does not open it (\"Заперто с той стороны\")", G("#sc_r1") == 0 and has("@e[type=minecraft:interaction,tag=le.schub,scores={le.scw=1}]"))
    R(f"tp Cam {HUB_R1_TRIG[0]} 103 {HUB_R1_TRIG[2]}") if False else None
    # r1 opens by approach (24): Cam2 walks up to the door
    R("tp Cam2 1520.5 201 1580.5 180 0"); time.sleep(1.5)
    chk("r1: 40 blocks from the door it stays locked", G("#sc_r1") == 0)
    R("tp Cam2 1520.5 201 1562.5 180 0"); wait(lambda: G("#sc_r1") == 1, 4)
    chk("r1: within 24 blocks of the door it opens", G("#sc_r1") == 1)
    time.sleep(1.6)
    chk("r1 region side: chains off, lanterns, the door open", block(*DOOR1, "minecraft:dark_oak_door[open=true]") and block(1520, 204, 1541, "minecraft:air")
        and block(1520, 205, 1538, "minecraft:lantern"))
    R("tp Cam 18.5 103 -18.5 -135 0"); time.sleep(1.6)
    chk("r1 Refuge side: portcullis up, doors open, 2 lanterns, the banner", block(22, 103, -22, "minecraft:air") and block(21, 112, -21, "#minecraft:banners")
        and count("@e[type=minecraft:interaction,tag=le.schub,scores={le.scw=1}]") == 0)
    # r2 opens by a click on the door (approach does nothing)
    R(f"tp Cam2 {DOOR2[0] + 3.5} 201 {DOOR2[2] + 0.5} 90 10"); time.sleep(1.6)
    chk("r2 (open=click): standing at the door does not open it", G("#sc_r2") == 0)
    tc.act("Cam2", "!use"); wait(lambda: G("#sc_r2") == 1, 3)
    chk("r2: a click on the door opens it", G("#sc_r2") == 1)
    time.sleep(1.6); chk("r2: the door is open", block(*DOOR2, "minecraft:dark_oak_door[open=true]"))
    # the transfer: Cam walks from the plaza into the r1 vestibule, through to the blank wall
    safe("Cam"); R("tp Cam 21.5 103 -21.5 -135 0"); time.sleep(0.5); R("scoreboard players reset Cam le.sccd")
    tc.act("Cam", "!fwd_on"); t0 = time.time()
    ok_dark = wait(lambda: has("@a[name=Cam,tag=le.sct]"), 6, 0.1); tc.act("Cam", "!fwd_off")
    eff = R("data get entity Cam active_effects")
    chk("walking into the vestibule: the transfer starts at the blank wall (darkness, blindness)", ok_dark and "darkness" in eff and "blindness" in eff, eff)
    arrived = wait(lambda: (pos("Cam") or [0])[0] > 1000, 4, 0.1); p = pos("Cam"); ro = rot("Cam")
    chk("Cam arrives at the r1 door: the middle of the vestibule, facing the door (south)", arrived and dist(p, DOOR1_EXIT) < 0.6 and abs(((ro[0] - 0) + 180) % 360 - 180) < 1, (p, ro))
    chk("the darkness falls off (blindness only, ~1 s)", "darkness" not in R("data get entity Cam active_effects"))
    # the cooldown: back into the trigger at once -> nothing for 3 s, then the transfer
    R(f"tp Cam {DOOR1_TRIG[0]} 201 {DOOR1_TRIG[2]}"); time.sleep(1.6)
    chk("cooldown: just arrived, stepping into the trigger again does nothing for a while", (pos("Cam") or [0])[0] > 1000)
    wait(lambda: (pos("Cam") or [9999])[0] < 1000, 6, 0.2); p = pos("Cam"); ro = rot("Cam")
    chk("after the cooldown: back in the Refuge, the middle of the vestibule, facing the plaza", dist(p, HUB_R1_EXIT) < 0.6 and abs(((ro[0] - 45) + 180) % 360 - 180) < 1, (p, ro))
    # cancelled: step into the trigger and out again before 1 s
    time.sleep(3.5); R(f"tp Cam {HUB_R1_TRIG[0]} 103 {HUB_R1_TRIG[2]}"); wait(lambda: has("@a[name=Cam,tag=le.sct]"), 2, 0.05); R(f"tp Cam {HUB_R1_EXIT[0]} 103 {HUB_R1_EXIT[2]}")
    time.sleep(2); p = pos("Cam")
    chk("left the trigger before 1 s: the transfer is cancelled, the darkness cleared", dist(p, HUB_R1_EXIT) < 0.6 and not has("@a[name=Cam,tag=le.sct]") and "darkness" not in R("data get entity Cam active_effects"), p)
    # r2 by the plaza gate of r2 (270 deg)
    R("scoreboard players reset Cam le.sccd"); R(f"tp Cam {HUB_R2_TRIG[0]} 103 {HUB_R2_TRIG[2]}"); wait(lambda: (pos("Cam") or [0])[0] > 1000, 4)
    p = pos("Cam"); ro = rot("Cam"); chk("r2: from the plaza to the r2 door (faces east)", dist(p, DOOR2_EXIT) < 0.6 and abs(((ro[0] - 270) + 180) % 360 - 180) < 1, (p, ro))
    # spectator and creative go too, without darkness
    R("gamemode creative Cam2"); R("scoreboard players reset Cam2 le.sccd"); R(f"tp Cam2 {HUB_R2_TRIG[0]} 103 {HUB_R2_TRIG[2]}")
    time.sleep(0.4); eff = R("data get entity Cam2 active_effects")
    wait(lambda: (pos("Cam2") or [0])[0] > 1000, 4); chk("creative: transferred, without darkness", (pos("Cam2") or [0])[0] > 1000 and "darkness" not in eff, eff)
    safe("Cam2"); R("tp Cam 1540.5 201 1580.5"); R("tp Cam2 1542.5 201 1580.5")

def t_multi():
    print("[multi: two players in one trigger in one tick; two players crossing in opposite directions at once]")
    for r in ("r1",): R(f'function last_ember:gate/sc_open {{r:"{r}"}}')
    for p in ("Cam", "Cam2"): safe(p); R(f"scoreboard players reset {p} le.sccd")
    R(f"execute as Cam run tp @s {HUB_R1_TRIG[0]} 103 {HUB_R1_TRIG[2]}"); R(f"tp Cam2 {HUB_R1_TRIG[0] + 0.6} 103 {HUB_R1_TRIG[2] + 0.4}")
    wait(lambda: (pos("Cam") or [0])[0] > 1000 and (pos("Cam2") or [0])[0] > 1000, 5, 0.1)
    a, b = pos("Cam"), pos("Cam2")
    chk("both entered the r1 trigger together: both arrive at the r1 door exit", dist(a, DOOR1_EXIT) < 0.8 and dist(b, DOOR1_EXIT) < 0.8, (a, b))
    chk("each one once (2 players online, none left in transfer)", count("@a") == 2 and count("@a[tag=le.sct]") == 0)
    time.sleep(3.6)
    R(f"tp Cam {HUB_R1_TRIG[0]} 103 {HUB_R1_TRIG[2]}"); R(f"tp Cam2 {DOOR1_TRIG[0]} 201 {DOOR1_TRIG[2]}")
    wait(lambda: (pos("Cam") or [0])[0] > 1000 and (pos("Cam2") or [9999])[0] < 1000, 5, 0.1)
    a, b = pos("Cam"), pos("Cam2")
    chk("Cam from the Refuge and Cam2 from the region at the same time: they swap", dist(a, DOOR1_EXIT) < 0.8 and dist(b, HUB_R1_EXIT) < 0.8, (a, b))
    time.sleep(3.6); R("tp Cam 1540.5 201 1580.5"); R("tp Cam2 1542.5 201 1580.5")

def uuid(p): return R(f"data get entity {p} UUID").split("has the following entity data: ")[1].strip()
def t_pets():
    print("[pets: a tame wolf that follows goes along, a sitting one stays, the horse stays]")
    R('function last_ember:gate/sc_open {r:"r1"}'); safe("Cam"); R("scoreboard players reset Cam le.sccd")
    R("kill @e[type=minecraft:wolf]"); R("kill @e[type=minecraft:horse]"); u = uuid("Cam"); R("gamemode spectator Cam2"); R("tp Cam2 10.5 110 -10.5")
    R(f"tp Cam {HUB_R1_EXIT[0]} 103 {HUB_R1_EXIT[2]} 225 0"); time.sleep(0.5)
    R(f"summon minecraft:wolf 25.5 103 -24.5 {{Owner:{u},Tags:[\"t_walk\"],PersistenceRequired:1b}}")
    R(f"summon minecraft:wolf 24.5 103 -23.5 {{Owner:{u},Sitting:1b,Tags:[\"t_sit\"],PersistenceRequired:1b}}")
    R("summon minecraft:horse 26.5 103 -25.5 {Tame:1b,Tags:[\"t_horse\"],PersistenceRequired:1b}")
    R("ride Cam mount @e[type=minecraft:horse,tag=t_horse,limit=1]"); time.sleep(0.5)
    chk("setup: Cam rides the horse, two tame wolves (one sitting)", "passed" in R("execute as @e[type=minecraft:horse,tag=t_horse] on passengers if entity @s[name=Cam]") and count("@e[type=minecraft:wolf]") == 2)
    R(f"execute as @e[type=minecraft:horse,tag=t_horse] run tp @s {HUB_R1_TRIG[0]} 103 {HUB_R1_TRIG[2]}"); R(f"tp @e[type=minecraft:wolf,tag=t_walk] {HUB_R1_TRIG[0] - 1} 103 {HUB_R1_TRIG[2] + 1}")
    wait(lambda: (pos("Cam") or [0])[0] > 1000, 5, 0.1); time.sleep(1.5)
    w = pos("@e[type=minecraft:wolf,tag=t_walk,limit=1]"); s = pos("@e[type=minecraft:wolf,tag=t_sit,limit=1]"); h = pos("@e[type=minecraft:horse,tag=t_horse,limit=1]"); c = pos("Cam")
    chk("Cam is transferred (dismounted first)", c and c[0] > 1000, c)
    chk("the following wolf came along (within 4 of Cam)", w is not None and dist(w, c) < 4, w)
    chk("the sitting wolf stays in the Refuge", s is not None and abs(s[0]) < 100, s)
    chk("the horse stays in the vestibule", h is not None and abs(h[0]) < 100, h)
    R("kill @e[type=minecraft:wolf]"); R("kill @e[type=minecraft:horse]"); R("tp Cam 1540.5 201 1580.5"); safe("Cam2"); R("tp Cam2 1542.5 201 1580.5")

def t_ember():
    print("[ember: the carrier is transferred like anybody; the light of the Ember goes with him]")
    R('function last_ember:gate/sc_open {r:"r1"}'); safe("Cam"); R("scoreboard players reset Cam le.sccd")
    R("function last_ember:altar/set_chapters {n:1}"); R(f"tp Cam {HUB_R1_EXIT[0]} 103 {HUB_R1_EXIT[2]} 225 0"); R("gamemode spectator Cam2"); R("tp Cam2 10.5 110 -10.5")
    R("clear Cam"); R("tag @a remove le.carrier"); R("data remove storage last_ember:ember carrier"); R("execute as Cam run function last_ember:ember/give_to_me"); time.sleep(1.5)
    chk("the carrier has the light at his head in the Refuge", has("@a[name=Cam,tag=le.carrier]") and has("@e[type=minecraft:marker,tag=le.emlight,x=0,y=103,z=0,distance=..60]"))
    R(f"tp Cam {HUB_R1_TRIG[0]} 103 {HUB_R1_TRIG[2]}"); wait(lambda: (pos("Cam") or [0])[0] > 1000, 5, 0.1); time.sleep(1.0)
    chk("after the transfer Cam is still the carrier", has("@a[name=Cam,tag=le.carrier]"))
    chk("the light is at his head on the other side", "passed" in R("execute at Cam if entity @e[type=minecraft:marker,tag=le.emlight,distance=..3]"))
    chk("no light is left behind in the Refuge", count("@e[type=minecraft:marker,tag=le.emlight,x=0,y=103,z=0,distance=..60]") == 0 and block(26, 104, -26, "minecraft:air"))
    safe("Cam2"); R("clear Cam minecraft:trial_key"); R("function last_ember:altar/set_chapters {n:0}"); R("tp Cam 1540.5 201 1580.5")

def t_board():
    print("[board: a contract of a closed region is not on the board; it appears when the gate opens]")
    for g in ("t_gate", "west_pass"): R(f'function last_ember:gate/close {{id:"{g}"}}')
    R('function last_ember:contract/reset {id:"t_r2"}'); time.sleep(2.2)
    chk("#open_r2 = 0: the r2 contract is not on the board (state 0)", G("#open_r2") == 0 and score("#t_r2_s", "le.ct") == 0)
    R('function last_ember:gate/open {id:"west_pass"}'); time.sleep(2.2)
    chk("the gate west_pass opens (#open_r2 = 1): the contract is on the board (state 1)", G("#open_r2") == 1 and score("#t_r2_s", "le.ct") == 1)
    chk("the r1 contracts are on the board from the start (#open_r1 = 1)", score("#t_leshy_s", "le.ct") >= 1)

def t_perf():
    print("[perf: the gate loop with two players, idle and in the vestibules]")
    pf = load("test_contracts").prof
    R('function last_ember:gate/sc_open {r:"r1"}')
    R("tp Cam 0.5 103 5.5"); R("tp Cam2 2.5 103 5.5"); time.sleep(2); p0 = pf(10)
    R(f"tp Cam {HUB_R1_EXIT[0]} 103 {HUB_R1_EXIT[2]}"); R(f"tp Cam2 {HUB_R2_EXIT[0]} 103 {HUB_R2_EXIT[2]}"); time.sleep(2); p1 = pf(10)
    R(f"tp Cam {HUB_R1_TRIG[0]} 103 {HUB_R1_TRIG[2]}"); R(f"tp Cam2 {DOOR1_TRIG[0]} 201 {DOOR1_TRIG[2]}"); p2 = pf(10)
    for tag, p in (("idle on the plaza", p0), ("both standing in vestibules", p1), ("both in triggers (transfers every ~4 s)", p2)):
        print(f"   {tag}: tick {p.get('tick', 0):.1f} ms, gate/loop {p.get('last_ember:gate/loop', 0):.4f} ms, keys_loop {p.get('last_ember:altar/keys_loop', 0):.4f} ms, char/loop {p.get('last_ember:char/loop', 0):.3f} ms")
    worst = max(p.get("last_ember:gate/loop", 0) for p in (p0, p1, p2))
    chk(f"the gate loop with two players: at most {worst:.3f} ms per tick (< 0.2)", worst < 0.2)
    R("tp Cam 1540.5 201 1580.5"); R("tp Cam2 1542.5 201 1580.5")

def t_shots():
    print("[shots: docs/reports/T-021/]")
    R("gamemode spectator Cam"); R("time set noon"); R("weather clear")
    R('function last_ember:gate/sc_close {r:"r1"}'); R("tp Cam 8.5 106 -8.5 -135 12"); time.sleep(3); shot("hub_r1_closed_day")
    R("time set 12800"); time.sleep(2); shot("hub_r1_closed_dusk")
    R('function last_ember:gate/sc_open {r:"r1"}'); time.sleep(2); R("time set noon"); time.sleep(2); shot("hub_r1_open_day")
    R("time set 12800"); time.sleep(2); shot("hub_r1_open_dusk")
    R("tp Cam 23.5 104.6 -23.5 -135 8"); R("time set noon"); time.sleep(2); shot("hub_r1_vestibule_open")
    R('function last_ember:gate/sc_close {r:"r2"}'); R(f"tp Cam {DOOR2[0] + 9.5} 203.5 {DOOR2[2] + 3.5} 110 12"); time.sleep(3); shot("door_r2_locked")
    R('function last_ember:gate/sc_open {r:"r2"}'); time.sleep(2.5); shot("door_r2_open")
    R(f"tp Cam {DOOR2[0] - 1.5} 202.6 {DOOR2[2] + 0.5} 90 10"); time.sleep(2); shot("door_r2_vestibule")
    R("tp Cam -283 125 470 180 20"); time.sleep(3); shot("barrier_along_axis")
    R("tp Cam -296 70 610 -60 5"); time.sleep(3); shot("barrier_lake")
    R("gamemode survival Cam"); safe("Cam"); R("tp Cam 1540.5 201 1580.5")
    for f in os.listdir(OUT):
        if f.endswith(".png"):
            src = os.path.join(OUT, f); subprocess.run(["convert", src, "-resize", "1280x", "-quality", "78", src[:-4] + ".jpg"], check=False); os.remove(src)

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")] or ["build", "border", "gate", "shortcut", "multi", "pets", "ember", "board", "perf"]
    try:
        for w in want: globals()["t_" + w]()
    finally: R("gamerule send_command_feedback true")
    print(f"\n{ok} ok, {bad} failed"); sys.exit(1 if bad else 0)
