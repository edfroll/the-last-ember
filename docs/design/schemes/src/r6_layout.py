#!/usr/bin/env python3
"""Схема Р6: план Незера (ограниченная область) и план Пепельных Земель. Архитектор. Только для глаз.
Пишет docs/design/schemes/r6_nether_plan.png и r6_surface_plan.png. Запуск: python3 r6_layout.py (Pillow)."""
import os
from PIL import Image, ImageDraw, ImageFont
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font, small = ImageFont.truetype(F, 14), ImageFont.truetype(F, 11)

def plan(fname, x0, x1, z0, z1, scale, grid, areas, points, path, title, alt=None):
    W = int((x1 - x0) * scale); H = int((z1 - z0) * scale)
    img = Image.new("RGB", (W, H + 34), (26, 20, 20)); d = ImageDraw.Draw(img)
    P = lambda x, z: ((x - x0) * scale, (z - z0) * scale)
    for gx in range((x0 // grid) * grid, x1 + 1, grid):
        if gx < x0: continue
        d.line([P(gx, z0), P(gx, z1)], fill=(60, 50, 50)); d.text((P(gx, z0)[0] + 2, 2), f"x {gx}", fill=(160, 150, 150), font=small)
    for gz in range((z0 // grid) * grid, z1 + 1, grid):
        if gz < z0: continue
        d.line([P(x0, gz), P(x1, gz)], fill=(60, 50, 50)); d.text((2, P(x0, gz)[1] + 2), f"z {gz}", fill=(160, 150, 150), font=small)
    for name, kind, a, c in areas:
        if kind == "rect":
            ax1, ax2, az1, az2 = a; d.rectangle([P(ax1, az1), P(ax2, az2)], fill=c, outline=(230, 220, 220)); tx, tz = P(ax1, az1)
        else:
            cx, cz, r = a; d.ellipse([P(cx - r, cz - r), P(cx + r, cz + r)], fill=c, outline=(230, 220, 220)); tx, tz = P(cx - r, cz - r)
        d.text((tx + 4, tz + 4), name, fill=(255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
    if path:
        d.line([P(*p) for p in path], fill=(255, 255, 255), width=3)
    if alt:  # необязательная петля — пунктир
        pts = [P(*p) for p in alt]
        for (ax, az), (bx, bz) in zip(pts, pts[1:]):
            n = max(1, int(((bx - ax) ** 2 + (bz - az) ** 2) ** 0.5 // 8))
            for i in range(0, n, 2):
                d.line([(ax + (bx - ax) * i / n, az + (bz - az) * i / n), (ax + (bx - ax) * (i + 1) / n, az + (bz - az) * (i + 1) / n)], fill=(190, 190, 190), width=2)
    for name, x, z, c in points:
        px, pz = P(x, z); d.ellipse([px - 5, pz - 5, px + 5, pz + 5], fill=c, outline=(0, 0, 0))
        tw = d.textlength(name, font=small); tx = px + 8 if px + 8 + tw < W - 4 else px - 8 - tw
        d.text((tx, pz - 8), name, fill=(255, 255, 255), font=small, stroke_width=2, stroke_fill=(0, 0, 0))
    d.text((8, H + 9), title, fill=(230, 230, 230), font=font)
    img.save(os.path.join(OUT, fname))

plan("r6_nether_plan.png", -240, 440, -280, 280, 1.4, 100,
     [("Незер: граница области", "rect", (-220, 420, -260, 260), (60, 30, 25)),
      ("Лавовое море", "rect", (-120, 300, -40, 60), (150, 60, 20)),
      ("Огненная Крепость", "rect", (-50, 150, -200, -80), (90, 30, 30)),
      ("Бастион Свиных Королей", "rect", (140, 220, 100, 180), (70, 60, 60)),
      ("Пепельный Котёл", "circle", (250, 10, 30), (40, 40, 45)),
      ("Наковальня Трёх Глав", "circle", (340, -90, 30), (50, 20, 50))],
     [("Входной портал (из Рамки Предков)", -180, 0, (180, 255, 200)), ("Выходной портал → Пепельные Земли", 370, 40, (255, 160, 60)),
      ("Багровый лес", -150, -180, (200, 60, 60)), ("Искажённый лес", -150, 180, (60, 180, 170)), ("Долина душ", 60, 200, (140, 120, 100))],
     [(-180, 0), (-120, 10), (0, 10), (50, -80), (100, 10), (180, 100), (220, 40), (250, 10), (300, 20), (370, 40), (340, -90)],
     "Незер (своё измерение, координаты Незера). Белая линия — основной путь. Север — вверх.")

plan("r6_surface_plan.png", 640, 1520, -880, 680, 0.6, 200,
     [("Р6 · Пепельные Земли", "rect", (665, 1500, -870, 650), (55, 45, 40)),
      ("Мёртвые Топи", "rect", (800, 1100, 250, 450), (40, 50, 40)),
      ("Город Мертвенного Света", "rect", (900, 1100, -400, -200), (30, 60, 45)),
      ("Пепельная гора", "circle", (1280, -620, 200), (90, 40, 30))],
     [("Пепельные Врата: выход из Незера, главный костёр", 760, 0, (255, 160, 60)),
      ("Врата в Край — вершина вулкана", 1280, -620, (180, 140, 255)),
      ("Обугленный хребет (граница с Р1)", 665, 300, (200, 200, 200))],
     [(760, 0), (880, -120), (1000, -300), (1150, -480), (1280, -620)],
     "Пепельные Земли: x +665…+1500, z −870…+650. Белая — основной путь, пунктир — Топи (необязательно). Север — вверх.",
     alt=[(760, 0), (900, 150), (950, 350), (1000, 100), (1000, -300)])
print("ok")
