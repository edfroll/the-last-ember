#!/usr/bin/env python3
"""T-009 flow test with two real clients (Cam in server/client, Cam2 in server/client2) on a FRESH world (tools/build/rebuild.sh):
Cell -> Hall -> Font -> square for two players at the same moment, soft passages, doors, kits, grate fires, a late player.
Run: python3 tools/test_char_flow.py [part]   parts: 1 (flow) 2 (late player)"""
import importlib.util, os, re, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("rcon", os.path.join(ROOT, "tools/rcon.py")); rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
DIR = {"Cam": "server/client", "Cam2": "server/client2"}
ok = bad = 0
def check(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n)
    else: bad += 1; print("  FAIL", n, e)
def use(p):
    d = os.path.join(ROOT, DIR[p]); open(os.path.join(d, "shot-request.txt"), "w").write("!use\n")
def pos(p):
    m = re.findall(r"([-0-9.]+)d", rc.run(f"data get entity {p} Pos")); return [float(x) for x in m]
def score(p, o):
    m = re.search(r"has (-?\d+)", rc.run(f"scoreboard players get {p} {o}")); return int(m.group(1)) if m else None
def block_open(x, y, z): return "passed" in rc.run(f"execute if block {x} {y} {z} minecraft:dark_oak_door[open=true]")
def tp(p, x, y, z, yaw=0, pitch=0): rc.run(f"tp {p} {x} {y} {z} {yaw} {pitch}")
def both(f):
    f("Cam"); f("Cam2")
def part1():
    print("[flow]")
    rc.run("gamemode survival Cam"); rc.run("gamemode survival Cam2"); time.sleep(3.2)
    a, b = pos("Cam"), pos("Cam2")
    check("two newcomers on different beds of the Cell", abs(a[0] - b[0]) > 1.5 and a[2] < -7 and b[2] < -7 and 57 < a[1] < 60, (a, b))
    check("Cell door closed at the start", not block_open(0, 57, -1)); time.sleep(5)
    check("Cell door open after 5 s", block_open(0, 57, -1))
    # without a people there is no way to the Font (soft push back, no damage)
    tp("Cam", 0.5, 57, 47.5, 0, 0); time.sleep(1.6); p = pos("Cam"); check("no people: pushed back from the Font", p[2] < 44, p)
    check("no damage from the push", "20.0f" in rc.run("data get entity Cam Health"))
    check("Hall door still closed", not block_open(0, 57, 48))
    # both choose at the same moment: Cam human (pad 12.5,12.5), Cam2 elf (pad 16.5,24.5)
    tp("Cam", 12.5, 57, 12.5, -135, 5); tp("Cam2", 16.5, 57, 24.5, -90, 5); time.sleep(1.2)
    use("Cam"); use("Cam2"); time.sleep(1.5)
    check("first click only describes (no choice yet)", score("Cam", "le.race") == 0 and score("Cam2", "le.race") == 0)
    use("Cam"); use("Cam2"); time.sleep(1.8)
    check("Cam chose humans, Cam2 elves (same second)", score("Cam", "le.race") == 1 and score("Cam2", "le.race") == 2, (score("Cam", "le.race"), score("Cam2", "le.race")))
    check("Hall door opened", block_open(0, 57, 48))
    check("elf scale 1.1 / human 1.0", "1.1" in rc.run("attribute Cam2 minecraft:scale get") and "1.0" in rc.run("attribute Cam minecraft:scale get"))
    tp("Cam", 12.5, 57, 12.5, -135, 5); use("Cam"); time.sleep(1.5)
    check("chosen: a second click does not change the choice", score("Cam", "le.race") == 1)
    # no class -> no way to the stairs
    tp("Cam", 20.5, 55, 57.5, 90, 0); time.sleep(1.6); p = pos("Cam"); check("no class: pushed back from the stairs corridor", p[0] < 14, p)
    check("Font door still closed", not block_open(14, 55, 57))
    # classes: Cam ranger (altar 5,52 -> side path 7.5,52.5), Cam2 seer (altar -5,62 -> -6.5,62.5)
    tp("Cam", 7.5, 55, 52.5, -90, 5); tp("Cam2", -6.5, 55, 62.5, 90, 5); time.sleep(1.2)
    use("Cam"); use("Cam2"); time.sleep(1.5); check("class: first click only describes", score("Cam", "le.class") == 0 and score("Cam2", "le.class") == 0)
    use("Cam"); use("Cam2"); time.sleep(2.0)
    check("Cam ranger, Cam2 seer (same second)", score("Cam", "le.class") == 2 and score("Cam2", "le.class") == 3, (score("Cam", "le.class"), score("Cam2", "le.class")))
    check("Font door opened", block_open(14, 55, 57))
    inv = rc.run("data get entity Cam Inventory"); inv2 = rc.run("data get entity Cam2 Inventory")
    check("ranger kit: bow, arrows, horn, bread", all(k in inv for k in ("minecraft:bow", "minecraft:arrow", "minecraft:goat_horn", "minecraft:bread")))
    check("seer kit: staff, dagger, book", all(k in inv2 for k in ("minecraft:stick", "minecraft:stone_sword", "minecraft:written_book")))
    check("name stones lit (human, elf)", "passed" in rc.run("execute if block -3 52 54 minecraft:sea_lantern") and "passed" in rc.run("execute if block 3 52 54 minecraft:sea_lantern"))
    time.sleep(1.5)
    check("respawn point moved to the Main Bonfire", "105" in rc.run("data get entity Cam respawn") and "105" in rc.run("data get entity Cam2 respawn"))
    time.sleep(1.5)
    check("four fires at the grate lit (everyone has chosen)", all("passed" in rc.run(f"execute if block {x} 103 {z} minecraft:campfire[lit=true]") for x, z in ((-2, 22), (2, 22), (-2, 26), (2, 26))))
    # free passage back and forth
    tp("Cam", 20.5, 55, 57.5, 90, 0); time.sleep(1.6); p = pos("Cam"); check("with a class the corridor is free", p[0] > 14.5, p)
def part2():
    print("[late player]")
    rc.run("execute as Cam2 run function last_ember:char/reset"); time.sleep(3.0)
    p = pos("Cam2"); check("late player: back in the Cell", p[2] < -7, p)
    check("the fires stay lit and the doors stay open", block_open(0, 57, 48) and block_open(14, 55, 57))
    tp("Cam2", 12.5, 57, 36.5, -45, 5); time.sleep(1.2); use("Cam2"); time.sleep(1.5); use("Cam2"); time.sleep(1.8)
    check("late player chooses halflings (pad 12,36) while Cam is already on the square", score("Cam2", "le.race") == 4 and score("Cam", "le.class") == 2)
    tp("Cam2", -6.5, 55, 52.5, 90, 5); time.sleep(1.2); use("Cam2"); time.sleep(1.5); use("Cam2"); time.sleep(2.0)
    check("late player chooses a class (knight)", score("Cam2", "le.class") == 1)
    check("small body: scale 0.65", "0.65" in rc.run("attribute Cam2 minecraft:scale get"))
if __name__ == "__main__":
    for s in (sys.argv[1:] or ["1", "2"]): {"1": part1, "2": part2}[s]()
    print(f"\n{ok} ok, {bad} failed"); sys.exit(1 if bad else 0)
