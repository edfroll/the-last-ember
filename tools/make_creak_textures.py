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
# tones of the vanilla bark (review T-025, point 5): the base is stripped pale oak greyed to a grey-beige (3 shades), the veins are the bark of the
# pale oak log, the rims of the plates one step darker than the base, the eye slits dark with a dull ember of the creaking's orange
BASE = [(200, 190, 181), (189, 179, 170), (209, 200, 191)]
RIM = (165, 154, 146)
VEIN = [(78, 67, 64), (94, 83, 80), (67, 59, 57)]
SLIT, EMBER = (40, 34, 31), (168, 90, 32)
def base(x, y, s=0):
    n = hsh(x, y, s + 1); g = hsh(x // 2, y // 3, s + 2)        # soft grain: patches 2x3 of one shade, a little speckle
    return BASE[0 if g < 0.5 else 1 if g < 0.8 else 2] if n > 0.15 else BASE[int(n * 20) % 3]
def veins(px, x1, y1, x2, y2, s):
    """dark vertical veins 3..8 long that wander by one pixel and fork; about one start per 26 pixels of the region, no spots"""
    w, h = x2 - x1, y2 - y1; n = max(1, (w * h) // 26)
    for k in range(n):
        x = x1 + int(hsh(k, 1, s) * w); y = y1 + int(hsh(k, 2, s) * h); L = 3 + int(hsh(k, 3, s) * 6)
        stack = [(x, y, L, 0)]
        while stack:
            x, y, L, depth = stack.pop()
            for i in range(L):
                if not (x1 <= x < x2 and y1 <= y < y2): break
                px[y][x] = VEIN[int(hsh(x, y, s + 9) * 3)] + (255,)
                if depth == 0 and i == L // 2 and hsh(k, 4, s) < 0.6:
                    stack.append((x + (1 if hsh(k, 5, s) < 0.5 else -1), y + 1, 2 + int(hsh(k, 6, s) * 3), 1))
                y += 1
                if hsh(x, y, s + 11) < 0.3: x += 1 if hsh(x, y, s + 12) < 0.5 else -1
# ---- worn layers (64x32 humanoid layout): head 0..32 x 0..16, body 16..40 x 16..32, arms 40..56 x 16..32, legs 0..16 x 16..32
def layer(regions, rims, eyes=False):
    px = [[(0, 0, 0, 0)] * 64 for _ in range(32)]
    for r, (x1, y1, x2, y2) in enumerate(regions):
        for y in range(y1, y2):
            for x in range(x1, x2): px[y][x] = base(x, y) + (255,)
        veins(px, x1, y1, x2, y2, 100 + r)
    for (x1, y1, x2, y2) in rims:                  # the rims of the plates: shoulders, belt, the bottom of the leggings / boots
        for y in range(y1, y2):
            for x in range(x1, x2):
                if px[y][x][3]: px[y][x] = RIM + (255,)
    if eyes:      # the helmet's front face is (8,8)-(16,16): two slits 3x1, each with a dull orange pixel in the middle
        for x0 in (8, 13):
            for i in range(3): px[11][x0 + i] = (EMBER if i == 1 else SLIT) + (255,)
            for i in range(3): px[10][x0 + i] = base(x0 + i, 10) + (255,)     # no vein over the eye
    return px
HEAD, BODY, ARM, LEG = (0, 0, 32, 16), (16, 16, 40, 32), (40, 16, 56, 32), (0, 16, 16, 32)
png(os.path.join(OUT, "textures/entity/equipment/humanoid/creaking.png"),
    layer([HEAD, BODY, ARM, LEG], [(44, 16, 52, 20), (40, 20, 56, 21), (16, 31, 40, 32), (0, 31, 16, 32)], eyes=True))
png(os.path.join(OUT, "textures/entity/equipment/humanoid_leggings/creaking.png"), layer([LEG, BODY], [(16, 20, 40, 21), (0, 31, 16, 32)]))
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
            line.append(base(x, y, 5) + (255,) if c == "#" else VEIN[1] + (255,) if c == "o" else (EMBER if x in (5, 11) else SLIT) + (255,) if c == "e" else (0, 0, 0, 0))
        px.append(line)
    for y, row in enumerate(rows):                 # veins inside the '#' area
        for x, c in enumerate(row):
            if c == "#" and (x + int(1.5 * math.sin(y * 0.7 + x))) % 4 == 0 and hsh(x, y // 3, 8) < 0.55 and row[x - 1] == "#" and row[x + 1] == "#":
                px[y][x] = VEIN[int(hsh(x, y, 9) * 3)] + (255,)
    png(os.path.join(OUT, "textures/item/creaking_%s.png" % name), px)
    json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": "last_ember:item/creaking_%s" % name}},
              open(os.path.join(OUT, "models/item/creaking_%s.json" % name), "w"), indent=1)
    json.dump({"model": {"type": "minecraft:model", "model": "last_ember:item/creaking_%s" % name}}, open(os.path.join(OUT, "items/creaking_%s.json" % name), "w"), indent=1)
print("creaking armour textures done")
