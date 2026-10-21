#!/usr/bin/env python3
"""Карта высот Пепельной горы (Р6). Архитектор.

Пишет рядом с собой (в docs/design/heightmaps/):
  ash_mountain_height.png    — 8 бит, 1 пиксель = 1 блок, y = значение + 40
  ash_mountain_material.png  — карта материалов (индексы цветов, легенда в Пепельная гора.md)
  ash_mountain_preview.png   — схема для глаз: цвет по высоте, горизонтали, тропа, точки
  ash_mountain_profiles.csv  — профили по 8 направлениям от центра, шаг 5

Запуск: python3 ash_mountain.py (numpy, Pillow). Детерминирован (seed 2066).
"""
import math, os, csv
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
X0, Z0, W, H = 1060, -900, 440, 500          # x +1060…+1499, z −900…−401
CX, CZ = 1280, -620                           # центр вулкана
Y_OFFSET = 40
BASE_Y = 80                                   # Пустошь вокруг (сшивать с генерацией)
FOOT_R, RIM_R, FLOOR_R = 200, 45, 30
FLOOR_Y, LAVA_Y = 256, 253
LAKE_R, ISLAND_R, ISLAND_Y = 18, 8, 257
NOTCH_BEAR, NOTCH_Y = 225, 272                # Пролом — вход в кратер с юго-запада
RIDGE_Z, RIDGE_FOOT = -870, 80                # Северный хребет: ось и полуширина склона

rng = np.random.default_rng(2066)

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
    return n / sum(amps) * 2 - 1

def bearing_deg(dx, dz):
    return (np.degrees(np.arctan2(dx, -dz)) + 360) % 360

def ang_dist(a, b):
    d = np.abs(a - b) % 360
    return np.minimum(d, 360 - d)

def polar(r, bear):
    return CX + r * math.sin(math.radians(bear)), CZ - r * math.cos(math.radians(bear))

zz, xx = np.mgrid[0:H, 0:W]
wx = xx + X0; wz = zz + Z0
dx = wx - CX; dz = wz - CZ
r = np.hypot(dx, dz)
b = bearing_deg(dx, dz)
n_big = fbm((H, W)); n_small = fbm((H, W), cells=(10, 5, 3), amps=(1, .6, .3))

# --- гребень кратера: выше на севере (к хребту), Пролом на юго-западе ---
rim_h = 284 + 5 * n_big
rim_h = rim_h + 11 * np.exp(-(ang_dist(b, 10) / 35) ** 2)          # северный пик ~295
notch = np.exp(-(ang_dist(b, NOTCH_BEAR) / 6) ** 2)
rim_h = rim_h * (1 - notch) + NOTCH_Y * notch

# --- конус: вогнутый склон, юго-запад (к Городу) длиннее и положе ---
foot_r = FOOT_R + 25 * np.exp(-(ang_dist(b, 225) / 50) ** 2) + 8 * n_big
t = np.clip((foot_r - r) / (foot_r - RIM_R), 0, 1)
cone = BASE_Y + (rim_h - BASE_Y) * t ** 1.7
# кратер: внутренняя стена гребень → дно, дно, лавовое озеро, остров
t2 = np.clip((r - FLOOR_R) / (RIM_R - FLOOR_R), 0, 1)
crater_wall = FLOOR_Y + (rim_h - FLOOR_Y) * t2 ** 0.6
h = np.where(r >= RIM_R, cone, crater_wall)
h = np.where(r < FLOOR_R, FLOOR_Y + 1.0 * np.clip((r - LAKE_R) / (FLOOR_R - LAKE_R), 0, 1), h)
h = np.where(r < LAKE_R, LAVA_Y - 3, h)                               # дно озера под лавой
h = np.where(r < ISLAND_R, ISLAND_Y, h)

# --- лавовые потоки: радиальные ложбины на склонах ---
FLOWS = [(60, 4, True), (100, 5, True), (140, 4, False), (170, 3, False), (290, 4, False)]
flow_mask = np.zeros_like(r, dtype=bool); lava_mask = np.zeros_like(r, dtype=bool)
for bear, half_w, live in FLOWS:
    wiggle = bear + 6 * n_big
    lateral = r * np.radians(ang_dist(b, wiggle))
    m = (lateral < half_w) & (r > RIM_R + 2) & (r < foot_r - 10)
    h = np.where(m, h - 2 - (half_w - lateral) * 0.4, h)
    flow_mask |= m
    if live:
        lava_mask |= m & (lateral < half_w * 0.45) & (r < 150)

# --- шероховатость ---
h = h + n_small * np.where(r < FLOOR_R, 0.3, np.where(r < RIM_R, 2.5, 3.0))

# --- Северный хребет (ось z −870): вулкан сливается с ним ---
dzr = np.abs(wz - RIDGE_Z)
ridge_top = 248 + 12 * n_big
ridge = ridge_top - (ridge_top - BASE_Y) * np.clip(dzr / RIDGE_FOOT, 0, 1) ** 1.4
h = np.maximum(h, ridge)
ridge_mask = ridge > np.maximum(cone, BASE_Y) + 2
# --- окрестность и сшивка ---
h = np.where(r >= foot_r, np.maximum(BASE_Y + 3 * n_big, ridge), h)
# седловина: северный склон вулкана переходит в хребет без долины между ними
u = np.clip((r - RIM_R) / (CZ - RIDGE_Z - RIM_R), 0, 1)
saddle_h = rim_h * (1 - u) + ridge_top * u - 45 * np.sin(np.pi * u)
wgt = np.exp(-(ang_dist(b, 0) / 28) ** 2) * (wz < CZ) * (wz >= RIDGE_Z)
h = np.where(r >= RIM_R, np.maximum(h, saddle_h * wgt + h * (1 - wgt)), h)


# --- тропа восхождения: серпантин по юго-западному склону ---
LEGS = [(None, None, (1112, -412)), (185, 205, None), (160, 245, None), (132, 205, None),
        (106, 245, None), (82, 208, None), (62, 240, None), (RIM_R + 1, NOTCH_BEAR, None)]
pts = []
for rr, bb, xy in LEGS:
    pts.append(xy if xy else polar(rr, bb))
road = np.zeros_like(r, dtype=bool)
road_y = np.full_like(r, np.nan)
path_samples = []
for (ax, az), (bx, bz) in zip(pts, pts[1:]):
    n = int(math.hypot(bx - ax, bz - az))
    for i in range(n + 1):
        px, pz = ax + (bx - ax) * i / n, az + (bz - az) * i / n
        path_samples.append((px, pz))
# высота тропы — профиль конуса под осью, сглажен и монотонно растёт
ys = []
for px, pz in path_samples:
    ix, iz = int(round(px - X0)), int(round(pz - Z0))
    ys.append(h[min(max(iz, 0), H - 1), min(max(ix, 0), W - 1)])
ys = np.maximum.accumulate(np.convolve(np.pad(ys, 6, mode="edge"), np.ones(13) / 13, mode="valid"))
ys[-1] = NOTCH_Y; ys = np.minimum(ys, NOTCH_Y)
for (px, pz), y in zip(path_samples, ys):
    x0i, z0i = int(px - X0), int(pz - Z0)
    for oz in range(-5, 6):
        for ox in range(-5, 6):
            ix, iz = x0i + ox, z0i + oz
            if not (0 <= ix < W and 0 <= iz < H):
                continue
            d = math.hypot(ix + X0 - px, iz + Z0 - pz)
            if d <= 2.5:
                road[iz, ix] = True
                road_y[iz, ix] = y if np.isnan(road_y[iz, ix]) else max(road_y[iz, ix], y)
            elif d <= 5 and not road[iz, ix]:
                k = (d - 2.5) / 2.5
                h[iz, ix] = h[iz, ix] * k + y * (1 - k) if h[iz, ix] < y else h[iz, ix] * k + (y + 1) * (1 - k)
h = np.where(road, road_y, h)
# пандус в кратер: от Пролома вниз к дну и дамба к острову
ramp = []
nx, nz = polar(RIM_R + 1, NOTCH_BEAR)
for i in range(0, 41):
    rr = RIM_R + 1 - i * (RIM_R + 1 - ISLAND_R) / 40
    px, pz = polar(rr, NOTCH_BEAR)
    y = NOTCH_Y - (NOTCH_Y - FLOOR_Y) * min(1, i / 16)
    if rr < LAKE_R:
        y = FLOOR_Y
    ramp.append((px, pz, y))
for px, pz, y in ramp:
    for oz in range(-3, 4):
        for ox in range(-3, 4):
            ix, iz = int(px - X0) + ox, int(pz - Z0) + oz
            if 0 <= ix < W and 0 <= iz < H and math.hypot(ix + X0 - px, iz + Z0 - pz) <= 2.5:
                h[iz, ix] = y; road[iz, ix] = True

# --- Скит Пепельного Монаха: терраса на южном отроге ---
SKIT = polar(118, 162)
dsk = np.hypot(wx - SKIT[0], wz - SKIT[1])
skit_y = float(h[int(SKIT[1] - Z0), int(SKIT[0] - X0)])
h = np.where(dsk < 9, skit_y, h)
# --- вход в Лавовую трубу (сокровищница): ниша на восточном склоне ---
TUBE = polar(150, 100)

h = np.clip(np.round(h), 41, 295)
gray = (h - Y_OFFSET).astype(np.uint8)
Image.fromarray(gray, mode="L").save(os.path.join(OUT, "ash_mountain_height.png"))

# --- материалы ---
# 0 пепел и туф (нижние склоны) · 1 базальт (верх) · 2 чернокамень хребта · 3 застывший поток (магма, базальт)
# 4 живая лава в потоке · 5 обсидиан кратера · 6 лавовое озеро · 7 тропа · 8 остров врат
mat = np.zeros_like(r, dtype=np.uint8)
mat[h >= 180] = 1
mat[ridge_mask & (r > foot_r - 20)] = 2
mat[flow_mask] = 3
mat[lava_mask] = 4
mat[(r < RIM_R) & (r >= LAKE_R)] = 5
mat[r < LAKE_R] = 6
mat[road] = 7
mat[r < ISLAND_R] = 8
pal = [(150, 145, 140), (70, 68, 72), (35, 30, 35), (150, 60, 30), (255, 120, 20), (40, 20, 60), (255, 80, 0), (230, 220, 160), (120, 220, 255)]
Image.fromarray(np.array(pal, dtype=np.uint8)[mat]).save(os.path.join(OUT, "ash_mountain_material.png"))

# --- профили ---
with open(os.path.join(OUT, "ash_mountain_profiles.csv"), "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["направление", "азимут"] + [f"r={d}" for d in range(0, 231, 5)])
    for name, bear in [("С", 0), ("СВ", 45), ("В", 90), ("ЮВ", 135), ("Ю", 180), ("ЮЗ (Пролом)", 225), ("З", 270), ("СЗ", 315)]:
        row = []
        for d in range(0, 231, 5):
            px, pz = polar(d, bear)
            ix, iz = int(round(px - X0)), int(round(pz - Z0))
            row.append(int(h[iz, ix]) if 0 <= ix < W and 0 <= iz < H else "")
        wr.writerow([name, bear] + row)

# --- схема ---
def hyps(y):
    stops = [(41, (90, 85, 80)), (80, (120, 115, 108)), (140, (105, 95, 90)), (190, (80, 72, 72)),
             (240, (60, 52, 55)), (280, (45, 35, 40)), (295, (30, 20, 25))]
    for (y0, c0), (y1, c1) in zip(stops, stops[1:]):
        if y <= y1:
            tt = (y - y0) / (y1 - y0)
            return tuple(int(c0[i] + (c1[i] - c0[i]) * tt) for i in range(3))
    return stops[-1][1]
lut = np.array([hyps(y) for y in range(300)], dtype=np.uint8)
rgb = lut[h.astype(int)].astype(float)
gz_, gx_ = np.gradient(h)
shade = np.clip(1 - (gx_ * 0.8 + gz_ * 0.8) / 12, 0.5, 1.3)
rgb = np.clip(rgb * shade[..., None], 0, 255)
rgb[flow_mask] = rgb[flow_mask] * 0.6 + np.array([150, 60, 30]) * 0.4
rgb[lava_mask] = (255, 120, 20)
rgb[r < LAKE_R] = (255, 80, 0)
rgb[r < ISLAND_R] = (40, 30, 50)
rgb[road] = (230, 220, 160)
rgb = rgb.astype(np.uint8)
cont = np.zeros_like(h, dtype=bool)
lvl = (h // 20).astype(int)
cont[:-1] |= lvl[:-1] != lvl[1:]; cont[:, :-1] |= lvl[:, :-1] != lvl[:, 1:]
rgb[cont & ~road] = (rgb[cont & ~road] * 0.55).astype(np.uint8)
SC = 2
img = Image.fromarray(rgb).resize((W * SC, H * SC), Image.NEAREST)
d = ImageDraw.Draw(img)
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font, small = ImageFont.truetype(F, 15), ImageFont.truetype(F, 12)
P = lambda x, z: ((x - X0) * SC, (z - Z0) * SC)
for gx in range(1100, 1500, 100):
    d.line([P(gx, Z0), P(gx, Z0 + H)], fill=(90, 90, 90)); d.text((P(gx, Z0)[0] + 3, 3), f"x {gx}", fill=(230, 230, 230), font=small)
for gzv in range(-900, -400, 100):
    d.line([P(X0, gzv), P(X0 + W, gzv)], fill=(90, 90, 90)); d.text((3, P(X0, gzv)[1] + 3), f"z {gzv}", fill=(230, 230, 230), font=small)
def mark(x, z, text, col=(255, 230, 80)):
    px, pz = P(x, z)
    d.ellipse([px - 6, pz - 6, px + 6, pz + 6], fill=col, outline=(0, 0, 0))
    tw = d.textlength(text, font=small); tx = px + 9 if px + 9 + tw < W * SC - 4 else px - 9 - tw
    d.text((tx, pz - 8), text, fill=(255, 255, 255), font=small, stroke_width=2, stroke_fill=(0, 0, 0))
nxp, nzp = polar(RIM_R + 1, NOTCH_BEAR)
mark(1112, -412, "Начало Восхождения (костёр)", (255, 160, 60))
mark(nxp, nzp, f"Пролом y {NOTCH_Y}: костёр", (255, 160, 60))
mark(CX, CZ, f"Остров врат y {ISLAND_Y}: врата в Край, маяк", (120, 220, 255))
mark(*SKIT, f"Скит Монаха y {int(skit_y)}", (200, 255, 200))
mark(*TUBE, "Лавовая труба (сокровищница)", (255, 120, 120))
mark(CX, -870, "ось Северного хребта", (200, 200, 200))
d.text((10, H * SC - 26), "Пепельная гора: x +1060…+1499, z −900…−401. Горизонтали через 20. Светлая — тропа. Север — вверх.", fill=(255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
img.save(os.path.join(OUT, "ash_mountain_preview.png"))
print("ok skit", [round(v) for v in SKIT], int(skit_y), "tube", [round(v) for v in TUBE], int(h[int(TUBE[1] - Z0), int(TUBE[0] - X0)]),
      "notch", [round(nxp), round(nzp)], "max", int(h.max()), "legs", [(round(x), round(z)) for x, z in pts])
