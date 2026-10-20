#!/usr/bin/env python3
"""Draws the Ember item texture: 16x16, 8-frame vertical strip (smouldering coal, flickering cracks). No PIL needed."""
import math, os, struct, zlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "resourcepack/assets/last_ember/textures/item/ember.png")
W, FR = 16, 8
def h(x, y, s=0): n = (x * 73856093 ^ y * 19349663 ^ s * 83492791) & 0xffffffff; n = (n ^ (n >> 13)) * 1274126177 & 0xffffffff; return (n & 0xffff) / 65535
shape = [  # coal lump silhouette, '#' body
"................",
"......####......",
"....########....",
"...##########...",
"..############..",
"..#############.",
".##############.",
".##############.",
".##############.",
".#############..",
"..############..",
"..###########...",
"...#########....",
"....#######.....",
"......###.......",
"................"]
cracks = {(5,4),(6,5),(7,6),(8,6),(9,7),(10,8),(4,8),(5,9),(6,9),(7,10),(9,10),(10,11),(11,6),(12,7),(6,12),(7,12)}
rows = []
for f in range(FR):
    t = f / FR * 2 * math.pi
    for y in range(W):
        row = b"\x00"
        for x in range(W):
            if shape[y][x] != "#": row += bytes((0, 0, 0, 0)); continue
            edge = any(shape[yy][xx] != "#" for xx, yy in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)) if 0 <= xx < W and 0 <= yy < W)
            base = 26 + int(h(x, y) * 18)
            r, g, b = base, base - 4, base - 6
            if (x, y) in cracks:
                k = 0.55 + 0.45 * math.sin(t + h(x, y, 1) * 6.28)
                r, g, b = int(200 + 55 * k), int(70 + 90 * k), int(10 + 30 * k)
            elif h(x, y, 2) > 0.86:
                k = 0.5 + 0.5 * math.sin(t * 2 + h(x, y, 3) * 6.28)
                r, g, b = int(90 + 80 * k), int(30 + 30 * k), 8
            if edge: r, g, b = r // 2 + 10, g // 2 + 6, b // 2 + 4
            row += bytes((max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))
        rows.append(row)
raw = b"".join(rows)
def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, W * FR, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
open(OUT, "wb").write(png); print(OUT, len(png), "bytes")
