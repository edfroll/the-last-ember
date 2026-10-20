#!/usr/bin/env python3
"""Карта высот Кольцевой горы (Р2). Архитектор.

Пишет рядом с собой (в docs/design/heightmaps/):
  ring_mountain_height.png   — 8-бит оттенки серого, 1 пиксель = 1 блок, y = значение + 40
  ring_mountain_preview.png  — цветная схема с горизонталями и подписями (для глаз, не для скрипта)
  ring_mountain_profiles.csv — профили высот по 8 направлениям от центра, шаг 5 блоков

Запуск: python3 ring_mountain.py   (numpy, Pillow). Результат детерминирован (seed 2042).
"""
import math, os, csv
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
X0, Z0, SIZE = -1200, -360, 560          # охват: x −1200…−641, z −360…+199
CX, CZ = -920, -80                        # центр кольца
Y_OFFSET = 40                             # y = gray + 40

# --- ключевые точки (мировые координаты) ---
LAKE = (-915, -100, 40)                   # центр и радиус Исцеляющего озера
LAKE_WATER_Y = 76
PASS_BEARING = 90                         # перевал на восток, к Западному перевалу Р1
PASS_SADDLE_Y = 128

rng = np.random.default_rng(2042)

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

def fbm(shape, cells=(64, 32, 16, 8), amps=(1, .5, .25, .125)):
    n = sum(a * value_noise(shape, c) for c, a in zip(cells, amps))
    return n / sum(amps) * 2 - 1      # −1…1

def bearing_deg(dx, dz):
    """Компас: 0 = север (−z), 90 = восток (+x), 180 = юг (+z), 270 = запад."""
    return (np.degrees(np.arctan2(dx, -dz)) + 360) % 360

def ang_dist(a, b):
    d = np.abs(a - b) % 360
    return np.minimum(d, 360 - d)

zz, xx = np.mgrid[0:SIZE, 0:SIZE]
wx = xx + X0; wz = zz + Z0
dx = wx - CX; dz = wz - CZ
r = np.hypot(dx, dz)
b = bearing_deg(dx, dz)

n_big = fbm((SIZE, SIZE)); n_small = fbm((SIZE, SIZE), cells=(12, 6, 3), amps=(1, .6, .3))

# гребень: радиус и высота по направлению
crest_r = 150 + 8 * n_big
crest_h = 190 + 22 * n_big
for bear, top, width in [(315, 250, 22), (40, 226, 18), (230, 214, 16), (170, 204, 14)]:
    crest_h = crest_h + (top - 190) * np.exp(-(ang_dist(b, bear) / width) ** 2)
# перевал: седловина на востоке
notch = np.exp(-(ang_dist(b, PASS_BEARING) / 7) ** 2)
crest_h = crest_h * (1 - notch) + PASS_SADDLE_Y * notch

base = 72 + 4 * n_big                       # окрестная местность
rim_r = 105                                 # край долины
foot_r = 222                                # внешнее подножие

h = np.array(base, dtype=float)
# внешний склон: подножие → гребень, вогнутый профиль (круче к вершине)
t = np.clip((foot_r - r) / (foot_r - crest_r), 0, 1)
outer = base + (crest_h - base) * t ** 1.6
h = np.where((r >= crest_r) & (r < foot_r), outer, h)
# внутренняя стена: гребень → край долины, обрыв (круче внизу у долины не делаем: стена отвесная сверху)
valley_rim_y = 84
t2 = np.clip((r - rim_r) / (crest_r - rim_r), 0, 1)
inner_steep = valley_rim_y + (crest_h - valley_rim_y) * t2 ** 0.55
inner_pass = valley_rim_y + (crest_h - valley_rim_y) * t2 ** 1.3   # у перевала склон пологий
inner = inner_steep * (1 - notch) + inner_pass * notch
h = np.where((r >= rim_r) & (r < crest_r), inner, h)
# дно долины: чаша 84 у края → 79 к озеру
lx, lz, lr = LAKE
dl = np.hypot(wx - lx, wz - lz)
floor = 79 + 5 * np.clip(r / rim_r, 0, 1) ** 2
h = np.where(r < rim_r, floor, h)
# озеро: дно 66 в центре, берег на уровне воды 76
lake_bottom = 66 + 10 * np.clip(dl / lr, 0, 1) ** 2
h = np.where(dl < lr, np.minimum(h, lake_bottom), h)
shore = (dl >= lr) & (dl < lr + 8)
h = np.where(shore, np.minimum(h, 77 + (dl - lr) / 8 * 2), h)
# шероховатость скал: сильнее на склонах, слабее в долине
rough = np.where(r < rim_r, 0.6, np.where(r < foot_r, 5.0, 1.5))
h = h + n_small * rough
# уступ Чаши Двух Вод: площадка y 108 во внутренней стене, вырублена в скале
CHX, CHZ = -958, -185
dch = np.hypot(wx - CHX, wz - CHZ)
h = np.where((dch < 10) & (r > rim_r - 2), np.minimum(h, 108), h)
h = np.clip(np.round(h), 41, 250)

gray = (h - Y_OFFSET).astype(np.uint8)
Image.fromarray(gray, mode="L").save(os.path.join(OUT, "ring_mountain_height.png"))

# --- профили ---
with open(os.path.join(OUT, "ring_mountain_profiles.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["направление", "азимут"] + [f"r={d}" for d in range(0, 241, 5)])
    for name, bear in [("С", 0), ("СВ", 45), ("В (перевал)", 90), ("ЮВ", 135), ("Ю", 180), ("ЮЗ", 225), ("З", 270), ("СЗ (пик)", 315)]:
        row = []
        for d in range(0, 241, 5):
            px = int(round(CX + d * math.sin(math.radians(bear)) - X0))
            pz = int(round(CZ - d * math.cos(math.radians(bear)) - Z0))
            row.append(int(h[pz, px]) if 0 <= px < SIZE and 0 <= pz < SIZE else "")
        w.writerow([name, bear] + row)

# --- цветная схема ---
def hyps(y):
    stops = [(41, (70, 100, 60)), (76, (88, 118, 66)), (80, (96, 128, 72)), (110, (120, 130, 80)),
             (150, (130, 115, 90)), (190, (150, 140, 130)), (220, (200, 200, 200)), (250, (245, 245, 250))]
    for (y0, c0), (y1, c1) in zip(stops, stops[1:]):
        if y <= y1:
            t = (y - y0) / (y1 - y0)
            return tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3))
    return stops[-1][1]
lut = np.array([hyps(y) for y in range(256)], dtype=np.uint8)
rgb = lut[h.astype(int)]
water = (dl < lr)
rgb[water] = (60, 150, 160)
# отмывка
gz, gx = np.gradient(h)
shade = np.clip(1 - (gx * 0.8 + gz * 0.8) / 12, 0.55, 1.25)
rgb = np.clip(rgb * shade[..., None], 0, 255).astype(np.uint8)
# горизонтали через 20
cont = np.zeros_like(h, dtype=bool)
lvl = (h // 20).astype(int)
cont[:-1] |= lvl[:-1] != lvl[1:]; cont[:, :-1] |= lvl[:, :-1] != lvl[:, 1:]
rgb[cont] = (rgb[cont] * 0.55).astype(np.uint8)
SC = 2
img = Image.fromarray(rgb).resize((SIZE * SC, SIZE * SC), Image.NEAREST)
d = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
except OSError:
    font = small = ImageFont.load_default()
def P(x, z): return ((x - X0) * SC, (z - Z0) * SC)
def mark(x, z, text, col=(255, 230, 80), dx_=8, dy_=-8):
    px, pz = P(x, z)
    d.ellipse([px - 5, pz - 5, px + 5, pz + 5], fill=col, outline=(0, 0, 0))
    d.text((px + dx_, pz + dy_), text, fill=(255, 255, 255), font=font, stroke_width=3, stroke_fill=(0, 0, 0))
# сетка 100
for gxw in range(-1200, -639, 100):
    d.line([P(gxw, Z0), P(gxw, Z0 + SIZE)], fill=(255, 255, 255, 60), width=1)
    d.text((P(gxw, Z0)[0] + 3, 3), f"x {gxw}", fill=(255, 255, 255), font=small, stroke_width=2, stroke_fill=(0, 0, 0))
for gzw in range(-300, 200, 100):
    d.line([P(X0, gzw), P(X0 + SIZE, gzw)], fill=(255, 255, 255, 60), width=1)
    d.text((3, P(X0, gzw)[1] + 3), f"z {gzw}", fill=(255, 255, 255), font=small, stroke_width=2, stroke_fill=(0, 0, 0))
# Чёрное озеро (пещера под гребнем)
bx, bz = -920, -230
d.rectangle([P(bx - 40, bz - 40), P(bx + 40, bz + 40)], outline=(20, 20, 20), width=3)
d.text((P(bx - 38, bz - 38)[0], P(bx - 38, bz - 38)[1]), "Чёрное озеро\n(пещера, y 40–75)", fill=(255, 255, 255), font=small, stroke_width=2, stroke_fill=(0, 0, 0))
# Ядовитые пещеры: вход и ход к Чёрному озеру
pts = [(-849, -151), (-870, -185), (-895, -205), (-905, -215)]
d.line([P(*p) for p in pts], fill=(150, 230, 60), width=4)
mark(-849, -151, "Ядовитые пещеры (вход y 84)", (150, 230, 60))
mark(-958, -185, "Чаша Двух Вод (уступ y 108)", (220, 220, 255), 10, 6)
d.line([P(-940, -150), P(-952, -165), P(-948, -176), P(-958, -185)], fill=(220, 220, 255), width=3)
mark(-915, -52, "Руины святилища", (255, 255, 255), 8, 4)
mark(-915, -100, "Исцеляющее озеро (вода y 76)", (60, 200, 210), -110, -30)
# пути
mark(-770, -80, "Перевал (седло y 128)", (255, 160, 60), -60, 14)
d.line([P(-640, -190), P(-700, -130), P(-745, -95), P(-770, -80)], fill=(255, 160, 60), width=4)
mark(-640, -190, "Завал на перевале Р1", (255, 160, 60), -210, -24)
tun = [(-905, 140), (-912, 80), (-918, 25)]
for a, c in zip(tun, tun[1:]):
    d.line([P(*a), P(*c)], fill=(255, 90, 90), width=4)
mark(-905, 140, "Тайный тоннель (вход y 74)", (255, 90, 90), 8, -8)
mark(-918, 25, "выход в долину", (255, 90, 90), 8, -8)
climb = [(-1150, -40), (-1110, -55), (-1085, -75), (-1068, -82)]
d.line([P(*p) for p in climb], fill=(255, 120, 220), width=4)
mark(-1150, -40, "Опасный подъём (с берега)", (255, 120, 220), 8, 6)
mark(-1026, -186, "Высший пик y 250 — Башня Шипов", (255, 255, 255), -150, -30)
mark(CX, CZ, "центр (−920, −80)", (255, 50, 50), 8, 2)
img.save(os.path.join(OUT, "ring_mountain_preview.png"))

print("min/max y:", int(h.min()), int(h.max()))
for name, (x, z) in {"центр": (CX, CZ), "озеро": LAKE[:2], "Чаша": (-958, -185), "перевал": (-770, -80),
                     "пик СЗ": (-1026, -186), "вход яд. пещер": (-849, -151), "выход тоннеля": (-918, 25)}.items():
    print(f"{name:16s} y={int(h[z - Z0, x - X0])}")
