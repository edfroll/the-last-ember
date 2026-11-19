#!/usr/bin/env python3
"""T-025: placeholder textures of the Creaking armour (generated, no PIL): the worn layers (equipment asset last_ember:creaking:
textures/entity/equipment/humanoid[_leggings]/creaking.png, 64x32) - pale bark with dark veins, eye slits on the helmet - and the 4
item icons (textures/item/creaking_<piece>.png, 16x16) with their models and item definitions. Vanilla textures are not touched.
  python3 tools/make_creak_textures.py"""
import json, math, os, struct, zlib
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
PALE = [(214, 208, 196), (200, 194, 182), (188, 181, 168), (226, 221, 210)]
VEIN = [(74, 68, 62), (92, 86, 78), (58, 54, 50)]
def bark(x, y, s=0):
    """pale bark: vertical grain, dark veins that wander (column offset by a slow sine)"""
    v = (x + int(2 * math.sin(y * 0.55 + x * 0.3 + s))) % 5
    if v == 0 and hsh(x, y // 3, s + 7) < 0.75: return VEIN[int(hsh(x, y, s + 3) * 3)] + (255,)
    return PALE[int(hsh(x, y, s + 1) * 4)] + (255,)
# ---- worn layers (64x32 humanoid layout): head 0..32 x 0..16, body 16..40 x 16..32, arms 40..56 x 16..32, legs 0..16 x 16..32
def layer(regions, eyes=False):
    px = [[(0, 0, 0, 0)] * 64 for _ in range(32)]
    for (x1, y1, x2, y2) in regions:
        for y in range(y1, y2):
            for x in range(x1, x2): px[y][x] = bark(x, y)
    if eyes:      # the helmet's front face is (8,8)-(16,16): two narrow dark slits and a dark brow line
        for x in (9, 10, 13, 14): px[11][x] = (24, 20, 18, 255)
        for x in (9, 14): px[12][x] = (40, 34, 30, 255)
        for x in range(8, 16): px[9][x] = VEIN[0] + (255,)
    return px
png(os.path.join(OUT, "textures/entity/equipment/humanoid/creaking.png"),
    layer([(0, 0, 32, 16), (16, 16, 40, 32), (40, 16, 56, 32), (0, 16, 16, 32)], eyes=True))
png(os.path.join(OUT, "textures/entity/equipment/humanoid_leggings/creaking.png"), layer([(0, 16, 16, 32), (16, 16, 40, 32)]))
json.dump({"layers": {"humanoid": [{"texture": "last_ember:creaking"}], "humanoid_leggings": [{"texture": "last_ember:creaking"}]}},
          open(os.path.join(OUT, "equipment/creaking.json"), "w"), indent=1)
# ---- item icons: masks ('#' bark, 'o' dark outline, 'e' eye slit)
ICONS = {
 "helmet": ["................", "................", "................", "....oooooooo....", "...o########o...", "..o##########o..", "..o##########o..",
            "..o#ee####ee#o..", "..o##########o..", "..o###oooo###o..", "..o##o....o##o..", "...oo......oo...", "................", "................", "................", "................"],
 "chestplate": ["................", "..ooo......ooo..", ".o###o....o###o.", ".o####oooo####o.", ".o############o.", "..oo########oo..", "...o########o...",
                "...o########o...", "...o########o...", "...o########o...", "...o########o...", "...o########o...", "...o########o...", "...oooooooooo...", "................", "................"],
 "leggings": ["................", "...oooooooooo...", "...o########o...", "...o########o...", "...o###oo###o...", "...o###oo###o...", "...o###oo###o...",
              "...o###oo###o...", "...o###oo###o...", "...o###oo###o...", "...o###oo###o...", "...o###oo###o...", "...oooooooooo...", "................", "................", "................"],
 "boots": ["................", "................", "................", "................", "................", "...oooo..oooo...", "...o##o..o##o...",
           "...o##o..o##o...", "...o##o..o##o...", "...o##o..o##o...", "..o###o..o###o..", ".o####o..o####o.", ".o####o..o####o.", ".oooooo..oooooo.", "................", "................"],
}
for name, rows in ICONS.items():
    px = []
    for y, row in enumerate(rows):
        line = []
        for x, c in enumerate(row):
            line.append(bark(x * 3, y * 2, 5) if c == "#" else (52, 46, 42, 255) if c == "o" else (20, 16, 14, 255) if c == "e" else (0, 0, 0, 0))
        px.append(line)
    png(os.path.join(OUT, "textures/item/creaking_%s.png" % name), px)
    json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": "last_ember:item/creaking_%s" % name}},
              open(os.path.join(OUT, "models/item/creaking_%s.json" % name), "w"), indent=1)
    json.dump({"model": {"type": "minecraft:model", "model": "last_ember:item/creaking_%s" % name}}, open(os.path.join(OUT, "items/creaking_%s.json" % name), "w"), indent=1)
print("creaking armour textures done")
