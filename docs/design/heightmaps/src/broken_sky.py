#!/usr/bin/env python3
"""Карта высот Бездны «Разбитое Небо» (Р4). Архитектор.

Пишет в docs/design/heightmaps/:
  broken_sky_height.png    — 8 бит, 1 пиксель = 1 блок, y = значение − 64 (0 → y −64, 255 → y 191)
  broken_sky_preview.png   — цветная схема для глаз, скрипт её не читает
  broken_sky_profiles.csv  — профили с севера на юг на 9 долготах, шаг 10

Запуск: python3 broken_sky.py (numpy, Pillow). Детерминирован (seed 4100).
"""
import os, csv, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
X0, Z0, W, H = -700, 900, 1400, 600            # x −700…+699, z +900…+1499
Y_OFF = -64
CZ = 1200                                       # ось каньона
rng = np.random.default_rng(4100)

def value_noise(shape, cell):
    gh, gw = shape[0] // cell + 2, shape[1] // cell + 2
    g = rng.random((gh, gw))
    ys = np.arange(shape[0]) / cell; xs = np.arange(shape[1]) / cell
    y0 = ys.astype(int); x0 = xs.astype(int)
    fy = ys - y0; fx = xs - x0
    fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
    a = g[y0][:, x0]; b = g[y0][:, x0 + 1]; c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
    top = a + (b - a) * fx[None, :]; bot = c + (d - c) * fx[None, :]
    return top + (bot - top) * fy[:, None]
def fbm(shape, cells=(128, 64, 32, 16), amps=(1, .5, .25, .125)):
    return sum(a * value_noise(shape, c) for c, a in zip(cells, amps)) / sum(amps) * 2 - 1

zz, xx = np.mgrid[0:H, 0:W]
wx = xx + X0; wz = zz + Z0
n1 = fbm((H, W)); n2 = fbm((H, W), (24, 12, 6), (1, .5, .25)); n3 = fbm((H, W), (300, 150), (1, .5))

# плато пустыни: y 88–100, к краям каньона чуть выше (выветренные столовые края)
h = 92 + 6 * n1

# каньон: полуширина меняется вдоль оси (120…180), ось извивается
axis = CZ + 40 * np.sin(wx / 230.0) + 20 * n3
half = 150 + 30 * np.sin(wx / 170.0 + 1.3) + 15 * n3
# каньон сходит на нет к краям охвата по x (за ±600 — переход в разломы помельче)
fade = np.clip((620 - np.abs(wx)) / 120, 0, 1)
half = half * np.sqrt(fade) * (0.85 + 0.15 * n1)
d = np.abs(wz - axis)                           # расстояние от оси
inside = d < half
# профиль: ступени-террасы у края (3 уступа по 20–30), потом отвес в «без дна»
t = np.clip(d / np.maximum(half, 1), 0, 1)       # 0 на оси, 1 на краю
floor = -60 + 4 * n2
terr = np.where(t > 0.95, 92 + 6 * n1,
       np.where(t > 0.88, 70 + 4 * n2,
       np.where(t > 0.81, 46 + 4 * n2,
       np.where(t > 0.74, 20 + 4 * n2, floor))))
h = np.where(inside, terr, h)

# опоры-столпы: скальные пальцы из бездны, на них держатся цепи и мосты к Городу
PILLARS = [(-420, 1150, 14, 70), (-250, 1250, 18, 96), (-80, 1130, 12, 60), (60, 1270, 20, 110),
           (210, 1160, 14, 84), (380, 1240, 16, 76), (-330, 1210, 10, 40), (150, 1110, 10, 50)]
for px, pz, r, top in PILLARS:
    dp = np.hypot(wx - px, wz - pz)
    col = top - np.clip(dp - r * 0.6, 0, None) * 6 + 3 * n2
    h = np.where(inside & (dp < r), np.maximum(h, col), h)

# ворота в каньон: спуск-рампа с северного края к первому уступу у (0, axis−half)
ramp_x = (np.abs(wx) < 6)
north_edge = (wz < axis) & (t > 0.74) & inside
h = np.where(ramp_x & north_edge, np.maximum(h, 20 + (t - 0.74) / 0.26 * 72), h)

h = np.clip(np.round(h), -64, 191)
Image.fromarray((h - Y_OFF).astype(np.uint8), "L").save(os.path.join(OUT, "broken_sky_height.png"))

with open(os.path.join(OUT, "broken_sky_profiles.csv"), "w", newline="") as f:
    wr = csv.writer(f); zs = list(range(900, 1500, 10))
    wr.writerow(["x"] + [f"z={z}" for z in zs])
    for x in [-600, -420, -250, -80, 0, 60, 210, 380, 600]:
        wr.writerow([x] + [int(h[z - Z0, x - X0]) for z in zs])

# --- схема ---
def col(y):
    stops = [(-64, (25, 20, 35)), (-20, (60, 50, 75)), (20, (120, 80, 70)), (60, (175, 110, 80)), (92, (210, 160, 110)), (110, (230, 200, 150)), (191, (255, 240, 210))]
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if y <= b:
            tt = (y - a) / (b - a); return tuple(int(ca[i] + (cb[i] - ca[i]) * tt) for i in range(3))
    return stops[-1][1]
lut = np.array([col(y) for y in range(-64, 192)], np.uint8)
rgb = lut[(h + 64).astype(int)]
gz, gx = np.gradient(h)
shade = np.clip(1 - (gx * .7 + gz * .7) / 14, .45, 1.3)
rgb = np.clip(rgb * shade[..., None], 0, 255).astype(np.uint8)
lvl = ((h + 64) // 20).astype(int); cont = np.zeros(h.shape, bool)
cont[:-1] |= lvl[:-1] != lvl[1:]; cont[:, :-1] |= lvl[:, :-1] != lvl[:, 1:]
rgb[cont] = (rgb[cont] * .6).astype(np.uint8)
img = Image.fromarray(rgb)
dr = ImageDraw.Draw(img)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
def P(x, z): return (x - X0, z - Z0)
def lab(x, z, t, c=(255, 230, 80), dx=7):
    px, pz = P(x, z); dr.ellipse([px - 4, pz - 4, px + 4, pz + 4], fill=c, outline=(0, 0, 0))
    dr.text((px + dx, pz - 8), t, fill=(255, 255, 255), font=font, stroke_width=3, stroke_fill=(0, 0, 0))
for gxw in range(-700, 700, 100):
    dr.line([P(gxw, Z0), P(gxw, Z0 + H)], fill=(255, 255, 255), width=1)
    dr.text((P(gxw, Z0)[0] + 2, 2), f"x {gxw}", fill=(255, 255, 255), font=small, stroke_width=2, stroke_fill=(0, 0, 0))
for gzw in range(1000, 1500, 100):
    dr.line([P(X0, gzw), P(X0 + W, gzw)], fill=(255, 255, 255), width=1)
    dr.text((2, P(X0, gzw)[1] + 2), f"z +{gzw}", fill=(255, 255, 255), font=small, stroke_width=2, stroke_fill=(0, 0, 0))
for i, (px, pz, r, top) in enumerate(PILLARS, 1):
    lab(px, pz, f"С{i} y {top}", (255, 160, 60))
lab(0, 1040, "Ворота каньона: рампа на первый уступ", (120, 220, 255))
lab(0, 1200, "Город Богов — над осью, на парящих скалах до y 300", (255, 255, 255), -200)
dr.text((10, H - 22), "Север — вверх. Без дна: y −60 в тумане. Террасы по краю: 70 / 46 / 20.", fill=(255, 255, 255), font=small, stroke_width=2, stroke_fill=(0, 0, 0))
img.save(os.path.join(OUT, "broken_sky_preview.png"))
print("min/max", int(h.min()), int(h.max()))
