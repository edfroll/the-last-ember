#!/usr/bin/env python3
"""T-026: placeholder textures and models of the heads in the pools of the Crooked Fens (generated, no PIL): a skull in slime with
glowing eyes (light_emission 15), two states - eyes open / eyes closed. Item models last_ember:fens/head_open, last_ember:fens/head_closed
(shown by item_display entities of the datapack, function/fens/gen/rise_<k>).
  python3 tools/make_fens_textures.py"""
import json, os, struct, zlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "resourcepack/assets/last_ember")
def png(path, px):
    h, w = len(px), len(px[0]); os.makedirs(os.path.dirname(path), exist_ok=True)
    raw = b"".join(b"\x00" + b"".join(bytes(p) for p in row) for row in px)
    def chunk(t, d): c = struct.pack(">I", len(d)) + t + d; return c + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
def hsh(x, y, s=0):
    n = (x * 73856093) ^ (y * 19349663) ^ (s * 83492791); n &= 0xffffffff; n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff; n ^= n >> 16
    return (n & 0xffff) / 0x10000
BONE = [(158, 150, 118), (143, 136, 104), (170, 162, 128)]
SLIME = [(58, 74, 40), (46, 60, 32), (72, 88, 46)]
def skull():
    px = []
    for y in range(16):
        row = []
        for x in range(16):
            r = hsh(x, y, 1)
            slime = y >= 10 - int(hsh(x, 0, 2) * 3) or (hsh(x // 2, y // 2, 3) < 0.18)       # slime from below, patches of weed
            c = SLIME[int(r * 3)] if slime else BONE[int(r * 3)]
            if not slime and hsh(x, y, 4) < 0.06: c = (96, 88, 66)                         # cracks
            row.append(c + (255,))
        px.append(row)
    return px
def face(open_):
    """the front: dark sockets with glowing eyes (open) or with a slit of a lid (closed), a nose hole, the teeth; the rest transparent"""
    px = [[(0, 0, 0, 0)] * 16 for _ in range(16)]
    for (cx, cy) in ((4, 6), (11, 6)):
        for dy in (-1, 0, 1):
            for dx in (-2, -1, 0, 1):
                x, y = cx + dx, cy + dy
                if open_:
                    core = abs(dx + 0.5) < 1 and dy == 0
                    px[y][x] = (214, 255, 120, 255) if core else (120, 200, 60, 255)
                else:
                    px[y][x] = (40, 36, 26, 255) if dy != 0 else (88, 120, 50, 255)
    for (x, y) in ((7, 9), (8, 9), (7, 10), (8, 10)): px[y][x] = (30, 26, 18, 255)
    for x in range(4, 12): px[12][x] = (200, 192, 160, 255) if x % 2 else (30, 26, 18, 255)
    return px
png(os.path.join(OUT, "textures/item/fens/skull.png"), skull())
png(os.path.join(OUT, "textures/item/fens/eyes_open.png"), face(True))
png(os.path.join(OUT, "textures/item/fens/eyes_closed.png"), face(False))
def model(state):
    sk = "last_ember:item/fens/skull"; fc = "last_ember:item/fens/eyes_%s" % state
    faces = {d: {"uv": [0, 0, 16, 16], "texture": "#skull"} for d in ("north", "south", "east", "west", "up", "down")}
    el = [{"from": [3, 0, 3], "to": [13, 9, 13], "faces": faces},                                   # the skull
          {"from": [4, -4, 4], "to": [12, 0, 12], "faces": {d: {"uv": [0, 10, 16, 16], "texture": "#skull"} for d in ("north", "south", "east", "west", "down")}},   # under the water
          {"from": [3, 0, 2.95], "to": [13, 9, 2.95], "faces": {"north": {"uv": [0, 0, 16, 16], "texture": "#face"}}, "light_emission": 15 if state == "open" else 0},
          {"from": [3, 0, 13.05], "to": [13, 9, 13.05], "faces": {"south": {"uv": [0, 0, 16, 16], "texture": "#face"}}, "light_emission": 15 if state == "open" else 0}]
    return {"textures": {"skull": sk, "face": fc, "particle": sk}, "elements": el,
            "display": {"head": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]}, "fixed": {"scale": [1, 1, 1]}}}
for state in ("open", "closed"):
    p = os.path.join(OUT, "models/item/fens/head_%s.json" % state); os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(model(state), open(p, "w"), indent=1)
    p = os.path.join(OUT, "items/fens/head_%s.json" % state); os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump({"model": {"type": "minecraft:model", "model": "last_ember:item/fens/head_%s" % state}}, open(p, "w"))
print("fens heads: 2 models, 3 textures")
