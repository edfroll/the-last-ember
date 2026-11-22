#!/usr/bin/env python3
"""T-030: the frames of the report (docs/reports/T-030/*.jpg, 1280 wide) from the dev client Cam (the camera, spectator).
  python3 tools/build/grove_shots.py [name ...]        (no names: all)
Frames: grove_top, grove_path, grove_dusk, house, study, observatory, garden, face_closed, face_open, circle, intro (the window,
`keep`), faded (the grove after the fading of chapter I by the darkened Vale)."""
import importlib.util, json, math, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def load(n, path):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, path)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon", "tools/rcon.py")
R = rc.run
OUT = os.path.join(ROOT, "docs/reports/T-030"); os.makedirs(OUT, exist_ok=True)
CL = os.path.join(ROOT, "server/client")
M = json.load(open(os.path.join(ROOT, "server/build/r1/grove.json")))
HX, HZ = M["house"]; L = M["L"]
def yawpitch(f, t):
    dx, dy, dz = t[0] - f[0], t[1] - f[1], t[2] - f[2]
    return math.degrees(math.atan2(-dx, dz)), -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
def jpg(name):
    from PIL import Image
    src = os.path.join(CL, "screenshots", name + ".png")
    if os.path.exists(src): Image.open(src).convert("RGB").resize((1280, 720)).save(os.path.join(OUT, name + ".jpg"), quality=80); os.remove(src)
LAST = [0.0]
def gap(sec=12.5):
    t = LAST[0] + sec - time.time()
    if t > 0: time.sleep(t)
def snap(name, hud=False, keep=False, pre=False):
    gap()
    d = os.path.join(CL, "shot-done.txt")
    for nm in ((name + "__pre",) if pre else ()) + (name,):
        if os.path.exists(d): os.remove(d)
        open(os.path.join(CL, "shot-request.txt"), "w").write(f"{nm} {1 if hud else 0} {'keep' if keep else 'clean'}\n")
        for _ in range(120):
            if os.path.exists(d): break
            time.sleep(0.5)
        time.sleep(0.6 if nm == name else 1.5)
        if nm != name:
            p = os.path.join(CL, "screenshots", nm + ".png")
            if os.path.exists(p): os.remove(p)
            LAST[0] = time.time(); gap()
    LAST[0] = time.time(); jpg(name); print("  shot", name, flush=True)
def place(f, t, nv=False):
    R("gamemode spectator Cam"); yw, pt = yawpitch((f[0], f[1] + 1.62, f[2]), t)
    if nv: R("effect give Cam minecraft:night_vision infinite 0 true")
    else: R("effect clear Cam minecraft:night_vision")
    R(f"tp Cam {f[0]} {f[1]} {f[2]} {yw:.1f} {pt:.1f}")
def shot(name, f, t, settle=7, nv=False, hud=False):
    place(f, t, nv); time.sleep(settle); snap(name, hud)

def setup():
    for c in ("gamerule advance_time false", "gamerule locator_bar false", "weather clear", "function last_ember:grove/advisor_free"):
        R(c)

def main(names):
    setup()
    ch = M["chair"]; ng = M["night"]; d = M["door"]
    cx, cz = HX, HZ
    S = {
        "grove_top": lambda: (R("time set 6000"), shot("grove_top", (-372, 196, 12), (-424, 132, 66), settle=12)),
        "grove_path": lambda: (R("time set 4000"), shot("grove_path", (-405.5, 137, 73.5), (cx + 4, L + 4, cz), settle=10)),
        "grove_dusk": lambda: (R("time set 12300"), shot("grove_dusk", (-398.5, 146, 70.5), (cx, L + 12, cz), settle=10)),
        "house": lambda: (R("time set 5000"), shot("house", (-403, 146, 60), (cx, L + 12, cz), settle=10)),
        "study": lambda: (R("time set 6000"), R("function last_ember:grove/advisor_free"), time.sleep(3), shot("study", (cx - 1.5, L + 0.9, cz - 2.3), (ch[0] + 0.5, ch[1] + 1.0, ch[2] + 0.5), settle=8)),
        "study_wide": lambda: (R("time set 6000"), shot("study_wide", (cx + 3.3, L + 2.2, cz + 2.4), (cx - 1, L + 1.6, cz - 2), settle=8)),
        "chimney": lambda: (R("time set 7000"), shot("chimney", (cx - 26, L + 30, cz + 14), (cx - 9, L + 27, cz + 3), settle=10)),
        "circle": lambda: circle(),
        "faded": lambda: faded(),
        "observatory": lambda: (R("time set 18000"), time.sleep(3), shot("observatory", (cx + 1.5, L + 10, cz + 4.5), (ng[0] + 1.5, ng[1] + 1.5, ng[2] + 0.5), settle=8)),
        "garden": lambda: (R("time set 7000"), shot("garden", (-397.5, 139.5, 79.5), (-405, 137, 62), settle=8)),
        "intro": lambda: intro(),
    }
    for f in M["faces"][:1]:
        dx, dz = {"north": (0, -1), "east": (1, 0), "south": (0, 1), "west": (-1, 0)}[f["side"]]
        pos = (f["x"] + dx * 5 + 0.5, f["y"] + 2, f["z"] + dz * 5 + 0.5); tgt = (f["x"] + dx + 0.5, f["y"] + 4.5, f["z"] + dz + 0.5)
        S["face_closed"] = lambda pos=pos, tgt=tgt: (R("time set 6000"), R("function last_ember:grove/faces_close"), shot("face_closed", pos, tgt, settle=6))
        S["face_open"] = lambda pos=pos, tgt=tgt: (R("time set 6000"), R("function last_ember:grove/faces_open"), shot("face_open", pos, tgt, settle=6), R("function last_ember:grove/faces_close"))
    order = [n for n in S if n != "intro"] + ["intro"]          # the window last (it stays open until an action closes it)
    for n in (names or order):
        if n in S: S[n]()
    R("gamerule advance_time true")

def circle():
    """the four keys of chapter I taken: the Advisor at the west arch of the Circle of the Weepers (the real rule, nobody near)"""
    c = M["advisor_points"]["circle"]
    R("forceload add -446 -189 -438 -181"); R("time set 6000"); R("tp Cam -404 160 72")
    for k in ("signet_king", "tear_creaker", "crown_witches", "thread_labyrinth"): R(f"execute as Cam run function last_ember:altar/give_key {{id:\"{k}\"}}")
    for _ in range(30):
        if "Советчик" in R("execute as @e[type=minecraft:mannequin,tag=le.advisor,x=%.1f,y=%.1f,z=%.1f,distance=..1.5] run data get entity @s CustomName" % tuple(c[:3])): break
        time.sleep(1)
    shot("circle", (c[0] + 5.5, c[1] + 1.2, c[2] + 2.5), (c[0], c[1] + 1.4, c[2]), settle=8)
    R("clear Cam minecraft:ominous_trial_key")
    for k in ("signet_king", "tear_creaker", "crown_witches", "thread_labyrinth"): R(f"data modify storage last_ember:keys k.{k}.got set value 0b")
    R("function last_ember:grove/reset"); R("forceload remove -446 -189 -438 -181")

def faded():
    """the grove after the fading of chapter I, by the darkened Vale"""
    R("time set 6000"); R("function last_ember:altar/set_chapters {n:1}"); R("function last_ember:region/gen/fade_r1")
    place((-352, 182, 30), (-420, 128, 66)); time.sleep(14)
    snap("faded")
    R("function last_ember:region/gen/unfade_r1"); R("function last_ember:altar/set_chapters {n:0}"); time.sleep(4)

def intro():
    """the window of the acquaintance (keep: the frame with the window open): Cam talks to the Advisor"""
    ch = M["chair"]
    R("time set 6000"); R("gamemode adventure Cam"); R("tag Cam remove le.amet")
    R(f"tp Cam {HX + 1.5} {L + 1} {HZ + 0.5} 150 10"); time.sleep(4)
    R("execute as Cam at @s run function last_ember:grove/meet"); time.sleep(3)
    snap("intro", hud=True, keep=True)
    open(os.path.join(CL, "shot-request.txt"), "w").write("!sneak_off\n"); time.sleep(2)      # any action of the agent closes the window
    R("gamemode spectator Cam")

if __name__ == "__main__":
    main(sys.argv[1:])
