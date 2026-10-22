#!/usr/bin/env python3
"""T-011: placeholder staff textures (16x16): a brown shaft and a coloured head per staff. Real models come with the characters' resource pack."""
import os, struct, zlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "resourcepack/assets/last_ember")
HEADS = {"blink": ((150, 90, 230), (190, 230, 255)), "frost": ((120, 200, 255), (235, 250, 255)), "flame": ((255, 120, 20), (255, 220, 90)),
         "lift": ((225, 225, 235), (150, 150, 165)), "banish": ((70, 200, 110), (170, 255, 190)), "wrath": ((150, 20, 30), (255, 230, 80))}
def png(path, px):
    raw = b"".join(b"\x00" + b"".join(bytes(p) for p in row) for row in px)
    def chunk(t, d): c = struct.pack(">I", len(d)) + t + d; return c + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 16, 16, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
os.makedirs(os.path.join(OUT, "textures/item"), exist_ok=True); os.makedirs(os.path.join(OUT, "models/item"), exist_ok=True); os.makedirs(os.path.join(OUT, "items"), exist_ok=True)
for name, (c1, c2) in HEADS.items():
    px = [[(0, 0, 0, 0)] * 16 for _ in range(16)]
    for i in range(10):                       # the shaft from the lower left to the upper right
        x, y = 2 + i, 14 - i
        px[y][x] = (110, 72, 38, 255); px[y][x + 1 if x + 1 < 16 else x] = (84, 54, 28, 255)
    for dy in range(-2, 3):                   # the head: an orb of radius ~2.5 at (12, 3)
        for dx in range(-2, 3):
            if dx * dx + dy * dy <= 5:
                x, y = 12 + dx, 3 + dy
                if 0 <= x < 16 and 0 <= y < 16: px[y][x] = (*c1, 255)
    px[2][11] = (*c2, 255); px[2][12] = (*c2, 255); px[3][11] = (*c2, 255)
    png(os.path.join(OUT, f"textures/item/staff_{name}.png"), px)
    open(os.path.join(OUT, f"models/item/staff_{name}.json"), "w").write('{ "parent": "minecraft:item/handheld", "textures": { "layer0": "last_ember:item/staff_%s" } }\n' % name)
    open(os.path.join(OUT, f"items/staff_{name}.json"), "w").write('{ "model": { "type": "minecraft:model", "model": "last_ember:item/staff_%s" } }\n' % name)
print("staff textures:", list(HEADS))
