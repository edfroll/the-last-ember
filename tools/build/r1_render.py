#!/usr/bin/env python3
"""T-022: top view of a scan (tools/terrain.sh scan) with hill shading: python3 tools/build/r1_render.py scan.bin out.png [x1 z1 x2 z2] [scale]"""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, NONE
from PIL import Image
s = Scan(sys.argv[1]); a = list(map(int, sys.argv[3:7])) if len(sys.argv) > 6 else [-760, -940, 760, 700]
sc = float(sys.argv[7]) if len(sys.argv) > 7 else 1
x1, z1, x2, z2 = a; sl = (slice(z1 - s.z0, z2 - s.z0), slice(x1 - s.x0, x2 - s.x0))
top = s.top[sl].astype(float); g = s.ground[sl].astype(float); miss = (s.flags[sl] & 16) > 0; top[miss] = 0
wat = (s.water[sl] != NONE) & (s.water[sl] >= s.top[sl]); tree = ((s.flags[sl] & 3) > 0) & (s.top[sl] > s.ground[sl] + 1)
gy, gx = np.gradient(top); shade = np.clip(0.75 + (gx * -0.7 + gy * -0.7) / 4, 0.35, 1.25)
pal = np.array([[72, 110, 60], [104, 132, 70], [150, 150, 92], [150, 128, 96], [130, 112, 100], [140, 140, 140], [236, 236, 240]], float)
lv = np.clip((g - 60) / 25, 0, 5.99); i = lv.astype(int); f = (lv - i)[..., None]
rgb = pal[i] * (1 - f) + pal[np.minimum(i + 1, 6)] * f
rgb[tree] = rgb[tree] * 0.7 + np.array([30, 60, 30]) * 0.3
rgb = rgb * shade[..., None]; rgb[wat] = [55, 85, 160]; rgb[miss] = [0, 0, 0]
im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
if sc != 1: im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
im.save(sys.argv[2]); print("saved", sys.argv[2], im.size)
