#!/usr/bin/env python3
"""Схема Глубин (Р5): план уровней и разрез. Архитектор. Только для глаз, скрипт стройки её не читает.
Пишет docs/design/schemes/depths_plan.png и depths_section.png. Запуск: python3 depths_layout.py (Pillow)."""
import os
from PIL import Image, ImageDraw, ImageFont
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font, small, big = ImageFont.truetype(F, 14), ImageFont.truetype(F, 11), ImageFont.truetype(F, 16)

# уровни: имя, x1, x2, z1, z2, y верх, y низ, цвет
LEVELS = [
    ("1 · Шахты Предков", -60, 300, -320, 60, 20, -6, (176, 120, 70)),
    ("2 · Чертоги", 120, 380, 40, 340, -18, -40, (150, 90, 90)),
    ("Пропасть и Мост", 80, 160, 180, 340, -20, -64, (40, 30, 40)),
    ("3 · Звёздная Река", -360, 80, 120, 380, -25, -55, (40, 70, 140)),
    ("4 · Безмолвный Город", -380, -140, -260, 60, -30, -64, (20, 60, 70)),
]
POINTS = [
    ("Колодец: спуск, костёр y 20", 40, -44, (255, 230, 80)),
    ("Великая Лестница (−6 → −18)", 260, 40, (255, 160, 60)),
    ("Мост 80 над Пропастью, y −22", 120, 260, (255, 90, 90)),
    ("Пристань: главный костёр Р5?", 50, 250, (120, 220, 255)),
    ("Устье Реки → ворота Города", -340, 200, (120, 220, 255)),
    ("Рамка Предков (Алтарь V)", -260, -100, (180, 255, 200)),
    ("Изгнанник (запечатанный зал)", 220, -260, (255, 230, 80)),
    ("Зал Пробуждения (Р0), y 55–87", 0, 24, (220, 220, 220)),
    ("Шахты Железных Руд (Р1), низ y 34", 280, -60, (220, 220, 220)),
]
S = 1  # 1 пиксель = 1 блок
W = H = 800
img = Image.new("RGB", (W, H + 40), (24, 22, 28)); d = ImageDraw.Draw(img)
def P(x, z): return (x + 400, z + 400)
for gx in range(-400, 401, 100):
    d.line([P(gx, -400), P(gx, 400)], fill=(60, 58, 66)); d.text((P(gx, -400)[0] + 2, 2), f"x {gx}", fill=(150, 150, 160), font=small)
for gz in range(-400, 401, 100):
    d.line([P(-400, gz), P(400, gz)], fill=(60, 58, 66)); d.text((2, P(-400, gz)[1] + 2), f"z {gz}", fill=(150, 150, 160), font=small)
for name, x1, x2, z1, z2, yt, yb, c in LEVELS:
    d.rectangle([P(x1, z1), P(x2, z2)], fill=c, outline=(230, 230, 230))
    d.text((P(x1, z1)[0] + 4, P(x1, z1)[1] + 4), f"{name}\ny {yt} … {yb}", fill=(255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
path = [(40, -44), (150, -150), (230, -40), (260, 40), (300, 150), (220, 260), (160, 260), (80, 260), (50, 250), (-150, 230), (-340, 200), (-330, 60), (-260, -100)]
d.line([P(*p) for p in path], fill=(255, 255, 255), width=3)
for name, x, z, c in POINTS:
    px, pz = P(x, z); d.ellipse([px - 5, pz - 5, px + 5, pz + 5], fill=c, outline=(0, 0, 0))
    tw = d.textlength(name, font=small)
    tx = px + 8 if px + 8 + tw < W - 4 else px - 8 - tw
    d.text((tx, pz - 8), name, fill=(255, 255, 255), font=small, stroke_width=2, stroke_fill=(0, 0, 0))
d.text((8, H + 10), "План Глубин: x −400…+400, z −400…+400. Белая линия — основной путь вниз. Север — вверх.", fill=(230, 230, 230), font=font)
img.save(os.path.join(OUT, "depths_plan.png"))

# разрез вдоль пути: условная горизонталь — пройденный путь, вертикаль — y
SEC = [("Колодец", 0, 20), ("Шахты", 220, 8), ("Великая Лестница", 330, -18), ("Чертоги", 470, -30), ("Мост", 560, -22),
       ("Пристань", 600, -47), ("Река", 850, -48), ("Устье", 1000, -50), ("Город", 1180, -55), ("Рамка", 1300, -58)]
W2, H2 = 1400, 380
img2 = Image.new("RGB", (W2, H2), (24, 22, 28)); d2 = ImageDraw.Draw(img2)
def Q(s, y): return (50 + s, 30 + (110 - y) * 2)   # y 110 вверху, −64 внизу
for y in range(-60, 111, 20):
    d2.line([Q(0, y), Q(1320, y)], fill=(60, 58, 66)); d2.text((4, Q(0, y)[1] - 7), f"y {y}", fill=(150, 150, 160), font=small)
d2.rectangle([Q(0, 103), Q(60, 98)], fill=(200, 170, 120)); d2.text(Q(65, 112), "Площадь Приюта y 103", fill=(220, 220, 220), font=small)
d2.line([Q(0, 103), Q(0, 20)], fill=(255, 230, 80), width=4); d2.text(Q(8, 70), "провал колодца, 83", fill=(255, 230, 80), font=small)
d2.line([Q(0, 20), Q(1320, 20)], fill=(120, 120, 130), width=1); d2.text(Q(1100, 26), "граница Глубин y 20", fill=(160, 160, 170), font=small)
pts = [Q(s, y) for _, s, y in SEC]
d2.line(pts, fill=(255, 255, 255), width=3)
for name, s, y in SEC:
    x, yy = Q(s, y); d2.ellipse([x - 4, yy - 4, x + 4, yy + 4], fill=(255, 160, 60)); d2.text((x - 20, yy + 8), f"{name}\ny {y}", fill=(255, 255, 255), font=small)
d2.text((8, H2 - 24), "Разрез вдоль основного пути (условно, по горизонтали — пройденные блоки).", fill=(230, 230, 230), font=font)
img2.save(os.path.join(OUT, "depths_section.png"))
