#!/usr/bin/env python3
"""T-023 frames of the Circle of the Weepers (server + client Cam; Cam2 places the keys for the event frames) -> docs/reports/T-023/*.jpg
Usage: python3 tools/build/weepers_shots.py [before | tears | strike | after]   (default: all, in this order)
  before  the Circle before the event (altar/reset {chapter:1}): east trail day and night, the stair, a Weeper close
  tears   the Weepers weeping (an event, the frame at tick 150)
  strike  the moment of the strike (another event, the frame at tick 239: the client shows it a few ticks later)
  after   after the event: the pedestals with the keys, the Circle at night, a faded bonfire"""
import importlib.util, json, math, os, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
OUT = os.path.join(ROOT, "docs/reports/T-023"); TMP = os.path.join(ROOT, "server/build/r1/shots_w"); os.makedirs(TMP, exist_ok=True)
CX, Y, CZ = -420, 111, -180
def look(c, t):
    dx, dy, dz = t[0] - c[0], t[1] - c[1], t[2] - c[2]
    return round(math.degrees(math.atan2(-dx, dz)), 1), round(-math.degrees(math.atan2(dy, math.hypot(dx, dz))), 1)
def shot(name, c, t, settle=20): yaw, pitch = look(c, t); return dict(name=name, x=c[0], y=c[1], z=c[2], yaw=yaw, pitch=pitch, settle=settle)
def run(shots, time_="noon", tag=""):
    spec = os.path.join(TMP, f"shots{tag}.json"); json.dump({"time": time_, "weather": "clear", "shots": shots}, open(spec, "w"))
    subprocess.run([sys.executable, os.path.join(ROOT, "tools/screenshot.py"), spec, "--out", TMP, "--double"], check=True)
    for s in shots: jpg(s["name"])
def jpg(name):
    subprocess.run(["convert", os.path.join(TMP, name + ".png"), "-resize", "1600x", "-quality", "82", os.path.join(OUT, name + ".jpg")], check=True)
def prep():
    rc.run("gamerule advance_time false"); rc.run("gamerule locator_bar false"); rc.run("difficulty peaceful")
EAST = shot("w_east_trail", (-382.5, 115.6, -177.5), (-420, 121, -180))
def before():
    prep(); rc.run("function last_ember:altar/reset {chapter:1}"); rc.run("function last_ember:altar/set_chapters {n:0}"); time.sleep(3)
    run([EAST, shot("w_stair_up", (-448.5, 91.7, -157.5), (-448, 109, -184)),
         shot("w_weeper_face", (-401.5, 120.6, -179.5), (-406, 119.5, -179.5)),              # the Weeper of the Garden (90 deg, faces east)
         shot("w_circle_from_west_arch", (-443.5, 114.5, -185.5), (-420, 113, -180))], "noon", "_day")
    e = dict(EAST, name="w_east_trail_night"); run([e], "midnight", "_night")
def strike(): event("w_strike", 239, (-404.5, 127.5, -166.5), (-420, 138, -180))
def tears(): event("w_tears", 150, (-401.5, 121.6, -183.5), (-406, 120, -180))
def event(name, tick, c, t):
    """one event of the altar, one frame at the given tick (the client renders with a delay of some ticks)"""
    prep(); rc.run("time set 13800"); rc.run("function last_ember:altar/reset {chapter:1}"); rc.run("function last_ember:altar/set_chapters {n:0}"); time.sleep(3)
    rc.run("gamemode spectator Cam"); yaw, pitch = look(c, t); rc.run(f"tp Cam {c[0]} {c[1]} {c[2]} {yaw} {pitch}")
    # Cam2 is the carrier and places the four keys (real clicks, as in tools/test_weepers.py)
    rc.run("gamemode survival Cam2"); rc.run("tp Cam2 -414.5 111 -181.5")
    for q in ("Cam", "Cam2"): rc.run(f"tag {q} remove le.carrier"); rc.run(f"clear {q} minecraft:trial_key")
    time.sleep(25)                                          # the camera's chunks (the cloud client renders slowly)
    src = open(os.path.join(ROOT, "tools/test_weepers.py")).read(); src = src[:src.index("T = {")]
    g = {"__file__": os.path.join(ROOT, "tools/test_weepers.py"), "__name__": "tw"}; exec(src, g)
    for k in g["PEDS"]: g["hand_key"]("Cam2", k); time.sleep(0.2); g["click"]("Cam2", k)
    rc.run("data remove storage last_ember:ember carrier"); rc.run("execute as Cam2 run function last_ember:ember/give_to_me")   # the carrier comes last
    rc.run("tp Cam2 -414.5 111 -181.5 0 0")
    while (tc.score("#ev", "le.alt") or 0) < tick and "done: 1b" not in rc.run("data get storage last_ember:altars a.weepers"): time.sleep(0.02)
    tc.act("Cam", name + " 0"); time.sleep(1.5)
    src_png = os.path.join(ROOT, "server/client/screenshots", name + ".png")
    if os.path.exists(src_png): os.replace(src_png, os.path.join(TMP, name + ".png")); jpg(name)
    while "done: 1b" not in rc.run("data get storage last_ember:altars a.weepers"): time.sleep(0.5)
def after():
    prep()
    if "done: 1b" not in rc.run("data get storage last_ember:altars a.weepers"): strike()
    run([shot("w_pedestals_keys", (-413.5, 116.5, -193.5), (-414, 112, -180)),
         shot("w_after_night", (-388.5, 127.5, -160.5), (-420, 122, -180))], "midnight", "_after")
    run([shot("w_faded_bonfire", (-150.5, 114.6, -356.5), (-150, 112, -362))], "noon", "_faded")
for n in (sys.argv[1:] or ["before", "tears", "strike", "after"]): {"before": before, "tears": tears, "strike": strike, "after": after}[n]()
