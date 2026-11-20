#!/usr/bin/env python3
"""T-027: placeholder textures and flat item models of the Cemetery of the Fallen Knights (generated, no PIL): the crypt key (a black iron
key with a skull bow) and the Seal of the Magister (a dark seal with an ash-tree sign). Item models last_ember:cemetery/crypt_key,
last_ember:cemetery/seal (the items: tools/build/cemetery_dp.py).
  python3 tools/make_cemetery_textures.py"""
import json, os, struct, zlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "resourcepack/assets/last_ember")
def png(path, px):
    h, w = len(px), len(px[0]); os.makedirs(os.path.dirname(path), exist_ok=True)
    raw = b"".join(b"\x00" + b"".join(bytes(p) for p in row) for row in px)
    def chunk(t, d): c = struct.pack(">I", len(d)) + t + d; return c + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
def grid(rows, pal):
    return [[pal[ch] for ch in r] for r in rows]
T = (0, 0, 0, 0)
KEY = ["................",
       "....oooo........",
       "...oBBBBo.......",
       "..oBb..bBo......",
       "..oB.bb.Bo......",
       "..oBBBBBBo......",
       "...oBBBBo.......",
       "....oBBo........",
       ".....oBo........",
       ".....oBo........",
       ".....oBoo.......",
       ".....oBBBo......",
       ".....oBoo.......",
       ".....oBBBo......",
       ".....oooo.......",
       "................"]
SEAL = ["................",
        ".....oooooo.....",
        "...ooRRRRRRoo...",
        "..oRRRRRRRRRRo..",
        "..oRRRggRRRRRo..",
        ".oRRRgRRgRRRRRo.",
        ".oRRRRRgRRgRRRo.",
        ".oRRgRRgRgRRRRo.",
        ".oRRRgRgggRRRRo.",
        ".oRRRRRgRRRRRRo.",
        ".oRRRRRgRRRRRRo.",
        "..oRRRRgRRRRRo..",
        "..oRRRRRRRRRRo..",
        "...ooRRRRRRoo...",
        ".....oooooo.....",
        "................"]
def main():
    png(os.path.join(OUT, "textures/item/cemetery/crypt_key.png"), grid(KEY, {".": T, "o": (24, 22, 26, 255), "B": (74, 70, 78, 255), "b": (20, 18, 22, 255)}))
    png(os.path.join(OUT, "textures/item/cemetery/seal.png"), grid(SEAL, {".": T, "o": (30, 22, 20, 255), "R": (92, 32, 30, 255), "g": (196, 170, 110, 255)}))
    for n in ("crypt_key", "seal"):
        p = os.path.join(OUT, "models/item/cemetery/%s.json" % n); os.makedirs(os.path.dirname(p), exist_ok=True)
        json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": "last_ember:item/cemetery/%s" % n}}, open(p, "w"))
        p = os.path.join(OUT, "items/cemetery/%s.json" % n); os.makedirs(os.path.dirname(p), exist_ok=True)
        json.dump({"model": {"type": "minecraft:model", "model": "last_ember:item/cemetery/%s" % n}}, open(p, "w"))
main()
