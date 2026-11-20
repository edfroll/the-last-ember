#!/usr/bin/env python3
"""T-026: the frames of the report (docs/reports/T-026/*.jpg, 1280 wide) from the dev client Cam (the server and Cam running, Cam2 as well):
the climb from bonfire 5 and the view over the fens from the rim, the main channel with its lanterns by day and by night, the boardwalk
(a gap with its tussock, the dark gap), the ruins and the house of the ambush inside, the hut from its pier and from the water, the hall,
the three rooms, each witch close, a head in a pool (eyes open at night, closed), the Master of the Causeway, the trade window, the
window of a task, the line over the hotbar at the choice.
  python3 tools/build/fens_shots.py [name ...]"""
import importlib.util, json, math, os, re, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def load(n, path):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, path)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
tf = load("tf", "tools/test_fens.py"); tc = tf.tc; R = tf.R
M = tf.M; W = tf.W; FL = tf.FL; HUT = tf.HUT
OUT = os.path.join(ROOT, "docs/reports/T-026"); os.makedirs(OUT, exist_ok=True)
CL = os.path.join(ROOT, "server/client")
def yawpitch(f, t):
    dx, dy, dz = t[0] - f[0], t[1] - f[1], t[2] - f[2]
    return math.degrees(math.atan2(-dx, dz)), -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
def shot(name, f, t, hud=False, settle=6, keep=False, spectator=True):
    if spectator: R("gamemode spectator Cam")
    yw, pt = yawpitch(f, t)
    R(f"tp Cam {f[0]} {f[1]} {f[2]} {yw:.1f} {pt:.1f}"); time.sleep(settle)
    for nm in (name + "__pre", name):            # twice, the second kept (the software GL may hand back the previous frame)
        d = os.path.join(CL, "shot-done.txt")
        if os.path.exists(d): os.remove(d)
        open(os.path.join(CL, "shot-request.txt"), "w").write(f"{nm} {1 if hud else 0}{' keep' if keep else ''}\n")
        for _ in range(120):
            if os.path.exists(d): break
            time.sleep(0.5)
        time.sleep(1.0)
    src = os.path.join(CL, "screenshots", name + ".png")
    for _ in range(20):
        if os.path.exists(src): break
        time.sleep(0.5)
    subprocess.run(["convert", src, "-resize", "1280x", "-quality", "80", os.path.join(OUT, name + ".jpg")], check=False)
    for f_ in os.listdir(os.path.join(CL, "screenshots")):
        if f_.startswith(name): os.remove(os.path.join(CL, "screenshots", f_))
    print("shot", name, flush=True)
def at(p, dy=0.0): return (p[0] + 0.5, p[1] + dy, p[2] + 0.5)
def day(): R("time set noon"); R("weather clear 100000")
def night(): R("time set midnight"); R("weather clear 100000")
def stage():
    R("gamerule advance_time false"); R("difficulty easy"); R("forceload add -500 250 -300 420"); time.sleep(4)
    R("gamemode spectator Cam2"); R("tp Cam2 -390 200 330")

def s_climb():
    day(); cp = M["cpath"]; hx, hy, hz = M["hearth"]
    shot("climb_from_bonfire", (hx - 2.5, hy + 3.5, hz + 6.5), at((cp[len(cp) // 2][0], 0, cp[len(cp) // 2][1]), W - 15), settle=10)
    po = M["pier_out"]; shot("rim_view", (po[0] + 1.5, W + 7, po[2] + 0.5), (HUT["table"][0], W + 2, HUT["table"][2]), settle=12)
def s_channel():
    mn = M["main"]; a, b = mn[70], mn[90]
    day(); shot("channel_day", (a[0] + 0.5, W + 5, a[1] + 0.5), (b[0] + 0.5, W + 1, b[1] + 0.5), settle=10)
    night(); shot("channel_night", (a[0] + 0.5, W + 5, a[1] + 0.5), (b[0] + 0.5, W + 1, b[1] + 0.5), settle=10); day()
def s_board():
    day(); d = M["deck"]
    g = next(g for g in M["gaps"] if not g["dark"]); k = g["k"]; p = d[k - 6][0]; q = d[k][0]
    shot("boardwalk_gap", (p[0] + 0.5, W + 3.6, p[1] + 0.5), (q[0] + 0.5, W + 1, q[1] + 0.5), settle=10)
    g = M["dark"]; k = g["k"]; p = d[k - 6][0]; q = d[k][0]
    shot("boardwalk_dark_gap", (p[0] + 0.5, W + 3.6, p[1] + 0.5), (q[0] + 0.5, W, q[1] + 0.5), settle=8)
def s_ruins():
    day(); r = next(r_ for r_ in M["ruins"] if r_["role"] == "ambush"); c = r["chest"]
    shot("ruins_outside", (r["x"] + 12.5, W + 6, r["z"] + 9.5), (r["x"] + 0.5, W + 2, r["z"] + 0.5), settle=10)
    shot("ruin_ambush_inside", (c[0] + 0.5 - 1.0 * (1 if r["rot"] % 2 else 0), c[1] + 1.2, c[2] + 0.5 + 2.2), at(c, 0.3), settle=6)
def s_hut():
    day(); ph = HUT["pier_hut"]
    shot("hut_from_pier", (ph[0] - 4.5, W + 3, ph[2] + 0.5), (-390.5, W + 12, 340.5), settle=10)
    shot("hut_from_water", (-362.5, W + 2.5, 366.5), (-390.5, W + 14, 340.5), settle=10)
    shot("hall", (-385.5, FL + 2.6, 343.5), (-393, FL + 1, 338), settle=6)
    shot("room_mother", (-398.5, FL + 2.2, 339.5), (-403, FL + 1.5, 339.5), settle=5)
    shot("room_maiden", (-379.5, FL + 2.2, 333.8), (-380, FL + 2, 328.5), settle=5)
    shot("room_crone", (-379.5, FL + 2.2, 345.6), (-378, FL + 2.5, 350), settle=5)
def s_witches():
    day()
    for k, n in ((1, "mother"), (2, "maiden"), (3, "crone")):
        x, y, z, yaw = tf.WITCH[k]; r = math.radians(yaw); dx, dz = -math.sin(r), math.cos(r)
        shot("witch_" + n, (x + 0.5 + dx * 1.8, y + 1.7, z + 0.5 + dz * 1.8), (x + 0.5, y + 1.6, z + 0.5), settle=4)
def s_heads():
    night(); p = tf.pool(2); c = (p["x"] + 0.5, W + 1.2, p["z"] + 0.5)
    R("function last_ember:fens/gen/heads_kill"); R(f"forceload add {p['x'] - 8} {p['z'] - 8} {p['x'] + 8} {p['z'] + 8}"); time.sleep(1)
    R(f"function last_ember:fens/gen/rise_{p['id']}"); time.sleep(0.6); R(f"function last_ember:fens/gen/up_{p['id']}")
    R(f"scoreboard players set #p{p['id']} le.fn 3")                # held up for the frames (the loop leaves a closed pool alone)
    time.sleep(1); R(f"execute as @e[type=minecraft:item_display,tag=le.fh{p['id']}] at @s run tp @s ~ ~ ~ facing {p['x'] + 6.5} {W + 3} {p['z'] + 0.5}")
    shot("head_open_night", (p["x"] + 6.5, W + 3.2, p["z"] + 0.5), c, settle=6)
    R(f"execute as @e[type=minecraft:item_display,tag=le.fh{p['id']}] run data modify entity @s item.components.\"minecraft:item_model\" set value \"last_ember:fens/head_closed\"")
    day(); shot("head_closed", (p["x"] + 5.5, W + 3.0, p["z"] + 0.5), c, settle=5)
    R("function last_ember:fens/gen/heads_kill"); R(f"forceload remove {p['x'] - 8} {p['z'] - 8} {p['x'] + 8} {p['z'] + 8}")
def s_master():
    day(); g = M["dark"]; R("function last_ember:fens/gen/master_spawn"); time.sleep(1)
    R("execute as @e[type=minecraft:drowned,tag=le.fmaster] run data merge entity @s {NoAI:1b}")
    R(f"tp @e[type=minecraft:drowned,tag=le.fmaster] {g['x'] + 0.5} {W - 0.6} {g['z'] + 0.5}"); time.sleep(1)
    shot("master", (g["x"] + 3.5, W + 2.6, g["z"] + 2.5), (g["x"] + 0.5, W + 0.6, g["z"] + 0.5), settle=5)
    R("function last_ember:fens/master_gone")
def s_windows():
    """the trade window, the window of a task, the line over the hotbar at the choice: Cam in the game (survival), HUD on"""
    day(); R("function last_ember:fens/reset"); R("clear Cam"); R("gamemode survival Cam"); tf.trophy("Cam", 4); R("give Cam minecraft:spider_eye 8"); time.sleep(1)
    tf.face_witch("Cam", 1); time.sleep(0.6); tc.act("Cam", "!use"); time.sleep(1.5)
    shot("window_trade", tuple(tf.pos("Cam")), (HUT["mother"][0] + 0.5, FL + 1.6, HUT["mother"][2] + 0.5), hud=True, keep=True, settle=1, spectator=False)
    tc.act("Cam", "!sneak_off"); time.sleep(1)
    (sx, sz), (tx_, ty_, tz_) = tf.TALK(3); R(f"tp Cam {sx} {FL + 1} {sz}"); tf.look_at("Cam", tx_, ty_, tz_); time.sleep(0.5)
    R("advancement revoke Cam only last_ember:fens/talk"); tc.act("Cam", "!use"); time.sleep(1.5)
    shot("window_task", tuple(tf.pos("Cam")), (tx_, ty_, tz_), hud=True, keep=True, settle=1, spectator=False)
    tc.act("Cam", "!sneak_off"); time.sleep(1)
    tf.vial("Cam"); R("scoreboard players set #vs le.fn 2"); tf.talk("Cam", 1); tc.act("Cam", "!sneak_off"); time.sleep(0.5)
    (sx, sz), (tx_, ty_, tz_) = tf.TALK(1); R(f"tp Cam {sx} {FL + 1} {sz}"); tf.look_at("Cam", -395, FL + 2, 339.5); time.sleep(0.6)
    R("execute as Cam run trigger le.fgive set 1"); time.sleep(0.4); tc.act("Cam", "!sneak_off"); time.sleep(0.3)
    shot("choice_actionbar", tuple(tf.pos("Cam")), (-395, FL + 2, 339.5), hud=True, settle=0.3, spectator=False)
    R("clear Cam"); R("function last_ember:fens/reset")
    for k in (1, 2, 3): R("function last_ember:trader/gen/reset_witch_%s" % tf.KEY[k])
def s_enchant():
    """the enchanting table with its 7 shelves: a sword and lapis put in (shift-clicks of the open window), the three offers"""
    day(); ex, ey, ez = HUT["enchant"]
    R("clear Cam"); R("gamemode survival Cam"); R("item replace entity Cam hotbar.0 with minecraft:iron_sword"); R("item replace entity Cam hotbar.1 with minecraft:lapis_lazuli 64")
    R("experience add Cam 50 levels"); R(f"tp Cam {ex + 0.5} {ey} {ez - 1.5}"); tf.look_at("Cam", ex + 0.5, ey + 0.7, ez + 0.5); time.sleep(0.6)
    tc.act("Cam", "!use"); time.sleep(1.5); tc.act("Cam", "!menu_qmove 29"); time.sleep(0.6); tc.act("Cam", "!menu_qmove 30"); time.sleep(1.2)
    shot("enchant_table", tuple(tf.pos("Cam")), (ex + 0.5, ey + 0.7, ez + 0.5), hud=True, keep=True, settle=1, spectator=False)
    tc.act("Cam", "!sneak_off"); time.sleep(0.6); R("clear Cam"); R("experience set Cam 0 levels")
ALL = dict(enchant=s_enchant, climb=s_climb, channel=s_channel, board=s_board, ruins=s_ruins, hut=s_hut, witches=s_witches, heads=s_heads, master=s_master, windows=s_windows)
if __name__ == "__main__":
    stage()
    for n in (sys.argv[1:] or list(ALL)): ALL[n]()
    R("gamemode survival Cam"); R("forceload remove -500 250 -300 420")
