#!/usr/bin/env python3
"""T-034: the frames of the report (docs/reports/T-034/*.jpg, 1280 wide) from the dev client Cam (the camera, spectator).
  python3 tools/build/treasury_shots.py [name ...]        (no names: all)
Frames: bones_trail (the first signs of the chain seen from the trail), oak (the old oak, the fallen trunk, the ravens), mouth (the mouth
under the trunk from 4 blocks) and mouth_far (from 12), den (the den, night vision), ogre (the Ogre with the club up), channel (the channel
with a boat at its start, the sign), roots (the low tunnel under the roots), grotto (the grotto and the big Jelly asleep, night vision),
split (the Jelly torn into three), ledges (the ledges from the barbican), window_night (the window of the tower at night from the
causeway), lady (the White Lady in the room, night vision)."""
import importlib.util, json, math, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def load(n, path):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, path)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon", "tools/rcon.py")
R = rc.run
OUT = os.path.join(ROOT, "docs/reports/T-034"); os.makedirs(OUT, exist_ok=True)
CL = os.path.join(ROOT, "server/client")
R1 = os.path.join(ROOT, "server/build/r1")
O = json.load(open(os.path.join(R1, "ogre.json"))); G = json.load(open(os.path.join(R1, "grotto.json"))); TW = json.load(open(os.path.join(R1, "tower.json")))
F = O["F"]; W = G["W"]
def yawpitch(f, t):
    dx, dy, dz = t[0] - f[0], t[1] - f[1], t[2] - f[2]
    return math.degrees(math.atan2(-dx, dz)), -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
def jpg(name):
    from PIL import Image
    src = os.path.join(CL, "screenshots", name + ".png")
    if os.path.exists(src): Image.open(src).convert("RGB").resize((1280, 720)).save(os.path.join(OUT, name + ".jpg"), quality=80); os.remove(src)
LAST = [0.0]
def snap(name):
    t = LAST[0] + 12.5 - time.time()
    if t > 0: time.sleep(t)
    d = os.path.join(CL, "shot-done.txt")
    if os.path.exists(d): os.remove(d)
    open(os.path.join(CL, "shot-request.txt"), "w").write(f"{name} 0 clean\n")
    for _ in range(120):
        if os.path.exists(d): break
        time.sleep(0.5)
    time.sleep(0.6); LAST[0] = time.time(); jpg(name); print("  shot", name, flush=True)
def place(f, t, nv=False):
    R("gamemode spectator Cam"); yw, pt = yawpitch((f[0], f[1] + 1.62, f[2]), t)
    R("effect give Cam minecraft:night_vision infinite 0 true" if nv else "effect clear Cam minecraft:night_vision")
    R(f"tp Cam {f[0]} {f[1]} {f[2]} {yw:.1f} {pt:.1f}")
def shot(name, f, t, settle=7, nv=False):
    place(f, t, nv); time.sleep(settle); snap(name)
def reset():
    for k, (x, y, z) in (("ogre", O["lock"]), ("grotto", G["lock"]), ("tower", TW["lock"])):
        R(f"forceload add {x} {z}"); time.sleep(0.3); R(f"function last_ember:treasury/gen/{k}/reset"); R(f"forceload remove {x} {z}")

ex = O["exit"]; mx, mz = (ex[0][0] + ex[1][0] + 1) / 2, ex[0][1] + 0.5
d = O["stair"][-1][4]
def back(n): return (mx + d[0] * n, mz + d[1] * n)
SHOTS = {}
s0 = O["signs"][0]; s1 = O["signs"][1]; ts = O["trail_start"]
SHOTS["bones_trail"] = lambda: shot("bones_trail", (ts[0] + 0.5, s0[1] + 1, ts[1] + 0.5), (s1[0] + 0.5, s1[1], s1[2] + 0.5))
oc = O["oak"]["cells"]; ox = sum(c[0] for c in oc) / 4 + 0.5; oz = sum(c[1] for c in oc) / 4 + 0.5
SHOTS["oak"] = lambda: shot("oak", (back(16)[0] - 6, O["top"] + 2, back(16)[1]), (ox, O["top"] + 6, oz))
SHOTS["mouth"] = lambda: shot("mouth", (back(4)[0], O["top"] + 0.5, back(4)[1]), (mx, O["top"] - 1, mz - d[1] * 1.5))
SHOTS["mouth_far"] = lambda: shot("mouth_far", (back(12)[0], O["top"] - 1, back(12)[1]), (mx, O["top"], mz))
x1, z1, x2, z2 = O["cave"]
SHOTS["den"] = lambda: shot("den", (x2 - 1.5, F + 4, z2 - 1.5), (x1 + 4, F + 1, z1 + 5), nv=True)
def ogre():
    place((x1 + 12.5, F + 2, z1 + 9.5), (x1 + 4, F + 3, z1 + 6), nv=True); time.sleep(5)
    R("execute as @e[type=minecraft:zombie,tag=le.tr_ogre,limit=1] run item replace entity @s weapon.mainhand with minecraft:stick[minecraft:item_model=\"last_ember:treasury/ogre_club_raised\"]")
    R("execute as @e[type=minecraft:zombie,tag=le.tr_ogre,limit=1] run ride @s dismount")
    R("execute as @e[type=minecraft:zombie,tag=le.tr_ogre,limit=1] run tp @s %s %d %s facing %s %d %s" % (x1 + 7.5, F + 1, z1 + 7.5, x1 + 12.5, F + 2, z1 + 9.5))
    R("data merge entity @e[type=minecraft:zombie,tag=le.tr_ogre,limit=1] {CustomNameVisible:1b}")
    time.sleep(3); snap("ogre"); reset()
SHOTS["ogre"] = ogre
ln = G["line"]; e = ln[-1]
SHOTS["channel"] = lambda: shot("channel", (e[0] + 0.5 + e[2] * 6, W + 3, e[1] + 0.5 + e[3] * 6), (ln[-12][0] + 0.5, W + 1, ln[-12][1] + 0.5))
k0 = next(k for k, l in enumerate(ln) if not l[4])
SHOTS["roots"] = lambda: shot("roots", (ln[k0 + 4][0] + 0.5, W + 1.2, ln[k0 + 4][1] + 0.5), (ln[k0 - 2][0] + 0.5, W + 1.5, ln[k0 - 2][1] + 0.5))
gx1, gz1, gx2, gz2 = G["rect"]
SHOTS["grotto"] = lambda: shot("grotto", (gx1 + 3.5, W + 6, gz2 - 2.5), (G["rest"][0], W + 1, G["rest"][2]), nv=True)
def split():
    place((gx1 + 3.5, W + 6, gz2 - 2.5), (G["rest"][0], W + 1, G["rest"][2]), nv=True); time.sleep(5)
    R("scoreboard players set #g.st le.tr 1"); R("schedule function last_ember:treasury/gen/grotto/tick 1t replace")
    R("execute as @e[type=minecraft:ghast,tag=le.tr_jelly] run damage @s 300 minecraft:generic"); time.sleep(1.4)
    snap("split"); reset()
SHOTS["split"] = split
st = TW["start"]
SHOTS["ledges"] = lambda: shot("ledges", (st[0] - 4, st[1] + 3, st[2] - 6), (480.5, 182, 30))
SHOTS["window_night"] = lambda: (R("time set 18000"), shot("window_night", (477.5, 140, -30.5), (477.5, 192, 32), settle=9), R("time set 6000"))
def lady():
    reset(); place((480.5, TW["floor"] + 2.5, 34.5), (477.5, TW["floor"] + 2, 40.5), nv=True); time.sleep(6)
    R("execute as @e[type=minecraft:vex,tag=le.tr_lady,limit=1] on passengers if entity @s[type=minecraft:text_display] run data merge entity @s {text:{\"text\":\"Белая Дама\",\"color\":\"white\"}}")
    time.sleep(2); snap("lady")
SHOTS["lady"] = lady

if __name__ == "__main__":
    names = sys.argv[1:] or list(SHOTS)
    open(os.path.join(CL, "shot-request.txt"), "w").write("!sneak_off\n"); time.sleep(2)
    for c in ("gamerule advance_time false", "gamerule locator_bar false", "weather clear", "difficulty easy", "gamemode spectator Cam2", "tp Cam2 458 167 29", "time set 6000"):
        R(c)
    reset()
    for n in names: SHOTS[n]()
    R("gamemode survival Cam"); R("effect clear Cam minecraft:night_vision")
