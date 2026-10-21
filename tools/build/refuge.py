#!/usr/bin/env python3
"""T-008 orchestrator: the whole Refuge (Р0) from the builder modules.
  python3 tools/build/refuge.py            -> server/build/refuge/: terrain.png + terrain.json (tools/sculpt.sh apply),
                                              refuge.txt (tools/blockwriter.sh apply), per-piece placements (for .nbt),
                                              markers -> datapack function refuge/gen/markers + docs/reports/T-008-markers.txt
Pipeline (server STOPPED, hub chunks generated): sculpt.sh apply terrain.json -> blockwriter.sh apply refuge.txt -> biomepaint.sh
-> start (bonfire and urn are built by the datapack) -> python3 tools/build/refuge.py nbt (exports .nbt pieces)."""
import math, os, sys, struct, zlib, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import B, Mix, h
import geo, plaza, gates, buildings, tower, hall
from connect import connect
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/refuge")
X0, Z0, N = -210, -210, 421; OFF = 40
def natural():
    nat = {}
    for line in open(os.path.join(OUT, "heights.txt")):
        x, z, y = map(int, line.split()); nat[(x, z)] = y
    return nat
def terrain(nat):
    T = {}
    for x in range(X0, X0 + N):
        for z in range(Z0, Z0 + N):
            n = nat[(x, z)]; t, cut = geo.target(x, z, n)
            if t is None: T[(x, z)] = None; continue
            t = int(round(t))
            if not cut and t < n and math.hypot(x, z) > 90: t = n
            T[(x, z)] = None if t == n and math.hypot(x, z) > 40 else t
    return T
def write_png(path, T):
    rows = []
    for z in range(Z0, Z0 + N):
        row = bytearray([0])
        for x in range(X0, X0 + N):
            t = T[(x, z)]; row.append(0 if t is None else max(1, min(255, t - OFF)))
        rows.append(bytes(row))
    raw = b"".join(rows)
    def chunk(tp, data): c = struct.pack(">I", len(data)) + tp + data; return c + struct.pack(">I", zlib.crc32(tp + data) & 0xffffffff)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", N, N, 8, 0, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    open(path, "wb").write(png)
def ground(T, nat):
    return lambda x, z: (T.get((x, z)) if T.get((x, z)) is not None else nat.get((x, z)))
STREET = Mix({"cobblestone": 40, "gravel": 20, "coarse_dirt": 15, "mossy_cobblestone": 15, "stone_bricks": 10}, 77)
def street(b, gnd, pts, w=2, taken=None):
    """polyline of (x,z); paving at ground height, w = half width"""
    for (ax, az), (bx, bz) in zip(pts, pts[1:]):
        L = max(1, int(math.hypot(bx - ax, bz - az) * 2))
        for i in range(L + 1):
            t = i / L; x, z = ax + (bx - ax) * t, az + (bz - az) * t
            for dx in range(-w, w + 1):
                for dz in range(-w, w + 1):
                    if dx * dx + dz * dz > w * w + 1: continue
                    xi, zi = round(x) + dx, round(z) + dz; y = gnd(xi, zi)
                    if y is None or math.hypot(xi, zi) < 31.5: continue
                    if taken and (xi, y, zi) in taken: continue
                    b.set(xi, y, zi, STREET)
                    for dy in (1, 2, 3):
                        if not taken or (xi, y + dy, zi) not in taken: b.set(xi, y + dy, zi, "air")
def build_all():
    nat = natural(); T = terrain(nat); os.makedirs(OUT, exist_ok=True)
    write_png(os.path.join(OUT, "terrain.png"), T)
    spec = {"name": "refuge", "png": os.path.relpath(os.path.join(OUT, "terrain.png"), ROOT), "x0": X0, "z0": Z0, "offsetY": OFF, "seamWidth": 0,
            "center": [0, 0], "valleyRadius": 0, "lake": {"x": 0, "z": 0, "r": 0, "level": 0}, "snowLine": 400, "stoneLine": 400, "tolerance": 1}
    json.dump(spec, open(os.path.join(OUT, "terrain.json"), "w"), indent=1)
    gnd = ground(T, nat)
    pieces = [hall.build(), plaza.build()]
    pieces += [gates.build(a, r) for a, r in plaza.GATES.items()]
    pieces += [buildings.smithy(), buildings.tavern(), buildings.well(), tower.build()]
    world = {}; markers = []
    holes = hall.plaza_holes()
    for p in pieces:
        for k, s in p.v.items():
            if p.name == "plaza" and k in holes: continue
            world[k] = s
        markers += p.markers
    # streets and the tower path go last and never overwrite a building
    sb = B("streets"); taken = set(k for k, s in world.items() if s != "minecraft:air")
    street(sb, gnd, [geo.rot(0, 0, 125, 32, 0), (40, 21), (52, 21)], 2, taken)
    street(sb, gnd, [geo.rot(0, 0, 240, 32, 0), (-40, 19), (-53, 19)], 2, taken)
    street(sb, gnd, [geo.rot(0, 0, plaza.LANE_WELL, 32, 0), (18, -34), (32, -37)], 1, taken)
    tx, tz = geo.TOWER; sx, sz = round(tx + 28 * math.sin(math.radians(135))), round(tz - 28 * math.cos(math.radians(135)))
    street(sb, gnd, [geo.rot(0, 0, 315, 32, 0), (-60, -50), (sx, sz)], 2, taken)
    tp = B("tower_path"); tower.path(tp, gnd)
    for k, s in tp.v.items():
        if k not in taken: sb.v[k] = s
    for k, s in sb.v.items(): world[k] = s
    pieces.append(sb)
    wb = B("world"); wb.v = world; connect(wb)
    for p in pieces: connect(p)
    with open(os.path.join(OUT, "refuge.txt"), "w") as f:
        for (x, y, z), s in sorted(world.items(), key=lambda kv: (kv[0][1], kv[0][0], kv[0][2])): f.write(f"{x} {y} {z} {s}\n")
    for p in pieces: p.write_placements(os.path.join(OUT, "pieces", p.name + ".txt"))
    hall.build(envelope=False).write_placements(os.path.join(OUT, "pieces", "hall.txt"))   # .nbt without the rock envelope
    for p in hall.sixth_templates() + tuple(hall.statue_pieces()): p.write_placements(os.path.join(OUT, "pieces", p.name + ".txt"))
    write_markers(markers)
    print(f"terrain: {sum(1 for v in T.values() if v is not None)} columns; blocks: {len(world)}; pieces: {len(pieces)}; markers: {len(markers)}")
def write_markers(markers):
    fn = os.path.join(ROOT, "datapack/data/last_ember/function/refuge/gen/markers.mcfunction"); os.makedirs(os.path.dirname(fn), exist_ok=True)
    lines = ["# generated by tools/build/refuge.py: mechanic points of the Refuge (storage only, no entities)", "data remove storage last_ember:refuge m"]
    seen = {}
    for name, x, y, z, note in markers:
        k = name; i = seen.get(k, 0); seen[k] = i + 1
        if i: k = f"{name}_{i}"
        lines.append(f'data modify storage last_ember:refuge m.{k} set value [{x},{y},{z}]')
    open(fn, "w").write("\n".join(lines) + "\n")
    with open(os.path.join(ROOT, "docs/reports/T-008-markers.txt"), "w") as f:
        f.write("# Точки механик Приюта (генерирует tools/build/refuge.py; в игре: storage last_ember:refuge m.<имя> = [x,y,z])\n")
        seen = {}
        for name, x, y, z, note in markers:
            i = seen.get(name, 0); seen[name] = i + 1; k = name if not i else f"{name}_{i}"
            f.write(f"{k:28s} {x:5d} {y:4d} {z:5d}  {note}\n")
NBT_PIECES = ["plaza", "smithy", "tavern", "well", "tower", "hall", "sixth_intact", "sixth_fallen", "statue_humans", "statue_elves", "statue_dwarves",
              "statue_halflings", "statue_ashborn", "gate_r1", "gate_r2", "gate_r3", "gate_r4", "gate_r5", "gate_r6"]
def export_nbt():
    d = os.path.join(ROOT, "datapack/data/last_ember/structure/refuge"); os.makedirs(d, exist_ok=True)
    for n in NBT_PIECES:
        src = os.path.join(OUT, "pieces", n + ".txt")
        xs, ys, zs = [], [], []
        for line in open(src):
            a = line.split(" ", 3); xs.append(int(a[0])); ys.append(int(a[1])); zs.append(int(a[2]))
        subprocess.run([os.path.join(ROOT, "tools/blockwriter.sh"), "nbt", src, str(min(xs)), str(min(ys)), str(min(zs)), os.path.join(d, n + ".nbt")], check=True)
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "nbt": export_nbt()
    else: build_all()
