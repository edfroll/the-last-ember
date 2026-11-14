#!/usr/bin/env python3
"""T-022: the nine bonfires of the Dol on the built world (server + client Cam): built by the datapack at first load (variant dol),
lit by the Ember carrier with a real right click on the hearth, the respawn point moves there (kill -> respawn at that bonfire).
Usage: python3 tools/build/r1_bonfires_test.py"""
import json, os, re, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools")); import rcon as rc
import importlib.util
sp = importlib.util.spec_from_file_location("tc", os.path.join(ROOT, "tools/test_class.py")); tc = importlib.util.module_from_spec(sp); sp.loader.exec_module(tc)
R = rc.run; ok = bad = 0
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n)
    else: bad += 1; print("  FAIL", n, e)
def pos():
    v = re.findall(r"(-?\d+\.?\d*)d", R("data get entity Cam Pos")); return [float(x) for x in v]
def st(n, k): m = re.search(r": (-?\d+)", R(f"data get storage last_ember:bonfires by.b{n}.{k}")); return int(m.group(1)) if m else None
m = json.load(open(os.path.join(ROOT, "server/build/r1/r1.json")))
R("gamerule send_command_feedback false"); R("difficulty peaceful"); R("time set noon")
R("gamemode survival Cam"); R("effect give Cam minecraft:resistance infinite 255 true"); R("clear Cam")
R("execute as Cam run function last_ember:ember/give_to_me"); time.sleep(0.5)
for n, bid, x, y, z in m["bonfires"]:
    R(f"tp Cam {x + 0.5} {y} {z - 2.5}"); 
    for _ in range(20):
        if st(n, "built") == 1: break
        time.sleep(0.5)
    time.sleep(1.0)
    R(f"tp Cam {x + 0.5} {y} {z - 1.5}"); R(f"execute as Cam at @s anchored eyes facing {x + 0.5} {y + 0.4} {z + 0.5} run tp @s ~ ~ ~ ~ ~"); time.sleep(0.5)
    tc.act("Cam", "!use"); time.sleep(1.0)
    lit = "passed" in R(f"execute if block {x} {y} {z} minecraft:campfire[lit=true]")
    R("effect clear Cam minecraft:resistance"); R("kill Cam"); time.sleep(3.5); p = pos(); R("effect give Cam minecraft:resistance infinite 255 true")
    near = abs(p[0] - (x + 0.5)) < 3 and abs(p[2] - (z + 0.5)) < 6
    chk(f"{n} {bid} ({x} {y} {z}): built {st(n, 'built')}, variant dol, lit by a click {lit} (state {st(n, 'state')}), respawn at it ({p[0]:.1f} {p[1]:.1f} {p[2]:.1f})",
        st(n, "built") == 1 and lit and st(n, "state") == 1 and near)
R("clear Cam"); print(f"\n{ok} ok, {bad} failed"); sys.exit(1 if bad else 0)
