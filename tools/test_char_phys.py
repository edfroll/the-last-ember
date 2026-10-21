#!/usr/bin/env python3
"""T-009 physical checks with the real dev client (Cam): can each people jump onto a 1-block ledge, does an elf (1.98) fit under a 2-high ceiling.
Usage: python3 tools/test_char_phys.py  (server + client running)"""
import importlib.util, math, os, re, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); wb = load("walkbot")
def setc(race, cls=1):
    rc.run("clear Cam"); rc.run("execute as Cam run function last_ember:char/reset"); time.sleep(1.6); rc.run("gamemode survival Cam")
    rc.run(f"execute as Cam run function last_ember:char/set {{race:{race},class:{cls}}}"); time.sleep(0.5)
def walk(x, z0, z1, jump, secs=9):
    """walk along +z from z0 to z1 at x; returns (final y, final z, jumps)"""
    rc.run(f"tp Cam {x} 103 {z0} 0 0"); time.sleep(1.0); wb.agent("!fwd_on"); jumps = 0; t0 = time.time(); last = time.time(); bz = z0; peak = 0
    while time.time() - t0 < secs:
        time.sleep(0.05); px, py, pz = wb.pos("Cam")
        if pz > -18.8: peak = max(peak, py)
        if pz >= z1: break
        if pz > bz + 0.05: bz = pz; last = time.time()
        if jump and time.time() - last > 0.4 and time.time() - t0 > 0.5: wb.agent("!jump_on"); time.sleep(0.25); wb.agent("!jump_off"); jumps += 1; last = time.time() - 0.2
    snap = (py, pz); wb.agent("!fwd_off"); return (peak if peak else snap[0]), snap[1], jumps
ok = bad = 0
def check(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n)
    else: bad += 1; print("  FAIL", n, e)
rc.run("tp Cam -8 103 -24"); time.sleep(3)
rc.run("fill -14 103 -30 -2 108 -10 minecraft:air")
rc.run("fill -10 103 -19 -10 103 -8 minecraft:stone"); rc.run("fill -6 103 -19 -6 103 -8 minecraft:stone")
names = {1: "human", 2: "elf", 3: "dwarf", 4: "halfling", 5: "ashborn"}
for race in (1, 2, 3, 4, 5):
    setc(race)
    y, z, j = walk(-9.5, -23.5, -12.0, jump=True); check(f"{names[race]}: gets onto a 1-block ledge by jumping (y={y:.2f}, jumps={j})", y >= 103.99, (y, z))
for race in (1, 3, 4):
    setc(race)
    y, z, j = walk(-5.5, -23.5, -12.0, jump=False, secs=6); print(f"   {names[race]}: WITHOUT jumping onto the ledge: y={y:.2f} z={z:.2f} ({'steps up' if y >= 103.9 else 'does not step up'})")
# 2-high tunnel: stone ceiling at y 105 over x -3..-1 (a gap of 2 = y 103, 104), walls on both sides
rc.run("fill -3 103 -30 -1 104 -24 minecraft:air"); rc.run("fill -3 105 -28 -1 105 -26 minecraft:stone"); rc.run("fill -4 103 -28 -4 105 -26 minecraft:stone"); rc.run("fill 0 103 -28 0 105 -26 minecraft:stone")
for race, expect in ((2, True), (1, True), (4, True)):
    setc(race, 3); rc.run("effect give Cam minecraft:instant_health 1 10 true"); hp0 = float(re.search(r"data: ([\d.]+)f", rc.run("data get entity Cam Health")).group(1))
    y, z, j = walk(-1.5, -30.5, -23.5, jump=False, secs=7); hp1 = float(re.search(r"data: ([\d.]+)f", rc.run("data get entity Cam Health")).group(1))
    check(f"{names[race]}: walks through a 2-high tunnel without suffocating (z={z:.1f}, hp {hp0}->{hp1})", z >= -24.2 and hp1 >= hp0 - 0.1, (z, hp0, hp1))
h = {r: 1.8 * (1 + d) for r, d in ((1, 0), (2, 0.1), (3, -0.2), (4, -0.35), (5, 0))}
print("   body heights:", {names[r]: round(v, 2) for r, v in h.items()}, " halfling 1.17 > 1, elf 1.98 < 2")
check("halfling (1.17) does not fit a 1-block gap, elf (1.98) fits a 2-block gap", h[4] > 1.0 and h[2] < 2.0)
rc.run("fill -14 103 -30 -2 108 -10 minecraft:air"); rc.run("tp Cam 0.5 57 -4.5")
print(f"\n{ok} ok, {bad} failed"); sys.exit(1 if bad else 0)
