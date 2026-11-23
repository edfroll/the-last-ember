#!/usr/bin/env python3
"""T-030: placeholder skin of the Advisor (resource pack, for the mannequin's profile texture last_ember:entity/advisor): an old mage in a
grey hooded cloak, a grey beard, the pipe (item model last_ember:advisor_pipe: a 16 x 16 sprite). Classic 64 x 64 player skin layout (wide
arms). Deterministic (a hash, no randomness): tools/check_gen.sh runs it.
  python3 tools/make_advisor_skin.py"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab"))
import png

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(ROOT, "resourcepack/assets/last_ember")

def h(x, y, s):
    n = (x * 374761393 + y * 668265263 + s * 2654435761) & 0xffffffff
    n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff
    return ((n ^ (n >> 16)) & 0xffff) / 65535.0

CLOAK = [(92, 92, 98), (84, 84, 90), (100, 100, 106), (78, 78, 84)]
CLOAK_D = [(62, 62, 68), (56, 56, 62), (68, 68, 74)]
BEARD = [(206, 206, 202), (190, 190, 186), (222, 222, 218), (176, 176, 172)]
SKIN = [(196, 150, 120), (186, 140, 112), (204, 160, 128)]
SKIN_D = (150, 106, 84)
BOOT = [(58, 42, 30), (66, 48, 34)]
BELT = (74, 54, 36)
EYE = (40, 50, 64)
BROW = (170, 170, 166)

def pick(pal, x, y, s): return pal[int(h(x, y, s) * len(pal)) % len(pal)] + (255,)
def skin():
    img = [[(0, 0, 0, 0)] * 64 for _ in range(64)]
    def box(x1, y1, x2, y2, f):
        for y in range(y1, y2):
            for x in range(x1, x2): img[y][x] = f(x - x1, y - y1, x, y)
    cloak = lambda u, v, x, y: pick(CLOAK if h(x // 2, y, 5) > 0.22 else CLOAK_D, x, y, 1)
    # ---- head (base layer): the face, the beard over the lower half, the hood's shadow
    box(8, 0, 16, 8, cloak); box(16, 0, 24, 8, lambda u, v, x, y: pick(BEARD, x, y, 2))
    box(0, 8, 8, 16, lambda u, v, x, y: pick(BEARD, x, y, 2) if v >= 4 and u >= 4 else cloak(u, v, x, y))
    box(16, 8, 24, 16, lambda u, v, x, y: pick(BEARD, x, y, 2) if v >= 4 and u < 4 else cloak(u, v, x, y))
    box(24, 8, 32, 16, cloak)
    def face(u, v, x, y):
        if v == 0: return pick(CLOAK_D, x, y, 3)
        if v == 2 and u in (1, 2, 5, 6): return BROW + (255,)
        if v == 3 and u in (2, 5): return EYE + (255,)
        if v == 3 and u in (1, 6): return (230, 230, 226, 255)
        if v == 4 and u in (3, 4): return SKIN_D + (255,)
        if v >= 5 or (v == 4 and u in (0, 1, 6, 7)): return pick(BEARD, x, y, 2)
        return pick(SKIN, x, y, 4)
    box(8, 8, 16, 16, face)
    # ---- the hood (hat layer): over the top, the sides and the back, a rim round the face; the beard hangs out in front
    box(40, 0, 48, 8, cloak); box(48, 0, 56, 8, lambda u, v, x, y: (0, 0, 0, 0))
    box(32, 8, 40, 16, lambda u, v, x, y: cloak(u, v, x, y) if v < 6 else (0, 0, 0, 0))
    box(48, 8, 56, 16, lambda u, v, x, y: cloak(u, v, x, y) if v < 6 else (0, 0, 0, 0))
    box(56, 8, 64, 16, cloak)
    box(40, 8, 48, 16, lambda u, v, x, y: cloak(u, v, x, y) if v == 0 or (v < 5 and u in (0, 7)) else
        (pick(BEARD, x, y, 6) if v == 7 and u in (2, 3, 4, 5) else (0, 0, 0, 0)))
    # ---- body: cloak, the beard over the chest, a belt
    def body(u, v, x, y):
        if v == 6: return BELT + (255,)
        if v < 3 and 1 <= u <= 6: return pick(BEARD, x, y, 2)
        if v == 3 and 2 <= u <= 5: return pick(BEARD, x, y, 2)
        return cloak(u, v, x, y)
    box(20, 16, 28, 20, cloak); box(28, 16, 36, 20, cloak)
    box(16, 20, 20, 32, cloak); box(20, 20, 28, 32, body); box(28, 20, 32, 32, cloak); box(32, 20, 40, 32, cloak)
    # ---- arms: sleeves of the cloak, hands
    def arm(u, v, x, y): return pick(SKIN, x, y, 4) if v >= 10 else cloak(u, v, x, y)
    for (ax, ay) in ((40, 16), (32, 48)):
        box(ax + 4, ay, ax + 8, ay + 4, cloak); box(ax + 8, ay, ax + 12, ay + 4, lambda u, v, x, y: pick(SKIN, x, y, 4))
        box(ax, ay + 4, ax + 16, ay + 16, arm)
    # ---- legs: the cloak down to the boots
    def leg(u, v, x, y): return pick(BOOT, x, y, 7) if v >= 10 else cloak(u, v, x, y)
    for (lx, ly) in ((0, 16), (16, 48)):
        box(lx + 4, ly, lx + 8, ly + 4, cloak); box(lx + 8, ly, lx + 12, ly + 4, lambda u, v, x, y: pick(BOOT, x, y, 7))
        box(lx, ly + 4, lx + 16, ly + 16, leg)
    # ---- the cloak's outer layer: over the back and the sides of the body (the jacket layer), open in front
    def jacket(u, v, x, y): return cloak(u, v, x, y)
    box(20, 32, 28, 36, jacket); box(28, 32, 36, 36, jacket)
    box(16, 36, 20, 48, jacket); box(28, 36, 32, 48, jacket); box(32, 36, 40, 48, jacket)
    box(20, 36, 28, 48, lambda u, v, x, y: jacket(u, v, x, y) if u in (0, 7) else (0, 0, 0, 0))
    return img

PIPE = [
    "................",
    "................",
    "................",
    "..........gg....",
    ".........gwwg...",
    "..........gg....",
    "..........ww....",
    ".........BBBB...",
    ".........BbbB...",
    "........dBbbB...",
    ".......d.BBB....",
    "......d.........",
    ".....d..........",
    "....d...........",
    "...d............",
    "................"]
PAL = {"B": (96, 62, 36, 255), "b": (40, 26, 18, 255), "d": (120, 82, 48, 255), "g": (190, 190, 190, 150), "w": (230, 230, 230, 110)}

def main():
    os.makedirs(os.path.join(RP, "textures/entity"), exist_ok=True)
    png.write(os.path.join(RP, "textures/entity/advisor.png"), skin())
    os.makedirs(os.path.join(RP, "textures/item"), exist_ok=True)
    png.write(os.path.join(RP, "textures/item/advisor_pipe.png"), [[PAL.get(c, (0, 0, 0, 0)) for c in row] for row in PIPE])
    os.makedirs(os.path.join(RP, "models/item"), exist_ok=True); os.makedirs(os.path.join(RP, "items"), exist_ok=True)
    json.dump({"parent": "minecraft:item/handheld", "textures": {"layer0": "last_ember:item/advisor_pipe"}}, open(os.path.join(RP, "models/item/advisor_pipe.json"), "w"))
    json.dump({"model": {"type": "minecraft:model", "model": "last_ember:item/advisor_pipe"}}, open(os.path.join(RP, "items/advisor_pipe.json"), "w"))
    print("advisor skin and pipe written")

if __name__ == "__main__":
    main()
