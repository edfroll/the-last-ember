#!/usr/bin/env python3
"""T-012: the ring's icon (16x16) and the camera overlay of the world of shadows (256x256, grey mist, darker at the edges, semi-transparent)."""
import math, os, struct, zlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "resourcepack/assets/last_ember")
def png(path, w, h, px):
    raw = b"".join(b"\x00" + b"".join(bytes(p) for p in row) for row in px)
    def chunk(t, d): c = struct.pack(">I", len(d)) + t + d; return c + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
for d in ("textures/item", "textures/misc", "models/item", "items"): os.makedirs(os.path.join(OUT, d), exist_ok=True)
px = [[(0, 0, 0, 0)] * 16 for _ in range(16)]
for y in range(16):
    for x in range(16):
        r = math.hypot(x - 7.5, y - 9.0)
        if 3.2 <= r <= 5.4: px[y][x] = (200, 200, 210, 255) if (x + y) % 5 else (150, 150, 165, 255)
for (x, y) in ((7, 3), (8, 3), (7, 2), (8, 2)): px[y][x] = (110, 150, 230, 255)
png(os.path.join(OUT, "textures/item/ring.png"), 16, 16, px)
S = 256; px = []
for y in range(S):
    row = []
    for x in range(S):
        r = math.hypot((x - 127.5) / 127.5, (y - 127.5) / 127.5)           # 0 at the centre, 1.41 in the corners
        a = 0.40 + 0.52 * min(1.0, max(0.0, (r - 0.35) / 0.9)) ** 1.6      # thin mist in the middle, thick dark at the edges
        n = (math.sin(x * 0.11 + y * 0.05) + math.sin(y * 0.13 - x * 0.04)) * 0.03
        g = int(max(0, min(255, (118 - 70 * min(1.0, r / 1.2)) * (1 + n))))
        row.append((g, g, min(255, g + 8), int(255 * max(0.0, min(0.94, a + n)))))
    px.append(row)
png(os.path.join(OUT, "textures/misc/ring_mist.png"), S, S, px)
open(os.path.join(OUT, "models/item/ring.json"), "w").write('{ "parent": "minecraft:item/generated", "textures": { "layer0": "last_ember:item/ring" }, "display": { "head": { "scale": [0, 0, 0] } } }\n')
open(os.path.join(OUT, "items/ring.json"), "w").write('{ "model": { "type": "minecraft:model", "model": "last_ember:item/ring" } }\n')
print("ring textures done")
