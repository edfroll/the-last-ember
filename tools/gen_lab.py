#!/usr/bin/env python3
"""T-018, the monster lab: the resource-pack and data parts of the five lab samples (generated, do not edit by hand).
  resource pack: textures/item/lab/atlas.png (procedural materials), models/item/lab/*.json (box models), items/lab/*.json,
                 equipment/lab_drowner.json + its humanoid layers (the skin of sample 1), textures/entity/wolf/lab_warg*.png (sample 2);
  datapack:      wolf_variant/lab_warg.json, function/lab/gen/* (the rig of the Leshy: poses, the head looking around).
The vanilla textures the skins are made from are read from the 26.3 client jar.
Usage: python3 tools/gen_lab.py"""
import json, math, os, random, shutil, sys, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools/lab")); import png
RP = os.path.join(ROOT, "resourcepack/assets/last_ember"); DP = os.path.join(ROOT, "datapack/data/last_ember")
JAR = os.path.expanduser("~/Library/Application Support/minecraft/versions/26.3/26.3.jar")
jar = zipfile.ZipFile(JAR)
def vanilla(p): return png.read(jar.read("assets/minecraft/textures/" + p))
def wjson(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: json.dump(obj, f, ensure_ascii=False, indent=1)
def wtext(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: f.write(text)
def wpng(path, rows): os.makedirs(os.path.dirname(path), exist_ok=True); png.write(path, rows)
rnd = random.Random(18)
def clamp(v): return max(0, min(255, int(v)))

# ---------------------------------------------------------------- materials: a 64x64 atlas of 16 tiles of 16x16
MATS = ["bark", "moss", "bone", "glow_amber", "dark", "slime", "slime_light", "flesh", "seaweed", "teeth", "root", "glow_green", "glow_red", "glow_violet", "mud", "bark_light"]
M = {n: i for i, n in enumerate(MATS)}
GLOW = {"glow_amber", "glow_green", "glow_red", "glow_violet"}
def tile(name):
    t = [[None] * 16 for _ in range(16)]
    r = random.Random(name)
    base = {"bark": (58, 44, 32), "moss": (46, 62, 34), "bone": (196, 186, 160), "glow_amber": (255, 178, 70), "dark": (16, 12, 12),
            "slime": (70, 82, 48), "slime_light": (112, 120, 74), "flesh": (96, 108, 98), "seaweed": (40, 58, 36), "teeth": (210, 200, 160),
            "root": (40, 30, 24), "glow_green": (190, 255, 170), "glow_red": (255, 70, 40), "glow_violet": (220, 140, 255), "mud": (64, 52, 38),
            "bark_light": (92, 72, 50)}[name]
    streak = [r.uniform(-1, 1) for _ in range(16)]
    for y in range(16):
        for x in range(16):
            if name in GLOW:
                k = 1.0 if 4 <= x <= 11 and 4 <= y <= 11 else 0.85
                c = tuple(clamp(v * k) for v in base); a = 255
            elif name in ("bark", "bark_light", "root"):
                v = 1 + 0.22 * streak[x] + 0.12 * r.uniform(-1, 1) + (0.18 if (x + y // 5) % 7 == 0 else 0) * -1
                c = tuple(clamp(b * v) for b in base); a = 255
            elif name in ("slime", "slime_light"):
                v = 1 + 0.12 * r.uniform(-1, 1) + (0.25 if r.random() < 0.06 else 0)
                c = tuple(clamp(b * v) for b in base); a = 238
            else:
                v = 1 + 0.16 * r.uniform(-1, 1) + (-0.25 if r.random() < 0.08 else 0)
                c = tuple(clamp(b * v) for b in base); a = 255
            t[y][x] = c + (a,)
    return t
atlas = [[(0, 0, 0, 0)] * 64 for _ in range(64)]
for i, n in enumerate(MATS):
    t = tile(n); ox, oy = (i % 4) * 16, (i // 4) * 16
    for y in range(16):
        for x in range(16): atlas[oy + y][ox + x] = t[y][x]
wpng(os.path.join(RP, "textures/item/lab/atlas.png"), atlas)

# ---------------------------------------------------------------- box models
# Boxes are written in the RIG FRAME in pixels (1/16 block) relative to the pivot of the part: +Y up, +Z forward (where the mob looks), +X its left.
# The item display turns its model by 180 degrees around Y, so the model gets x -> -x, z -> -z; "s" shrinks a part that is too long for the
# model limits (-16..32), the display scales it back by 1/s.
def B(x1, y1, z1, x2, y2, z2, mat): return (x1, y1, z1, x2, y2, z2, mat)
def face_uv(mat, w, h):
    i = M[mat]; u0, v0 = (i % 4) * 4, (i // 4) * 4
    du, dv = min(abs(w), 16) / 4, min(abs(h), 16) / 4
    return [u0, v0, u0 + max(du, 0.25), v0 + max(dv, 0.25)]
def model(name, boxes, s=1.0, frame=True, display=None):
    els = []
    for (x1, y1, z1, x2, y2, z2, mat) in boxes:
        if frame: fx1, fx2, fz1, fz2 = 8 - x2 * s, 8 - x1 * s, 8 - z2 * s, 8 - z1 * s
        else: fx1, fx2, fz1, fz2 = x1, x2, z1, z2
        fy1, fy2 = (8 + y1 * s, 8 + y2 * s) if frame else (y1, y2)
        fr, to = [round(v, 3) for v in (fx1, fy1, fz1)], [round(v, 3) for v in (fx2, fy2, fz2)]
        assert all(-16 <= v <= 32 for v in fr + to), (name, fr, to)
        w, h, d = to[0] - fr[0], to[1] - fr[1], to[2] - fr[2]
        faces = {f: {"uv": face_uv(mat, *wh), "texture": "#a", "tintindex": 0} for f, wh in
                 (("north", (w, h)), ("south", (w, h)), ("east", (d, h)), ("west", (d, h)), ("up", (w, d)), ("down", (w, d)))}
        e = {"from": fr, "to": to, "faces": faces}
        if mat in GLOW: e["light_emission"] = 15; e["shade"] = False
        els.append(e)
    m = {"textures": {"a": "last_ember:item/lab/atlas", "particle": "last_ember:item/lab/atlas"}, "elements": els}
    if display: m["display"] = display
    wjson(os.path.join(RP, f"models/item/lab/{name}.json"), m)
    # the tint (custom_model_data colors[0], white by default) flashes the part red when the monster is hurt
    wjson(os.path.join(RP, f"items/lab/{name}.json"), {"model": {"type": "minecraft:model", "model": f"last_ember:item/lab/{name}",
          "tints": [{"type": "minecraft:custom_model_data", "index": 0, "default": -1}]}})
def mirror(boxes): return [B(-x2, y1, z1, -x1, y2, z2, m) for (x1, y1, z1, x2, y2, z2, m) in boxes]

# ---- probe: a nose to the front (+Z of the frame), a glowing cap; to check orientation and the light of the displays
model("probe", [B(-4, 0, -4, 4, 8, 4, "bone"), B(-1, 3, 4, 1, 5, 10, "glow_red"), B(-4, 8, -4, 4, 9, 4, "glow_green"), B(4, 0, -1, 8, 2, 1, "bark")])

# ---- 1. drowner: the head (a head-slot item: model space of a carved pumpkin, the face on the north side)
head = [B(1.5, 2, 1.5, 14.5, 15, 14.5, "flesh"), B(2, 15, 3, 9, 16, 12, "flesh"),                   # skull, a swollen crown
        B(3, 8, 1.1, 7, 11, 1.6, "dark"), B(9.5, 8.5, 1.1, 13, 11.5, 1.6, "dark"),                       # deep sockets, not alike
        B(4.6, 9, 0.9, 5.6, 10, 1.3, "glow_green"), B(10.8, 9.5, 0.9, 11.8, 10.5, 1.3, "glow_green"),   # small pale pupils
        B(7.3, 6.5, 1.1, 8.7, 8, 1.6, "dark"),                                                          # the nose hole
        B(3, 0, 1.0, 13, 5.5, 1.6, "dark"),                                                             # the gaping maw
        B(4, 3.5, 0.7, 5, 5.5, 1.1, "teeth"), B(8, 4, 0.7, 8.8, 5.5, 1.1, "teeth"), B(11, 3, 0.7, 12, 5.5, 1.1, "teeth"),
        B(5.5, 0, 0.7, 6.5, 1.5, 1.1, "teeth"), B(10, 0, 0.7, 10.8, 2, 1.1, "teeth"),
        B(3, -4, 0.2, 13, 0, 7, "flesh"), B(3.5, -0.5, 0.1, 12.5, 0, 6.5, "dark"),                       # the lower jaw hangs
        B(1, 3, 0.6, 3.5, 15.5, 3, "seaweed"), B(12.5, 5, 0.6, 15, 15.5, 2.5, "seaweed"), B(1, 15, 1, 15, 16.2, 15, "seaweed"),  # weed over the face, the crown
        B(0.8, 6, 6, 1.5, 11, 6.6, "dark"), B(0.8, 6, 8, 1.5, 11, 8.6, "dark"), B(14.5, 6, 6, 15.2, 11, 6.6, "dark"), B(14.5, 6, 8, 15.2, 11, 8.6, "dark"),  # gills
        B(2, -7, 14.5, 5, 15, 15.6, "seaweed"), B(6.5, -10, 14.5, 9, 15, 15.6, "seaweed"), B(10.5, -6, 14.5, 14, 15, 15.6, "seaweed"),
        B(5, 15.5, 5, 7, 16.8, 7, "mud"), B(10, 15, 9, 12, 16.5, 11, "mud")]
model("drowner_head", head, frame=False, display={"head": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]}})

# ---- 2. warg: glowing eyes riding the mob while it lies in ambush (scaled by the display)
model("warg_eyes", [B(-1.9, -0.45, 0, -0.9, 0.45, 0.5, "glow_red"), B(0.9, -0.45, 0, 1.9, 0.45, 0.5, "glow_red")])

# ---- 3. swamp womb: a blob 1 block wide standing on its pivot (scaled with the size of the slime)
womb = [B(-6, 0, -6, 6, 1.5, 6, "slime"), B(-7.5, 1.5, -7, 7.5, 4, 7.5, "slime"), B(-8, 4, -7.5, 8, 8, 8, "slime"),
        B(-7, 8, -6.5, 7, 10.5, 7, "slime"), B(-5, 10.5, -4.5, 5.5, 12, 5, "slime_light"), B(-2.5, 12, -2, 3, 13, 2.5, "slime_light"),   # a sagging heap
        B(5, 7, 3, 8.8, 10, 6.5, "slime_light"), B(-8.6, 3, -3, -7, 7, 1, "slime_light"), B(-3, 9, -7.5, 1, 12, -5.5, "slime"), B(2, 4, -8.6, 6, 7.5, -7.5, "mud"),
        B(-6, 2.5, 7.6, 5, 6.0, 8.3, "dark"), B(-5.5, 1.2, 7.5, 4.5, 2.5, 9, "slime_light"),               # the maw, a hanging lip
        B(-5, 4.8, 8.3, -4.2, 6, 8.7, "teeth"), B(-2.2, 5.0, 8.3, -1.4, 6.0, 8.7, "teeth"), B(2.8, 4.5, 8.3, 3.8, 6.0, 8.7, "teeth"),
        B(-0.5, 2.5, 8.3, 0.3, 3.6, 8.7, "teeth"), B(-4, 2.5, 8.3, -3.3, 3.3, 8.7, "teeth"),
        B(-5.6, 8.4, 6.9, -3.8, 9.8, 7.4, "glow_green"), B(1.2, 9.0, 6.9, 2.2, 10.0, 7.4, "glow_green"), B(3.6, 6.4, 7.9, 5.0, 7.6, 8.4, "glow_green"),  # three eyes, not alike
        B(-1, -0.5, 8.3, -0.3, 2.5, 8.7, "slime_light"),                                                      # drool
        B(-6, 1, -8.2, -4, 10, -7.6, "seaweed"), B(1, 3, -8.2, 3, 11, -7.6, "seaweed"), B(-8.5, 2, 3, -8, 9, 5, "seaweed"), B(8, 1, -6, 8.5, 8, -4, "seaweed")]
model("womb", womb)

# ---- 4. leshy: six parts (pivots in the rig below)
torso = [B(-7, 0, -4, 7, 19, 4, "bark"), B(-9, 15, -5, 9, 20, 5, "moss"), B(-6, 19, -3, 6, 21, 3, "moss"),
         B(-6, 13, 4, 6, 14, 5, "bone"), B(-6, 10.5, 4, 6, 11.5, 5, "bone"), B(-5.5, 8, 4, 5.5, 9, 5, "bone"),   # ribs
         B(-1.5, 9, 3.6, 1.5, 12.5, 4.2, "glow_amber"),                                                          # the ember in the chest
         B(-6, -2, -4.5, -2, 6, -4, "moss"), B(1, -4, -4.5, 5, 7, -4, "moss"), B(-7.5, 2, -3, -7, 14, 3, "bark_light"), B(7, 4, -3, 7.5, 15, 3, "bark_light")]
lhead = [B(-2, 0, -1.5, 2, 3, 2, "bark"), B(-4, 3, -3, 4, 10, 4, "bone"), B(-2.5, 3, 4, 2.5, 7, 10, "bone"),
         B(-2.2, 2.6, 6, 2.2, 3.2, 9.5, "dark"),
         B(1.2, 6.5, 4, 3.2, 8.5, 4.3, "dark"), B(-3.2, 6.5, 4, -1.2, 8.5, 4.3, "dark"),
         B(1.7, 7.0, 4.3, 2.7, 8.0, 4.5, "glow_amber"), B(-2.7, 7.0, 4.3, -1.7, 8.0, 4.5, "glow_amber")]
antler = [B(3, 9, -1, 4.5, 14, 0.5, "bone"), B(4.5, 12.5, -1, 9, 14, 0.5, "bone"), B(7.5, 14, -1, 9, 22, 0.5, "bone"), B(5.5, 14, -0.5, 6.8, 18.5, 3.5, "bone"),
          B(9, 18, -1, 12, 19.2, 0.5, "bone")]
lhead += antler + mirror(antler)
arm = [B(-2, -14, -2, 2, 0, 2, "bark"), B(-2.5, -3, -2.5, 2.5, 1.5, 2.5, "moss"), B(-1.5, -26, -1.5, 1.5, -14, 1.5, "bark"),
       B(-2, -31, -0.5, -1, -26, 1.5, "root"), B(-0.5, -32, 0, 0.5, -26, 2, "root"), B(1, -31, -0.5, 2, -26, 1.5, "root"), B(-1.6, -20, -1.6, 1.6, -18, 1.6, "moss")]
leg = [B(-2.5, -21, -2.5, 2.5, 0, 2.5, "bark"), B(-3.5, -21, -3, 3.5, -19, 5, "root"), B(-1, -21, 5, 1, -20, 8, "root"), B(-3, -10, -3, 3, -8, 3, "moss")]
if os.environ.get("LAB_PROBE"):   # debugging: every element of the arm alone
    for i, b in enumerate(arm): model(f"probe_arm{i}", [b], s=0.72)
    model("probe_arm_s1", [B(-2, -14, -2, 2, 0, 2, "bark")])
model("leshy_torso", torso); model("leshy_head", lhead); model("leshy_arm", arm, s=0.72); model("leshy_leg", leg)

# ---------------------------------------------------------------- 1. drowner: the skin (the humanoid layers of the equipment asset)
w, h, zr = vanilla("entity/zombie/zombie.png")
skin = [[(0, 0, 0, 0)] * 64 for _ in range(32)]
r = random.Random(1)
blots = [(r.randrange(64), r.randrange(32), r.uniform(1.0, 3.2), r.uniform(0.45, 0.75)) for _ in range(70)]
weeds = [(r.randrange(64), r.randrange(8, 32), r.randrange(3, 9)) for _ in range(26)]
for y in range(32):
    for x in range(64):
        p = zr[y][x]
        if p[3] == 0: continue
        L = (p[0] * 0.3 + p[1] * 0.59 + p[2] * 0.11) / 255
        c = [58 + 90 * L, 70 + 86 * L, 66 + 80 * L]                       # drowned grey-green, cold
        for bx, by, br, bk in blots:                                      # rot: soft dark blotches of different size
            if (x - bx) ** 2 + (y - by) ** 2 <= br * br: c = [v * bk for v in c]
        for wx, wy, wl in weeds:                                          # weed hanging in wisps
            if x == wx and wy <= y < wy + wl: c = [34, 52, 32]
        if 20 <= x < 28 and y in (22, 24, 26) and 21 <= x <= 26: c = [v * 1.35 for v in c]   # ribs under the skin of the chest
        if y >= 29 and 40 <= x < 56: c = [v * 0.6 for v in c]            # darker hands
        skin[y][x] = tuple(clamp(v + r.uniform(-7, 7)) for v in c) + (255,)
for lay in ("humanoid", "humanoid_leggings"): wpng(os.path.join(RP, f"textures/entity/equipment/{lay}/lab_drowner.png"), skin)
wjson(os.path.join(RP, "equipment/lab_drowner.json"), {"layers": {"humanoid": [{"texture": "last_ember:lab_drowner"}], "humanoid_leggings": [{"texture": "last_ember:lab_drowner"}]}})

# ---------------------------------------------------------------- 2. warg: its own wolf variant (never spawns by itself: no spawn conditions)
w, h, wr = vanilla("entity/wolf/wolf_black_angry.png")
r = random.Random(2); warg = []
for y in range(h):
    row = []
    for x in range(w):
        p = wr[y][x]
        if p[3] == 0: row.append(p); continue
        L = (p[0] + p[1] + p[2]) / 765
        c = [30 + 96 * L, 27 + 80 * L, 25 + 70 * L]                         # soot-black and ash-grey, rough
        if r.random() < 0.08: c = [v * 0.62 for v in c]
        elif r.random() < 0.05: c = [v * 1.3 for v in c]
        row.append(tuple(clamp(v) for v in c) + (255,))
    warg.append(row)
for k in ("", "_angry", "_tame", "_baby", "_angry_baby", "_tame_baby"): wpng(os.path.join(RP, f"textures/entity/wolf/lab_warg{k}.png"), warg)
wjson(os.path.join(DP, "wolf_variant/lab_warg.json"), {"assets": {"angry": "last_ember:entity/wolf/lab_warg_angry", "tame": "last_ember:entity/wolf/lab_warg_tame", "wild": "last_ember:entity/wolf/lab_warg"},
      "baby_assets": {"angry": "last_ember:entity/wolf/lab_warg_angry_baby", "tame": "last_ember:entity/wolf/lab_warg_tame_baby", "wild": "last_ember:entity/wolf/lab_warg_baby"},
      "spawn_conditions": []})

# ---------------------------------------------------------------- 4. the rig of the leshy
# Rig frame: blocks, origin at the feet of the carrier. Every part rides the carrier, so its display origin is the passenger point (0, PASS_Y, 0).
# passenger points measured in 26.3 (display Pos - mob Pos): husk scale 1.6 -> 3.32, slime Size:2 -> 1.513, wolf scale 1.7 -> 1.392, silverfish scale 3 -> 0.7125.
# The item display shows the model turned by 180 degrees: the +Z of the rig frame is the side the display looks at (checked with lab/probe).
PASS_Y = float(os.environ.get("LAB_PASS_Y", "3.32"))
ARM_S = 0.72
PARTS = {"torso": ("root", (0, 1.3, 0)), "head": ("torso", (0, 1.19, 0.05)), "arm_l": ("torso", (0.56, 1.06, 0)), "arm_r": ("torso", (-0.56, 1.06, 0)),
         "leg_l": ("root", (0.28, 1.3, 0)), "leg_r": ("root", (-0.28, 1.3, 0))}
def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx, aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)
def qaxis(ax, deg):
    t = math.radians(deg) / 2; s = math.sin(t)
    return {"x": (s, 0, 0, math.cos(t)), "y": (0, s, 0, math.cos(t)), "z": (0, 0, s, math.cos(t))}[ax]
def qeul(p, yw, rl): return qmul(qmul(qaxis("y", yw), qaxis("x", p)), qaxis("z", rl))   # yaw, then pitch, then roll
def qrot(q, v):
    x, y, z, w_ = q; vq = (v[0], v[1], v[2], 0); qi = (-x, -y, -z, w_)
    r_ = qmul(qmul(q, vq), qi); return (r_[0], r_[1], r_[2])
def solve(pose, look=0.0):
    """pose: {part: (pitch, yaw, roll)}, 'root': (pitch, yaw, roll, dy), 'scale': k -> {part: (translation, quaternion, scale)}"""
    rp = pose.get("root", (0, 0, 0, 0)); k = pose.get("scale", 1.0)
    world = {"root": ((0, rp[3], 0), qeul(rp[0], rp[1], rp[2]))}
    out = {}
    for part in ("torso", "head", "arm_l", "arm_r", "leg_l", "leg_r"):
        par, piv = PARTS[part]; pt, pq = world[par]
        if par == "root": piv = piv
        else: piv = tuple(a - b for a, b in zip(piv, (0, 0, 0)))
        pos = tuple(a + b for a, b in zip(pt, qrot(pq, piv)))
        e = pose.get(part, (0, 0, 0)); q = qmul(pq, qeul(*e))
        if part == "head": q = qmul(q, qaxis("y", look))
        world[part] = (pos, q)
        sc = k * (1 / ARM_S if part.startswith("arm") else 1.0)
        out[part] = ((pos[0] * k + 0, (pos[1] - 0) * k - PASS_Y, pos[2] * k), q, sc)
    return out
def merge(t, q, s, dur):
    f = lambda v: round(v, 4)
    return ("{start_interpolation:0,interpolation_duration:%d,transformation:{translation:[%sf,%sf,%sf],left_rotation:[%sf,%sf,%sf,%sf],scale:[%sf,%sf,%sf],right_rotation:[0f,0f,0f,1f]}}"
            % (dur, f(t[0]), f(t[1]), f(t[2]), f(q[0]), f(q[1]), f(q[2]), f(q[3]), f(s), f(s), f(s)))
LOOKS = list(range(-60, 61, 10))   # le.llook = index 0..12 (6 = straight)
POSES = {
    "idle0": {"torso": (3, 0, 0), "arm_l": (4, 0, -6), "arm_r": (4, 0, 6), "head": (-4, 0, 0)},
    "idle1": {"torso": (-1, 0, 0), "arm_l": (-2, 0, -9), "arm_r": (-2, 0, 9), "head": (2, 0, 0), "root": (0, 0, 0, 0.03)},
    "walk0": {"leg_l": (-24, 0, 0), "leg_r": (22, 0, 0), "arm_l": (18, 0, -6), "arm_r": (-20, 0, 6), "torso": (6, -6, 0), "root": (0, 0, 0, -0.06)},
    "walk1": {"leg_l": (0, 0, 0), "leg_r": (0, 0, 0), "arm_l": (0, 0, -6), "arm_r": (0, 0, 6), "torso": (5, 0, 0), "root": (0, 0, 0, 0.04)},
    "walk2": {"leg_l": (22, 0, 0), "leg_r": (-24, 0, 0), "arm_l": (-20, 0, -6), "arm_r": (18, 0, 6), "torso": (6, 6, 0), "root": (0, 0, 0, -0.06)},
    "walk3": {"leg_l": (0, 0, 0), "leg_r": (0, 0, 0), "arm_l": (0, 0, -6), "arm_r": (0, 0, 6), "torso": (5, 0, 0), "root": (0, 0, 0, 0.04)},
    "windup": {"torso": (-12, 24, 0), "arm_r": (-165, 0, 15), "arm_l": (-30, 0, -25), "head": (-14, 0, 0), "leg_l": (-10, 0, 0), "leg_r": (8, 0, 0)},
    "strike": {"torso": (24, -18, 0), "arm_r": (-25, 0, 0), "arm_l": (10, 0, -15), "head": (10, 0, 0), "leg_l": (-16, 0, 0), "leg_r": (14, 0, 0), "root": (0, 0, 0, -0.1)},
    "rise0": {"root": (0, 0, 0, -4.8), "torso": (30, 0, 0), "arm_l": (-160, 0, -20), "arm_r": (-160, 0, 20), "head": (40, 0, 0)},
    "rise1": {"root": (0, 0, 0, -1.4), "torso": (20, 0, 0), "arm_l": (-150, 0, -30), "arm_r": (-150, 0, 30), "head": (-30, 0, 0)},
    "rise2": {"torso": (-10, 0, 0), "arm_l": (-40, 0, -40), "arm_r": (-40, 0, 40), "head": (-25, 0, 0)},
    "die0": {"torso": (-16, 0, 6), "head": (-35, 0, 0), "arm_l": (-50, 0, -50), "arm_r": (-60, 0, 45), "leg_l": (6, 0, 0)},
    "die1": {"root": (0, 0, 0, -0.55), "torso": (34, 0, -6), "head": (20, 0, 10), "arm_l": (-10, 0, -20), "arm_r": (5, 0, 25), "leg_l": (-30, 0, 4), "leg_r": (-40, 0, -4)},
    "die2": {"root": (80, 0, 0, -0.35), "torso": (8, 0, -4), "head": (30, 25, 20), "arm_l": (-70, 0, -60), "arm_r": (-80, 0, 30), "leg_l": (-10, 0, 8), "leg_r": (-5, 0, -6)},
    "die3": {"root": (80, 0, 0, -0.75), "torso": (8, 0, -4), "head": (30, 25, 20), "arm_l": (-70, 0, -60), "arm_r": (-80, 0, 30), "leg_l": (-10, 0, 8), "leg_r": (-5, 0, -6), "scale": 0.0},
}
gd = os.path.join(DP, "function/lab/gen")
if os.path.isdir(gd): shutil.rmtree(gd)
for name, pose in POSES.items():
    # as the carrier; the macro argument d = the duration of the move in ticks
    lines = [f"# GENERATED by tools/gen_lab.py: the pose {name} of the leshy (as the carrier, macro d = ticks)"]
    sol = solve(pose)
    for part in ("torso", "arm_l", "arm_r", "leg_l", "leg_r"):
        t, q, s = sol[part]
        lines.append(f"$execute on passengers if entity @s[tag=le.lp_{part}] run data merge entity @s " + merge(t, q, s, 0).replace("interpolation_duration:0", "interpolation_duration:$(d)"))
    lines.append(f"function last_ember:lab/gen/head_{name} with storage last_ember:lab anim")
    wtext(os.path.join(gd, f"pose_{name}.mcfunction"), "\n".join(lines) + "\n")
    # the head: the same pose, turned by the look (le.llook) unless the pose drives the head itself
    hl = [f"# GENERATED: the head in the pose {name}, turned by the look index le.llook"]
    for i, lk in enumerate(LOOKS):
        t, q, s = solve(pose, lk if name.startswith(("idle", "walk")) else 0)["head"]
        hl.append(f"$execute if score @s le.llook matches {i} on passengers if entity @s[tag=le.lp_head] run data merge entity @s " + merge(t, q, s, 0).replace("interpolation_duration:0", "interpolation_duration:$(d)"))
    wtext(os.path.join(gd, f"head_{name}.mcfunction"), "\n".join(hl) + "\n")
# the parts at rest (summon data): carrier summons them as passengers
rest = solve(POSES["idle0"])
summ = []
for part in ("torso", "head", "arm_l", "arm_r", "leg_l", "leg_r"):
    t, q, s = rest[part]; mdl = {"torso": "leshy_torso", "head": "leshy_head", "arm_l": "leshy_arm", "arm_r": "leshy_arm", "leg_l": "leshy_leg", "leg_r": "leshy_leg"}[part]
    tr = merge(t, q, s, 0)[1:-1].split("transformation:")[1]
    summ.append('{id:"minecraft:item_display",Tags:["le.lab_part","le.lp_%s"],teleport_duration:3,view_range:1.5f,item_display:"none",item:{id:"minecraft:stick",count:1,components:{"minecraft:item_model":"last_ember:lab/%s"}},transformation:%s}' % (part, mdl, tr))
wtext(os.path.join(gd, "leshy_parts.mcfunction"), "# GENERATED: the parts of the leshy at rest (the passengers the carrier is summoned with: lab/leshy/spawn)\ndata modify storage last_ember:lab leshy_parts set value [" + ",".join(summ) + "]\n")
print(f"lab: {len(MATS)} materials, models probe/drowner_head/warg_eyes/womb/leshy x4, drowner skin, warg variant, {len(POSES)} leshy poses (PASS_Y {PASS_Y})")
