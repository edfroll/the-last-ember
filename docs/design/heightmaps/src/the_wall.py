#!/usr/bin/env python3
"""Карта высот Стены (Р3). Архитектор.

Пишет в docs/design/heightmaps/:
  the_wall_height.png    — 8 бит оттенки серого, 1 пиксель = 1 блок, y = значение + 40
  the_wall_material.png  — маска: 0 рельеф, 100 тело Стены (лёд и кладка), 200 площадка Чёрного Поста
  the_wall_preview.png   — цветная схема для глаз (по z растянута вдвое), скрипт её не читает
  the_wall_profiles.csv  — поперечные профили с юга на север на 9 долготах, шаг 10

Запуск: python3 the_wall.py (numpy, Pillow). Детерминирован (seed 3850).
"""
import os, csv
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
X0, Z0, W, H = -1000, -1000, 1400, 320        # x −1000…+399, z −1000…−681
Y_OFFSET = 40
WALL_X1, WALL_X2 = -650, 100                  # тело Стены по x
WALL_Z = -850                                 # южная грань
WALL_T = 40                                   # толщина: z −889…−850
WALL_TOP = 215
GATE_X = -560                                 # Врата через Стену
POST = (-560, -815)                           # центр Чёрного Поста

rng = np.random.default_rng(3850)

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

def fbm(shape, cells=(96, 48, 24, 12), amps=(1, .5, .25, .125)):
    return sum(a * value_noise(shape, c) for c, a in zip(cells, amps)) / sum(amps) * 2 - 1

zz, xx = np.mgrid[0:H, 0:W]
wx = xx + X0; wz = zz + Z0
n1 = fbm((H, W)); n2 = fbm((H, W), (10, 5, 3), (1, .6, .3)); n3 = fbm((H, W), (40, 20), (1, .5))

# основа: юг (край Дола) y ~76, север (Белая Тишь) чуть выше
h = 76 + 4 * n1 + np.clip((-wz - 860) / 140, 0, 1) * 4

# Стена закрывает единственный проход в сплошном хребте, который тянется с запада на восток
# через весь мир (за пределы этой карты — до краёв играбельной зоны). Обойти Стену нельзя.
# Ось хребта — z −870, полуширина ~55. Южное подножие не заходит дальше z −790:
# южнее проходит дорога от Северных Врат Дозора (Р2) к Чёрному Посту.
def ridge(peak):
    across = np.exp(-((wz + 870) / 42) ** 2)
    outside = np.clip(np.maximum(WALL_X1 - wx, wx - WALL_X2) / 25, 0, 1)   # 0 у конца Стены → 1 через 25 блоков
    crest = peak + 14 * n1 + 8 * n3
    return 76 + (crest - 76) * across * np.maximum(outside, 0.85)

side = (wx < WALL_X1) | (wx > WALL_X2)
mount = np.where(side, np.where(wx < WALL_X1, ridge(250), ridge(240)), 0)
h = np.where(side, np.maximum(h, mount + 5 * n2 * (mount > 100)), h)
# стык со Стеной: хребет не ниже гребня Стены на 30 блоков от её концов
join = (((wx < WALL_X1) & (wx > WALL_X1 - 30)) | ((wx > WALL_X2) & (wx < WALL_X2 + 30)))
join &= (wz <= WALL_Z + 10) & (wz > WALL_Z - WALL_T - 10)
h = np.where(join, np.maximum(h, WALL_TOP + 5), h)

# тело Стены: гребень y 215, по краям парапеты +3
in_wall = (wx >= WALL_X1) & (wx <= WALL_X2) & (wz <= WALL_Z) & (wz > WALL_Z - WALL_T)
parapet = (wz > WALL_Z - 3) | (wz <= WALL_Z - WALL_T + 3)
h = np.where(in_wall, WALL_TOP + np.where(parapet, 3, 0), h)
# осыпь ледяных глыб у подножия, 10 блоков с каждой стороны
near_s = (wx >= WALL_X1) & (wx <= WALL_X2) & (wz > WALL_Z) & (wz <= WALL_Z + 10)
near_n = (wx >= WALL_X1) & (wx <= WALL_X2) & (wz <= WALL_Z - WALL_T) & (wz > WALL_Z - WALL_T - 10)
h = np.where(near_s, np.maximum(h, 76 + 8 * (1 - (wz - WALL_Z) / 10)), h)
h = np.where(near_n, np.maximum(h, 78 + 8 * (1 - ((WALL_Z - WALL_T) - wz) / 10)), h)

# площадка Чёрного Поста: 120×70 на y 78, у южного подножия
px, pz = POST
post = (np.abs(wx - px) <= 60) & (wz > WALL_Z) & (wz <= WALL_Z + 70)
h = np.where(post, 78, h)

h = np.clip(np.round(h), 41, 295)
mat = np.zeros(h.shape, np.uint8); mat[in_wall] = 100; mat[post] = 200

Image.fromarray((h - Y_OFFSET).astype(np.uint8), "L").save(os.path.join(OUT, "the_wall_height.png"))
Image.fromarray(mat, "L").save(os.path.join(OUT, "the_wall_material.png"))

with open(os.path.join(OUT, "the_wall_profiles.csv"), "w", newline="") as f:
    wr = csv.writer(f)
    zs = list(range(-690, -1001, -10))
    wr.writerow(["x"] + [f"z={z}" for z in zs])
    for x in [-900, -700, -660, -560, -300, 0, 90, 140, 300]:
        wr.writerow([x] + [int(h[z - Z0, x - X0]) for z in zs])

# --- схема ---
def col(y):
    stops = [(41, (90, 110, 90)), (76, (140, 155, 140)), (100, (175, 180, 175)), (160, (200, 205, 212)), (215, (232, 236, 242)), (295, (255, 255, 255))]
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if y <= b:
            t = (y - a) / (b - a); return tuple(int(ca[i] + (cb[i] - ca[i]) * t) for i in range(3))
    return stops[-1][1]
lut = np.array([col(y) for y in range(300)], np.uint8)
rgb = lut[h.astype(int)]
gz, gx = np.gradient(h)
shade = np.clip(1 - (gx * .8 + gz * .8) / 12, .5, 1.3)
rgb = np.clip(rgb * shade[..., None], 0, 255).astype(np.uint8)
lvl = (h // 20).astype(int); cont = np.zeros(h.shape, bool)
cont[:-1] |= lvl[:-1] != lvl[1:]; cont[:, :-1] |= lvl[:, :-1] != lvl[:, 1:]
rgb[cont] = (rgb[cont] * .6).astype(np.uint8)
rgb[in_wall] = (120, 185, 215)
rgb[post] = (70, 70, 80)
img = Image.fromarray(rgb).resize((W, H * 2), Image.NEAREST)
d = ImageDraw.Draw(img)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
def P(x, z): return (x - X0, (z - Z0) * 2)
def lab(x, z, t, c=(255, 230, 80), dx=7):
    px, pz = P(x, z); d.ellipse([px - 4, pz - 4, px + 4, pz + 4], fill=c, outline=(0, 0, 0))
    d.text((px + dx, pz - 8), t, fill=(255, 255, 255), font=font, stroke_width=3, stroke_fill=(0, 0, 0))
for gxw in range(-1000, 400, 100):
    d.line([P(gxw, Z0), P(gxw, Z0 + H)], fill=(255, 255, 255), width=1)
    d.text((P(gxw, Z0)[0] + 2, 2), f"x {gxw}", fill=(255, 255, 255), font=small, stroke_width=2, stroke_fill=(0, 0, 0))
for gzw in range(-950, -680, 50):
    d.line([P(X0, gzw), P(X0 + W, gzw)], fill=(255, 255, 255), width=1)
    d.text((2, P(X0, gzw)[1] + 2), f"z {gzw}", fill=(255, 255, 255), font=small, stroke_width=2, stroke_fill=(0, 0, 0))
d.text(P(-420, -884), "СТЕНА · лёд и кладка · гребень y 215 · толщина 40", fill=(10, 30, 50), font=font)
lab(GATE_X, -870, "Врата через Стену", (255, 120, 80))
lab(-500, -790, "Чёрный Пост (площадка y 78)", (200, 200, 200))
lab(-880, -905, "Западный хребет y 235–270", (255, 255, 255))
lab(170, -905, "Восточный хребет y 225–260", (255, 255, 255))
d.line([P(-1000, -705), P(-880, -712), P(-760, -722), P(-640, -740), P(-580, -780)], fill=(120, 220, 255), width=3)
lab(-990, -705, "дорога от Северных Врат Дозора (Р2, −880, −640)", (120, 220, 255))
lab(40, -686, "Сгоревшая Дозорная (Р1): 170 до Стены", (255, 160, 60), -330)
d.text((10, H * 2 - 22), "Север — вверх. По z схема растянута вдвое.", fill=(255, 255, 255), font=small, stroke_width=2, stroke_fill=(0, 0, 0))
img.save(os.path.join(OUT, "the_wall_preview.png"))

print("min/max", int(h.min()), int(h.max()))
for n, (x, z) in {"Стена": (-300, -870), "Пост": POST, "хребет З": (-850, -870), "хребет В": (250, -870), "хребет З, z −790": (-850, -790),
                  "дорога (−760,−722)": (-760, -722), "юг": (-300, -760), "север": (-300, -960)}.items():
    print(n, int(h[z - Z0, x - X0]))
