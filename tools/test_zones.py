#!/usr/bin/env python3
"""T-004 tests (server + client 'Cam' online, test zones compiled in: gen_zones.py zones/test_zones.txt).
Moves the real player with /tp and checks the game mode, measures switch latency in ticks, death/respawn, pearl entry,
fall entry, TNT/creeper/fireball next to a zone wall, fire spread, falling blocks. Prints PASS/FAIL lines."""
import importlib.util, os, re, socket, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("rcon", os.path.join(ROOT, "tools/rcon.py")); rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
p = rc.props(); S = socket.create_connection(("127.0.0.1", int(p["rcon.port"])), timeout=30); rc.pkt(S, 1, 3, p["rcon.password"]); rc.read(S)
def R(c): return rc.exchange(S, c)
P = "Cam"; results = []
def ok(name, cond, info=""):
    results.append(cond); print(("PASS " if cond else "FAIL ") + name + (f"  [{info}]" if info else ""), flush=True)
def mode(): 
    for m in ("adventure", "survival", "creative", "spectator"):
        if "passed" in R(f"execute if entity @a[name={P},gamemode={m}]"): return m
def wait_mode(m, timeout=1.5):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if mode() == m: return round((time.time() - t0) * 20, 1)
        time.sleep(0.01)
    return None
def tp(x, y, z): R(f"tp {P} {x} {y} {z}")
def at(x, y, z, m, name):
    tp(x, y, z); t = wait_mode(m); ok(f"{name}: at ({x},{y},{z}) mode {m}", t is not None, f"switch after ~{t} ticks" if t is not None else f"mode={mode()}")

R("time set noon"); R("weather clear"); R(f"gamemode survival {P}"); R(f"effect give {P} minecraft:resistance infinite 255 true"); R(f"effect give {P} minecraft:slow_falling 1 0 true")
for a in ("-128 -32 47 191", "48 -32 223 191"): print(R(f"execute in minecraft:overworld run forceload add {a}"))
print(R("execute in minecraft:overworld run forceload add 288 288 319 319"))
time.sleep(2)
R(f"tp {P} 300 120 300"); time.sleep(0.5)
at(300, 120, 300, "survival", "outside all zones")
# box t_box 0..31, y 60..100 (margin 5)
at(16, 80, 16, "adventure", "box inside")
at(-4, 80, 16, "adventure", "box edge margin (x=-4, wall x=0)")
at(-7, 80, 16, "survival", "box outside margin (x=-7)")
at(16, 106, 16, "survival", "box above ceiling+margin (y=106)")
# cylinder t_cyl center (100,16) r 60, y 0..100
at(155, 80, 16, "adventure", "cylinder inside (r=55)")
at(166, 80, 16, "survival", "cylinder outside (r=66 > 60+5)")
# overlapping A(-100..-70) B(-80..-50) and leaving
at(-95, 80, 0, "adventure", "overlap: only A")
at(-75, 80, 0, "adventure", "overlap: A and B")
at(-55, 80, 0, "adventure", "overlap: only B")
at(-40, 80, 0, "survival", "overlap: left B")
# nested outer(0..60,100..160) inner(20..40,120..140, no_blink)
at(30, 80, 130, "adventure", "nested: inner"); time.sleep(0.3)
ok("nested: inner sets flag tag le.zf.no_blink", "passed" in R(f"execute if entity @a[name={P},tag=le.zf.no_blink]"))
at(5, 80, 105, "adventure", "nested: outer only"); time.sleep(0.3)
ok("nested: outer only has no flag tag", "failed" in R(f"execute if entity @a[name={P},tag=le.zf.no_blink]"))
at(70, 80, 175, "survival", "nested: outside both")
# flag no_spawn in t_ovA: monsters removed
R("summon minecraft:zombie -90 80 0 {Tags:[\"le.t\"],PersistenceRequired:1b}"); R("summon minecraft:zombie -60 80 0 {Tags:[\"le.t2\"],PersistenceRequired:1b}")
time.sleep(2.5)
ok("no_spawn: zombie inside A removed", "failed" in R("execute if entity @e[tag=le.t]"))
ok("no_spawn: zombie in B (no flag) stays", "passed" in R("execute if entity @e[tag=le.t2]")); R("kill @e[tag=le.t2]")
# death inside a zone, respawn outside
tp(16, 80, 16); wait_mode("adventure")
R(f"spawnpoint {P} 300 120 300"); R(f"effect clear {P} minecraft:resistance"); R(f"kill {P}"); time.sleep(2.5)
t = wait_mode("survival", 3); ok("death in zone -> respawn outside -> survival", t is not None, f"mode={mode()}")
R(f"effect give {P} minecraft:resistance infinite 255 true")
# fall into the box from high above (fast path every tick when fall_distance >= 3)
tp(16, 200, 16); R(f"effect clear {P} minecraft:slow_falling"); y_switch = None; t0 = time.time()
while time.time() - t0 < 6:
    if mode() == "adventure":
        m = re.search(r"\[[^,]*, ([-\d.]+)d", R(f"data get entity {P} Pos")); y_switch = float(m.group(1)) if m else None; break
ok("fall from y 200 into box: adventure before reaching ceiling+margin (y<=105)", y_switch is not None and y_switch > 100, f"switched at y={y_switch}")
tp(300, 120, 300); wait_mode("survival")
# ender pearl thrown by the player, lands in the box
uuid = re.search(r"\[I; ?(-?\d+), ?(-?\d+), ?(-?\d+), ?(-?\d+)\]", R(f"data get entity {P} UUID")).groups()
tp(-20, 80, 16); wait_mode("survival")
R(f"summon minecraft:ender_pearl 16 104 16 {{Owner:[I;{','.join(uuid)}],Motion:[0.0d,-1.5d,0.0d]}}")
t0 = time.time(); landed = None
while time.time() - t0 < 4:
    m = re.search(r"\[([-\d.]+)d", R(f"data get entity {P} Pos"))
    if m and float(m.group(1)) > -10: landed = time.time(); break
    time.sleep(0.01)
t = wait_mode("adventure", 2)
ok("ender pearl into the box -> adventure", landed is not None and t is not None, f"after landing ~{t} ticks")
tp(300, 120, 300); wait_mode("survival")
# --- blocks: wall at x=0..1, z 10..20, y 80..85 inside t_box
R("fill 0 80 10 1 85 20 minecraft:stone_bricks"); R("fill -6 79 8 -1 86 22 minecraft:air"); R("fill -6 78 8 -1 78 22 minecraft:stone")
def wall_ok(): return "passed" in R("execute if blocks 0 80 10 1 85 20 0 80 10 all") and "passed" not in R("execute if block 0 82 15 minecraft:air")
def count(box, block):
    """number of `block` in box: swap to a marker block and back (fill only reports changed blocks)"""
    m = re.search(r"(\d+)", R(f"fill {box} minecraft:sponge replace {block}")); R(f"fill {box} {block} replace minecraft:sponge"); return int(m.group(1)) if m else 0
def wall_count(): return count("0 80 10 1 85 20", "minecraft:stone_bricks")
base = wall_count()
R("summon minecraft:tnt -2 80 15 {fuse:30}"); time.sleep(2.5)
ok("TNT 2 blocks from the zone wall: wall intact", wall_count() == base == 132, f"bricks {wall_count()}/{base}")
# control: TNT far from zones explodes and breaks blocks
R("fill 300 100 300 304 104 304 minecraft:stone_bricks"); R("summon minecraft:tnt 302 105 302 {fuse:20}"); time.sleep(2)
n = count("300 100 300 304 104 304", "minecraft:stone_bricks")
ok("control: TNT away from zones still breaks blocks", n < 125, f"bricks left {n}/125")
R("summon minecraft:creeper -2 80 15 {ignited:1b,Fuse:1s}"); time.sleep(1.5)
ok("creeper exploding at the wall: wall intact", wall_count() == 132)
R("summon minecraft:fireball -3 82 15 {ExplosionPower:3b,Motion:[1.0d,0.0d,0.0d],power:[0.1d,0.0d,0.0d]}"); time.sleep(1.5)
ok("ghast fireball into the wall: wall intact, no fire", wall_count() == 132 and "failed" in R("execute if entity @e[type=minecraft:fireball]"))
# fire next to planks inside the zone
R("fill 2 80 30 2 82 31 minecraft:oak_planks"); R("setblock 2 80 32 minecraft:oak_planks"); R("setblock 2 81 32 minecraft:fire")
time.sleep(12)
n = count("2 80 30 2 82 31", "minecraft:oak_planks")
ok("fire next to zone planks: no spread (12 s)", n == 6, f"planks {n}/6")
print(f"\n{sum(results)}/{len(results)} passed")
