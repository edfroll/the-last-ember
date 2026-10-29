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
if not os.path.exists(JAR): JAR = os.path.join(ROOT, "server/clientjar/26.3.jar")   # the cloud: the client jar downloaded from Mojang (not in git)
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

# ---------------------------------------------------------------- materials: a 128x64 atlas of 32 tiles of 16x16 (8 columns, 4 rows)
MATS = ["bark", "moss", "bone", "glow_amber", "dark", "slime", "slime_light", "flesh", "seaweed", "teeth", "root", "glow_green", "glow_red", "glow_violet", "mud", "bark_light",
        "chitin", "chitin_light", "leg_ochre", "flesh_raw", "gore", "feather", "hair", "bone_old", "glow_white",
        "rust_fur", "heather", "gold"]   # T-020: the heath wolf (appended: the tiles of the others keep their places)
M = {n: i for i, n in enumerate(MATS)}
GLOW = {"glow_amber", "glow_green", "glow_red", "glow_violet", "glow_white"}
def tile(name):
    t = [[None] * 16 for _ in range(16)]
    r = random.Random(name)
    base = {"bark": (58, 44, 32), "moss": (46, 62, 34), "bone": (196, 186, 160), "glow_amber": (255, 178, 70), "dark": (16, 12, 12),
            "slime": (70, 82, 48), "slime_light": (112, 120, 74), "flesh": (96, 108, 98), "seaweed": (40, 58, 36), "teeth": (210, 200, 160),
            "root": (40, 30, 24), "glow_green": (190, 255, 170), "glow_red": (255, 70, 40), "glow_violet": (220, 140, 255), "mud": (64, 52, 38),
            "bark_light": (92, 72, 50), "chitin": (38, 20, 16), "chitin_light": (92, 46, 22), "leg_ochre": (176, 128, 44), "flesh_raw": (122, 40, 36),
            "gore": (70, 14, 14), "feather": (34, 34, 40), "hair": (14, 14, 16), "bone_old": (168, 150, 108), "glow_white": (235, 245, 255),
            "rust_fur": (86, 44, 30), "heather": (112, 60, 104), "gold": (214, 170, 60)}[name]
    streak = [r.uniform(-1, 1) for _ in range(16)]
    for y in range(16):
        for x in range(16):
            if name in GLOW:
                k = 1.0 if 4 <= x <= 11 and 4 <= y <= 11 else 0.85
                c = tuple(clamp(v * k) for v in base); a = 255
            elif name in ("bark", "bark_light", "root"):
                v = 1 + 0.22 * streak[x] + 0.12 * r.uniform(-1, 1) + (0.18 if (x + y // 5) % 7 == 0 else 0) * -1
                c = tuple(clamp(b * v) for b in base); a = 255
            elif name in ("chitin", "chitin_light"):                       # glossy plates: a bright edge on top, dark seams
                v = 1 + 0.1 * r.uniform(-1, 1) + (0.55 if y in (1, 2) else 0) + (-0.4 if x % 8 == 0 else 0)
                c = tuple(clamp(b * v) for b in base); a = 255
            elif name in ("hair", "feather", "rust_fur", "heather"):
                v = 1 + 0.35 * streak[x] + 0.1 * r.uniform(-1, 1)
                c = tuple(clamp(b * v + 6) for b in base); a = 255
            elif name in ("slime", "slime_light"):
                v = 1 + 0.12 * r.uniform(-1, 1) + (0.25 if r.random() < 0.06 else 0)
                c = tuple(clamp(b * v) for b in base); a = 238
            else:
                v = 1 + 0.16 * r.uniform(-1, 1) + (-0.25 if r.random() < 0.08 else 0)
                c = tuple(clamp(b * v) for b in base); a = 255
            t[y][x] = c + (a,)
    return t
atlas = [[(0, 0, 0, 0)] * 128 for _ in range(64)]
for i, n in enumerate(MATS):
    t = tile(n); ox, oy = (i % 8) * 16, (i // 8) * 16
    for y in range(16):
        for x in range(16): atlas[oy + y][ox + x] = t[y][x]
wpng(os.path.join(RP, "textures/item/lab/atlas.png"), atlas)

# ---------------------------------------------------------------- box models
# Boxes are written in the RIG FRAME in pixels (1/16 block) relative to the pivot of the part: +Y up, +Z forward (where the mob looks), +X its left.
# The item display turns its model by 180 degrees around Y, so the model gets x -> -x, z -> -z; "s" shrinks a part that is too long for the
# model limits (-16..32), the display scales it back by 1/s.
def B(x1, y1, z1, x2, y2, z2, mat): return (x1, y1, z1, x2, y2, z2, mat)
def face_uv(mat, w, h):
    i = M[mat]; u0, v0 = (i % 8) * 2, (i // 8) * 4      # uv units: 16 = the whole atlas (128 px wide, 64 px high)
    du, dv = min(abs(w), 16) / 8, min(abs(h), 16) / 4
    return [u0, v0, u0 + max(du, 0.125), v0 + max(dv, 0.25)]
GLOW_RGB = {"glow_amber": (255, 178, 70), "glow_green": (190, 255, 170), "glow_red": (255, 70, 40), "glow_violet": (220, 140, 255), "glow_white": (235, 245, 255)}
def model(name, boxes, s=1.0, frame=True, display=None):
    # two tints (custom_model_data colors): [0] the whole part (white by default; red for a moment when the monster is hurt),
    # [1] the glowing eyes: their texture is white, the tint gives their colour (and a black or white flash when it is hurt)
    els = []; eye = None
    for (x1, y1, z1, x2, y2, z2, mat) in boxes:
        if frame: fx1, fx2, fz1, fz2 = 8 - x2 * s, 8 - x1 * s, 8 - z2 * s, 8 - z1 * s
        else: fx1, fx2, fz1, fz2 = x1, x2, z1, z2
        fy1, fy2 = (8 + y1 * s, 8 + y2 * s) if frame else (y1, y2)
        fr, to = [round(v, 3) for v in (fx1, fy1, fz1)], [round(v, 3) for v in (fx2, fy2, fz2)]
        assert all(-16 <= v <= 32 for v in fr + to), (name, fr, to)
        w, h, d = to[0] - fr[0], to[1] - fr[1], to[2] - fr[2]
        glow = mat in GLOW; tex = "glow_white" if glow else mat
        if glow: eye = eye or GLOW_RGB[mat]
        faces = {f: {"uv": face_uv(tex, *wh), "texture": "#a", "tintindex": 1 if glow else 0} for f, wh in
                 (("north", (w, h)), ("south", (w, h)), ("east", (d, h)), ("west", (d, h)), ("up", (w, d)), ("down", (w, d)))}
        e = {"from": fr, "to": to, "faces": faces}
        if glow: e["light_emission"] = 15; e["shade"] = False
        els.append(e)
    m = {"textures": {"a": "last_ember:item/lab/atlas", "particle": "last_ember:item/lab/atlas"}, "elements": els}
    if display: m["display"] = display
    wjson(os.path.join(RP, f"models/item/lab/{name}.json"), m)
    ec = (eye[0] << 16 | eye[1] << 8 | eye[2]) - (1 << 32) + (255 << 24) if eye else -1   # ARGB as a signed int
    wjson(os.path.join(RP, f"items/lab/{name}.json"), {"model": {"type": "minecraft:model", "model": f"last_ember:item/lab/{name}",
          "tints": [{"type": "minecraft:custom_model_data", "index": 0, "default": -1}, {"type": "minecraft:custom_model_data", "index": 1, "default": ec}]}})
def mirror(boxes): return [B(-x2, y1, z1, -x1, y2, z2, m) for (x1, y1, z1, x2, y2, z2, m) in boxes]

# ---- probe: a nose to the front (+Z of the frame), a glowing cap; to check orientation and the light of the displays
model("probe", [B(-4, 0, -4, 4, 8, 4, "bone"), B(-1, 3, 4, 1, 5, 10, "glow_red"), B(-4, 8, -4, 4, 9, 4, "glow_green"), B(4, 0, -1, 8, 2, 1, "bark")])

# ---- 1. drowner: the head (a head-slot item: model space of a carved pumpkin, the face on the north side)
head = [B(1.5, 2, 1.5, 14.5, 15, 14.5, "flesh"), B(2, 15, 3, 9, 16, 12, "flesh"),                   # skull, a swollen crown
        B(3, 8, 1.1, 7, 11, 1.6, "dark"), B(9.5, 8.5, 1.1, 13, 11.5, 1.6, "dark"),                       # deep sockets, not alike
        B(4.6, 9, 0.9, 5.6, 10, 1.3, "glow_white"), B(10.8, 9.5, 0.9, 11.8, 10.5, 1.3, "glow_white"),   # small pale pupils
        B(7.3, 6.5, 1.1, 8.7, 8, 1.6, "dark"),                                                          # the nose hole
        B(3, -1, 1.0, 13, 5.5, 1.6, "dark"),                                                            # the gaping maw, longer
        B(4, 3.5, 0.7, 5, 5.5, 1.1, "teeth"), B(8, 4, 0.7, 8.8, 5.5, 1.1, "teeth"), B(11, 3, 0.7, 12, 5.5, 1.1, "teeth"),
        B(5.5, -1, 0.7, 6.5, 1.0, 1.1, "teeth"), B(10, -1, 0.7, 10.8, 1.5, 1.1, "teeth"),
        B(3, -6, 0.2, 13, -1, 7, "flesh"), B(3.5, -1.5, 0.1, 12.5, -1, 6.5, "gore"),                     # the lower jaw hangs low
        # long lank black hair: a cap, a curtain down the back, strands hanging over the face down to the chest
        B(1, 14.5, 0.5, 15, 16.4, 15.2, "hair"), B(0.6, -12, 13.8, 15.4, 16, 15.8, "hair"), B(0.3, -9, 2, 1.5, 15.5, 14, "hair"), B(14.5, -10, 2, 15.7, 15.5, 14, "hair"),
        B(1.2, -8, 0.2, 2.6, 15, 0.9, "hair"), B(2.9, -3, 0.1, 3.8, 15, 0.8, "hair"), B(5.6, 2, 0.1, 6.6, 15, 0.8, "hair"),
        B(10, -5, 0.1, 11.1, 15, 0.8, "hair"), B(12.2, -11, 0.2, 13.4, 15, 0.9, "hair"), B(13.6, -6, 0.2, 14.8, 15, 0.9, "hair"),
        B(0.8, 6, 6, 1.5, 11, 6.6, "dark"), B(14.5, 6, 8, 15.2, 11, 8.6, "dark")]                        # gills
model("drowner_head", head, frame=False, display={"head": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]}})


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

# ---- 5. scolopendra: a head with venom claws and a cluster of eyes, body segments with ochre legs in two phases of the step, a tail
def legs(z, foot, side):  # one leg: out from the side, down to the ground with the foot at z+foot
    x0, x1 = (7, 13) if side > 0 else (-13, -7); lx0, lx1 = (12, 13.2) if side > 0 else (-13.2, -12)
    return [B(x0, 5, z, x1, 6.2, z + 1.2, "leg_ochre"), B(lx0, 0, z + foot, lx1, 5, z + foot + 1.2, "leg_ochre")]
def seg(phase):
    b = [B(-7, 2, -6, 7, 8, 6, "chitin"), B(-6, 8, -5, 6, 9.2, 5, "chitin_light"), B(-6.5, 2.5, 5.6, 6.5, 7.5, 6.3, "dark"),
         B(5, 9, 0, 6.5, 11, 1.5, "chitin_light"), B(-6.5, 9, -2, -5, 10.5, -0.5, "chitin_light")]
    f = 1.6 if phase == 0 else -1.6
    return b + legs(2, f, 1) + legs(-3.2, -f, 1) + legs(2, -f, -1) + legs(-3.2, f, -1)
model("cent_seg_a", seg(0)); model("cent_seg_b", seg(1))
chead = [B(-6, 2, -5, 6, 7.5, 5, "chitin"), B(-5, 7.5, -4, 5, 8.5, 4, "chitin_light"), B(-4, 2.5, 4.9, 4, 6, 5.3, "dark"),
         B(2, 6, 5, 3, 7, 5.4, "glow_red"), B(3.4, 5.4, 4.6, 4.2, 6.2, 5.0, "glow_red"), B(-3, 6, 5, -2, 7, 5.4, "glow_red"), B(-4.2, 5.4, 4.6, -3.4, 6.2, 5.0, "glow_red"),
         B(0.6, 6.6, 5.1, 1.2, 7.2, 5.4, "glow_red"),
         B(3.6, 1, 4.4, 5.6, 3, 5.4, "chitin_light"), B(-5.6, 1, 4.4, -3.6, 3, 5.4, "chitin_light"),                                       # sockets of the venom claws
         B(2.8, 6.4, 4.4, 3.8, 7.4, 5.4, "chitin_light"), B(-3.8, 6.4, 4.4, -2.8, 7.4, 5.4, "chitin_light")] \
        + legs(-3, 1.6, 1) + legs(-3, -1.6, -1)
# the feelers are their own parts (they twitch): crooked and not alike, each with kinks and a hooked tip (Edward: not like aerials)
model("cent_ant_l", [B(-0.35, -0.35, 0, 0.35, 0.35, 3.5, "leg_ochre"), B(0.1, 0.0, 3.2, 0.8, 0.7, 6.5, "leg_ochre"), B(0.6, 0.6, 6.2, 1.2, 1.2, 8.8, "leg_ochre"),
                     B(0.9, 0.1, 8.5, 1.5, 0.7, 11.0, "leg_ochre"), B(1.3, 0.5, 10.7, 1.8, 1.0, 12.8, "leg_ochre"), B(1.0, 1.0, 12.5, 1.5, 2.6, 13.0, "chitin_light"),
                     B(0.6, 2.3, 12.6, 1.1, 2.8, 14.2, "chitin_light")])
model("cent_ant_r", [B(-0.35, -0.35, 0, 0.35, 0.35, 3.0, "leg_ochre"), B(-0.9, 0.2, 2.8, -0.2, 0.9, 5.8, "leg_ochre"), B(-1.3, 0.8, 5.5, -0.7, 1.4, 7.0, "leg_ochre"),
                     B(-1.2, 1.3, 6.8, -0.6, 3.0, 7.4, "leg_ochre"), B(-1.6, 2.8, 7.0, -1.0, 3.4, 10.0, "leg_ochre"), B(-2.2, 2.2, 9.8, -1.6, 2.8, 12.2, "leg_ochre"),
                     B(-2.6, 1.6, 12.0, -2.1, 2.2, 14.5, "chitin_light"), B(-2.9, 2.0, 14.3, -2.5, 2.5, 15.8, "chitin_light")])
model("cent_head", chead)
# the venom claws are their own parts (they chew and snap); a wider gap between their tips (Edward: from afar they looked like a zipped lace)
claw = [B(-1.2, -1, 0, 1.2, 1.2, 4, "chitin_light"), B(-2, -0.9, 3.5, 0.6, 0.9, 6.5, "chitin_light"), B(-2.8, -0.8, 6, -0.8, 0.6, 8, "dark"), B(-3.2, -0.6, 7.5, -2.0, 0.3, 9.2, "dark")]
model("cent_claw_l", claw); model("cent_claw_r", mirror(claw))
model("cent_tail", [B(-5, 2, -5, 5, 7, 5, "chitin"), B(-4, 7, -4, 4, 8, 4, "chitin_light"), B(4, 3, -5, 5, 4, -15, "leg_ochre"), B(-5, 3, -5, -4, 4, -15, "leg_ochre"),
                    B(4.5, 0, -15, 5.5, 4, -14, "leg_ochre"), B(-5.5, 0, -15, -4.5, 4, -14, "leg_ochre")] + legs(0, 1.6, 1) + legs(0, -1.6, -1))

# ---- 4. leshy: seven parts (pivots in the rig below)
# the torso: the right side thinner, heavy moss on the left shoulder only, a branch grows out of the right one; the chest is torn open:
# ribs whole on the left and broken on the right, the ember deep inside, roots spilling out; an animal skull and a dead bird hang on root strings
torso = [B(-6, 0, -4, 7, 19, 4, "bark"), B(7, 2, -3, 8.5, 12, 2, "root"),
         B(1, 15, -5, 9.5, 21, 5, "moss"), B(-6, 18, -3, 1, 20, 3, "moss"), B(-9, 16, -1, -6, 17.5, 1, "bark_light"), B(-11, 17.5, -1, -9.5, 21, 0.5, "bark_light"),
         B(-4, 7, 3.9, 4.5, 14.5, 4.1, "dark"), B(-1.5, 8.5, 3.6, 2.5, 12.5, 4.2, "glow_amber"),
         B(0, 13, 4, 6, 14, 5, "bone"), B(0, 10.5, 4, 6.5, 11.5, 5, "bone"), B(0, 8, 4, 5.5, 9, 5, "bone"),
         B(-5, 13, 4, -1.5, 14, 5, "bone"), B(-5.5, 8, 4, -3, 9, 5, "bone"), B(-4, 5.5, 4.2, -3, 10, 5, "bone"),
         B(-2, 1, 4, -1, 8, 5, "root"), B(1.5, 0, 4, 2.5, 7, 5.2, "root"),
         B(-5.5, 4, 4.5, -5, 9, 5, "root"), B(-7, 0.5, 4.2, -4, 4, 7, "bone_old"), B(-6.6, 2, 6.9, -6, 2.8, 7.2, "dark"), B(-5, 2, 6.9, -4.4, 2.8, 7.2, "dark"),
         B(4, 2, 4.2, 4.5, 6, 4.7, "root"), B(3, -2, 4, 5.5, 2, 6, "feather"), B(5.5, -3, 4, 6.5, 1, 5, "feather"), B(3.6, -3.5, 4.5, 4.4, -2, 5.3, "bone_old"),
         B(6, 4, -4.5, 7, 15, -3.5, "moss"), B(-3, -3, -4.5, -2, 9, -3.5, "moss"), B(5, 3, 4, 6, 15, 4.6, "moss"), B(0, 2.5, 4.2, 0.8, 5, 4.8, "bone")]
# the head: a long crooked skull, sockets not alike, the jaw a little open; antlers NOT alike (Edward: a symmetric deer skull looked funny):
# the left one big and branching outward and back, the right one broken off with moss hanging from the stump
lhead = [B(-2, 0, -1.5, 2, 3, 2, "bark"), B(-3.5, 4, -3, 3.5, 10, 3.5, "bone"), B(-3.8, 8, 2.5, 3.8, 9.5, 4, "bone"),
         B(-2.5, 6, 3.5, 2.5, 8.5, 12, "bone"), B(-2.2, 5.2, 3.5, 2.2, 6, 11.5, "gore"),                  # the upper muzzle, the raw palate
         B(1.6, 3.4, 5, 2.3, 6, 5.7, "teeth"), B(1.6, 2.8, 7, 2.3, 6, 7.7, "teeth"), B(1.6, 3.8, 9, 2.3, 6, 9.7, "teeth"),   # fangs hanging down, not alike
         B(-2.3, 3.0, 4.5, -1.6, 6, 5.2, "teeth"), B(-2.3, 4.0, 6.5, -1.6, 6, 7.2, "teeth"), B(-2.3, 2.5, 8.5, -1.6, 6, 9.2, "teeth"),
         B(-1, 2.5, 11.2, -0.2, 6, 11.8, "teeth"), B(0.5, 3.2, 11.2, 1.3, 6, 11.8, "teeth"),
         B(1.3, 7, 3.6, 3.6, 9.4, 3.9, "dark"), B(-3.2, 7.4, 3.6, -1.5, 9, 3.9, "dark"),                  # sockets: the left one bigger
         B(2, 7.8, 3.9, 3, 8.8, 4.1, "glow_amber"), B(-2.6, 7.9, 3.9, -2.0, 8.5, 4.1, "glow_amber"),
         B(-4, 4, -3.2, -3.4, 9, 2, "moss"), B(-3.5, 10, -3, 0, 10.7, 2, "moss"),
         # the left antler
         B(2.5, 9, -1.5, 4, 13, 0, "bone"), B(4, 12, -1.5, 8, 13.4, 0, "bone"), B(6.5, 13.4, -1.5, 7.8, 21, 0, "bone"),
         B(8, 11.5, -1.5, 13, 12.8, 0, "bone"), B(11.5, 12.8, -1.5, 12.7, 17, 0, "bone"), B(5, 13.4, 0, 6.2, 17, 3.5, "bone"),
         B(7.8, 17, -4, 9, 18.2, -1.5, "bone"), B(6.5, 21, -1.5, 10, 22.2, 0, "bone"),
         # the right antler, broken; moss hangs from the stump, a root twig is wound round it
         B(-4, 9, -1.5, -2.5, 12.5, 0, "bone"), B(-6.5, 11.5, -1.5, -4, 12.8, 0, "bone"), B(-6.5, 12.8, -1.5, -5.5, 14, 0, "bone"),
         B(-6.3, 6, -1, -5.7, 11.5, -0.4, "moss"), B(-7, 10.8, -2, -3.5, 11.3, 0.5, "root")]
arm = [B(-2, -14, -2, 2, 0, 2, "bark"), B(-2.5, -3, -2.5, 2.5, 1.5, 2.5, "moss"), B(-1.5, -26, -1.5, 1.5, -14, 1.5, "bark"),
       B(-2, -31, -0.5, -1, -26, 1.5, "root"), B(-0.5, -32, 0, 0.5, -26, 2, "root"), B(1, -31, -0.5, 2, -26, 1.5, "root"), B(-1.6, -20, -1.6, 1.6, -18, 1.6, "moss")]
leg = [B(-2.5, -21, -2.5, 2.5, 0, 2.5, "bark"), B(-3.5, -21, -3, 3.5, -19, 5, "root"), B(-1, -21, 5, 1, -20, 8, "root"), B(-3, -10, -3, 3, -8, 3, "moss")]
if os.environ.get("LAB_PROBE"):   # debugging: every element of the arm alone
    for i, b in enumerate(arm): model(f"probe_arm{i}", [b], s=0.72)
    model("probe_arm_s1", [B(-2, -14, -2, 2, 0, 2, "bark")])
ljaw = [B(-2.2, -2, 0, 2.2, 0, 8.5, "bone_old"), B(-1.9, -0.1, 0.5, 1.9, 0.2, 8, "gore"),           # the lower jaw (pivot at its hinge)
        B(1.4, 0, 2, 2, 2, 2.6, "teeth"), B(1.4, 0, 5, 2, 1.6, 5.6, "teeth"), B(-2, 0, 3.5, -1.4, 2.2, 4.1, "teeth"), B(-2, 0, 6.5, -1.4, 1.5, 7.1, "teeth"),
        B(-0.5, 0, 7.8, 0.4, 2.6, 8.4, "teeth"), B(1, -4.5, 7, 1.5, -2, 7.5, "moss"), B(-0.6, -3, 5.5, 0.4, -2, 6.5, "gore")]
model("leshy_jaw", ljaw)
gtorso = torso + [B(-3.5, 9, -4.6, 2.5, 16, -4, "dark"), B(-2.5, 10, -4.4, 1.5, 15, -3.8, "glow_amber"), B(-4.5, 8, -4.8, 3.5, 9, -4.2, "root"), B(-4.5, 16, -4.8, 3.5, 17, -4.2, "root"),
                  B(-6, 14, -5, -3.5, 17, -4.2, "moss"), B(2.5, 7, -5.2, 4, 18, -4.3, "bark_light")]   # T-020: the glowing hollow in the back (the weak place)
model("grove_torso", gtorso)
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
        # starved: ribs show through the hide on both flanks (the body box: sides at x 18-23 and 30-35, rows 20-28 along the body)
        if (18 <= x <= 23 or 30 <= x <= 35) and y in (21, 23, 25) and r.random() < 0.85: c = [150, 140, 118]
        if (18 <= x <= 23 or 30 <= x <= 35) and y in (22, 24, 26): c = [v * 0.55 for v in c]
        if 24 <= x <= 29 and 20 <= y <= 28 and x in (26, 27) and y % 2 == 0: c = [140, 128, 104]     # the spine
        if 18 <= x <= 41 and 26 <= y <= 28 and r.random() < 0.18: c = [96, 14, 12]                  # raw sores
        # red eyes (the front of the head: x 4-9, row 6 under the brows), the same red as its glowing eyes in the bushes (Edward)
        if y == 6 and x in (4, 5, 8, 9): c = [235, 40, 28] if x in (5, 8) else [150, 18, 14]
        row.append(tuple(clamp(v) for v in c) + (255,))
    warg.append(row)
for k in ("", "_angry", "_tame", "_baby", "_angry_baby", "_tame_baby"): wpng(os.path.join(RP, f"textures/entity/wolf/lab_warg{k}.png"), warg)
wjson(os.path.join(DP, "wolf_variant/lab_warg.json"), {"assets": {"angry": "last_ember:entity/wolf/lab_warg_angry", "tame": "last_ember:entity/wolf/lab_warg_tame", "wild": "last_ember:entity/wolf/lab_warg"},
      "baby_assets": {"angry": "last_ember:entity/wolf/lab_warg_angry_baby", "tame": "last_ember:entity/wolf/lab_warg_tame_baby", "wild": "last_ember:entity/wolf/lab_warg_baby"},
      "spawn_conditions": []})

# ---------------------------------------------------------------- rigs (4. the leshy, 2. the warg)
# Rig frame: blocks, origin at the feet of the carrier. Every part rides the carrier, so its display origin is the passenger point (0, pass_y, 0).
# passenger points measured in 26.3 (display Pos - mob Pos): husk scale 1.6 -> 3.32, slime Size:2 -> 1.513, wolf scale 1.7 -> 1.392, silverfish scale 3 -> 0.7125.
# The item display shows the model turned by 180 degrees: the +Z of the rig frame is the side the display looks at (checked with lab/probe).
def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx, aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)
def qaxis(ax, deg):
    t = math.radians(deg) / 2; s_ = math.sin(t)
    return {"x": (s_, 0, 0, math.cos(t)), "y": (0, s_, 0, math.cos(t)), "z": (0, 0, s_, math.cos(t))}[ax]
def qeul(p, yw, rl): return qmul(qmul(qaxis("y", yw), qaxis("x", p)), qaxis("z", rl))   # yaw, then pitch, then roll
def qrot(q, v):
    x, y, z, w_ = q; vq = (v[0], v[1], v[2], 0); qi = (-x, -y, -z, w_)
    r_ = qmul(qmul(q, vq), qi); return (r_[0], r_[1], r_[2])
def merge(t, q, s, dur):
    f = lambda v: round(v, 4)
    return ("{start_interpolation:0,interpolation_duration:%d,transformation:{translation:[%sf,%sf,%sf],left_rotation:[%sf,%sf,%sf,%sf],scale:[%sf,%sf,%sf],right_rotation:[0f,0f,0f,1f]}}"
            % (dur, f(t[0]), f(t[1]), f(t[2]), f(q[0]), f(q[1]), f(q[2]), f(q[3]), f(s), f(s), f(s)))
LOOKS = list(range(-60, 61, 10))   # le.llook = index 0..12 (6 = straight)
gd = os.path.join(DP, "function/lab/gen")
if os.path.isdir(gd): shutil.rmtree(gd)
def make_rig(rig, tag, parts, models, scales, pass_y, poses, look_parts, look_poses, size=1.0):
    """parts: ordered {part: (parent, pivot in blocks in the parent's frame)}; poses: {name: {part: (pitch, yaw, roll)}, 'root': (p, y, r, dy), 'scale': k}.
    Writes lab/gen/<rig>_pose_<p> (macro d = ticks; as the carrier), lab/gen/<rig>_head_<p> (the look parts turned by le.llook),
    lab/gen/<rig>_parts (storage last_ember:lab <rig>_parts: the passengers to summon the carrier with)."""
    def solve(pose, look=0.0):
        rp = pose.get("root", (0, 0, 0, 0)); k = pose.get("scale", 1.0)
        world = {"root": ((0, rp[3], 0), qeul(rp[0], rp[1], rp[2]))}; out = {}
        for part, (par, piv) in parts.items():
            pt, pq = world[par]
            pos = tuple(a + b for a, b in zip(pt, qrot(pq, piv)))
            q = qmul(pq, qeul(*pose.get(part, (0, 0, 0))))
            if part == look_parts[0]: q = qmul(q, qaxis("y", look))
            world[part] = (pos, q)
            out[part] = ((pos[0] * k * size, pos[1] * k * size - pass_y, pos[2] * k * size), q, k * size * scales.get(part, 1.0))
        return out
    for name, pose in poses.items():
        lines = [f"# GENERATED by tools/gen_lab.py: the pose {name} of the {rig} (as the carrier, macro d = ticks)"]
        sol = solve(pose)
        for part in parts:
            if part in look_parts: continue
            t, q, sc = sol[part]
            lines.append(f"$execute on passengers if entity @s[tag={tag}{part}] run data merge entity @s " + merge(t, q, sc, 0).replace("interpolation_duration:0", "interpolation_duration:$(d)"))
        lines.append(f"function last_ember:lab/gen/{rig}_head_{name} with storage last_ember:lab anim")
        wtext(os.path.join(gd, f"{rig}_pose_{name}.mcfunction"), "\n".join(lines) + "\n")
        hl = [f"# GENERATED: the head of the {rig} in the pose {name}, turned by the look index le.llook"]
        for i, lk in enumerate(LOOKS):
            so = solve(pose, lk if name.startswith(look_poses) else 0)
            for part in look_parts:
                t, q, sc = so[part]
                hl.append(f"$execute if score @s le.llook matches {i} on passengers if entity @s[tag={tag}{part}] run data merge entity @s " + merge(t, q, sc, 0).replace("interpolation_duration:0", "interpolation_duration:$(d)"))
        wtext(os.path.join(gd, f"{rig}_head_{name}.mcfunction"), "\n".join(hl) + "\n")
    rest = solve(poses[next(iter(poses))]); summ = []
    for part in parts:
        t, q, sc = rest[part]; tr = merge(t, q, sc, 0)[1:-1].split("transformation:")[1]
        summ.append('{id:"minecraft:item_display",Tags:["le.lab_part","%s%s"],teleport_duration:3,view_range:1.5f,item_display:"none",item:{id:"minecraft:stick",count:1,components:{"minecraft:item_model":"last_ember:lab/%s"}},transformation:%s}' % (tag, part, models[part], tr))
    wtext(os.path.join(gd, f"{rig}_parts.mcfunction"), f"# GENERATED: the parts of the {rig} at rest (the passengers the carrier is summoned with)\ndata modify storage last_ember:lab {rig}_parts set value [" + ",".join(summ) + "]\n")

# ---- 4. the leshy: an invisible husk of scale 1.6, 7 parts
ARM_S = 0.72
# roll of an arm: + moves the left arm (+X) outward, - the right one. Walking it spreads its long arms wide to the sides (Edward: not a golem).
# It strikes with the right and the left arm in turn (windup/strike and windup_l/strike_l).
LESHY_POSES = {
    "idle0": {"torso": (3, 0, 0), "arm_l": (4, 0, 14), "arm_r": (4, 0, -14), "head": (-4, 0, 0), "jaw": (22, 0, 0)},
    "idle1": {"torso": (-1, 0, 0), "arm_l": (-2, 0, 19), "arm_r": (-2, 0, -19), "head": (2, 0, 0), "jaw": (32, 0, 0), "root": (0, 0, 0, 0.03)},
    "walk0": {"leg_l": (-24, 0, 0), "leg_r": (22, 0, 0), "arm_l": (18, 0, 38), "arm_r": (-20, 0, -46), "torso": (6, -6, 0), "jaw": (26, 0, 0), "root": (0, 0, 0, -0.06)},
    "walk1": {"leg_l": (0, 0, 0), "leg_r": (0, 0, 0), "arm_l": (0, 0, 48), "arm_r": (0, 0, -48), "torso": (5, 0, 0), "jaw": (32, 0, 0), "root": (0, 0, 0, 0.04)},
    "walk2": {"leg_l": (22, 0, 0), "leg_r": (-24, 0, 0), "arm_l": (-20, 0, 46), "arm_r": (18, 0, -38), "torso": (6, 6, 0), "jaw": (26, 0, 0), "root": (0, 0, 0, -0.06)},
    "walk3": {"leg_l": (0, 0, 0), "leg_r": (0, 0, 0), "arm_l": (0, 0, 48), "arm_r": (0, 0, -48), "torso": (5, 0, 0), "jaw": (32, 0, 0), "root": (0, 0, 0, 0.04)},
    "windup": {"torso": (-12, 24, 0), "arm_r": (-165, 0, 15), "arm_l": (-30, 0, 35), "head": (-18, 0, 0), "jaw": (62, 0, 0), "leg_l": (-10, 0, 0), "leg_r": (8, 0, 0)},
    "strike": {"torso": (24, -18, 0), "arm_r": (-25, 0, 0), "arm_l": (10, 0, 30), "head": (10, 0, 0), "jaw": (14, 0, 0), "leg_l": (-16, 0, 0), "leg_r": (14, 0, 0), "root": (0, 0, 0, -0.1)},
    "windup_l": {"torso": (-12, -24, 0), "arm_l": (-165, 0, -15), "arm_r": (-30, 0, -35), "head": (-18, 0, 0), "jaw": (62, 0, 0), "leg_r": (-10, 0, 0), "leg_l": (8, 0, 0)},
    "strike_l": {"torso": (24, 18, 0), "arm_l": (-25, 0, 0), "arm_r": (10, 0, -30), "head": (10, 0, 0), "jaw": (14, 0, 0), "leg_r": (-16, 0, 0), "leg_l": (14, 0, 0), "root": (0, 0, 0, -0.1)},
    "rise0": {"root": (0, 0, 0, -4.8), "torso": (30, 0, 0), "arm_l": (-160, 0, 20), "arm_r": (-160, 0, -20), "head": (40, 0, 0), "jaw": (50, 0, 0)},
    "rise1": {"root": (0, 0, 0, -1.4), "torso": (20, 0, 0), "arm_l": (-150, 0, 30), "arm_r": (-150, 0, -30), "head": (-30, 0, 0), "jaw": (60, 0, 0)},
    "rise2": {"torso": (-10, 0, 0), "arm_l": (-40, 0, 50), "arm_r": (-40, 0, -50), "head": (-25, 0, 0), "jaw": (62, 0, 0)},
    "die0": {"torso": (-16, 0, 6), "head": (-35, 0, 0), "jaw": (60, 0, 0), "arm_l": (-50, 0, 50), "arm_r": (-60, 0, -45), "leg_l": (6, 0, 0)},
    # T-020: the grove leshy stands as a tree (arms up and apart like branches, head bowed into the crown, legs together as a trunk) until it is touched
    "tree": {"torso": (-3, 0, 2), "arm_l": (-172, 8, 28), "arm_r": (-168, -6, -36), "head": (24, 0, 12), "jaw": (4, 0, 0)},
    "tree_shake": {"torso": (4, 4, -3), "arm_l": (-150, 14, 40), "arm_r": (-158, -10, -24), "head": (10, 8, -8), "jaw": (30, 0, 0), "root": (0, 0, 0, 0.05)},
    "die1": {"root": (0, 0, 0, -0.55), "torso": (34, 0, -6), "head": (20, 0, 10), "jaw": (40, 0, 0), "arm_l": (-10, 0, 20), "arm_r": (5, 0, -25), "leg_l": (-30, 0, 4), "leg_r": (-40, 0, -4)},
    "die2": {"root": (80, 0, 0, -0.35), "torso": (8, 0, -4), "head": (30, 25, 20), "jaw": (50, 0, 0), "arm_l": (-70, 0, 60), "arm_r": (-80, 0, -30), "leg_l": (-10, 0, 8), "leg_r": (-5, 0, -6)},
    "die3": {"root": (80, 0, 0, -0.75), "torso": (8, 0, -4), "head": (30, 25, 20), "jaw": (50, 0, 0), "arm_l": (-70, 0, 60), "arm_r": (-80, 0, -30), "leg_l": (-10, 0, 8), "leg_r": (-5, 0, -6), "scale": 0.0},
}
make_rig("leshy", "le.lp_",
         {"torso": ("root", (0, 1.3, 0)), "head": ("torso", (0, 1.19, 0.05)), "jaw": ("head", (0, 0.33, 0.22)), "arm_l": ("torso", (0.56, 1.06, 0)),
          "arm_r": ("torso", (-0.56, 1.06, 0)), "leg_l": ("root", (0.28, 1.3, 0)), "leg_r": ("root", (-0.28, 1.3, 0))},
         {"torso": "leshy_torso", "head": "leshy_head", "jaw": "leshy_jaw", "arm_l": "leshy_arm", "arm_r": "leshy_arm", "leg_l": "leshy_leg", "leg_r": "leshy_leg"},
         {"arm_l": 1 / ARM_S, "arm_r": 1 / ARM_S}, 3.32, LESHY_POSES, ("head", "jaw"), ("idle", "walk"))

# ---- 2. the warg (second version, after Edward: "just a big vanilla wolf"): an invisible wolf of scale 1.9 (the rig is drawn for 1.7 and grown by 1.9/1.7) (its AI, anger and bite stay vanilla)
# carries a rig of 8 parts: a gaunt body with a shaggy mane, ribs and spine showing, a long skull with an open maw and glowing red eyes,
# a lower jaw of its own, four long thin legs, a ragged tail. Galloping, biting (the jaw snaps), crouching in the bushes, leaping, dying.
wtorso = [B(-6.5, -4, -6, 6.5, 7.5, 6, "hair"), B(-5, -5, -16, 5, 4, -6, "feather"), B(-4.5, -4, -26, 4.5, 3.5, -16, "hair"),
          B(5, -4, -8, 5.4, 3, -7, "bone_old"), B(5, -4, -10.5, 5.4, 3, -9.5, "bone_old"), B(5, -4, -13, 5.4, 3, -12, "bone_old"),
          B(-5.4, -4, -8, -5, 3, -7, "bone_old"), B(-5.4, -4, -13, -5, 3, -12, "bone_old"),
          B(-0.8, 4, -15, 0.8, 6, -13, "bone_old"), B(-0.8, 4, -11, 0.8, 6.5, -9, "bone_old"), B(-1.5, 7.5, -5, 1.5, 10, -2, "hair"), B(-1, 7.5, 0, 1, 9, 3, "hair"),
          B(5.4, -1, -21, 5.7, 1, -19, "gore"), B(-4.8, -3, -25, -4.5, -1.5, -23, "gore"), B(-3, -5.6, -14, 3, -5, -7, "gore")]
whead = [B(-2.5, -2.5, 0, 2.5, 2.5, 4, "hair"), B(-3.5, -2.5, 3, 3.5, 3.5, 10, "hair"), B(-2.2, -1, 10, 2.2, 1.8, 18, "feather"),
         B(-1.2, 0.6, 17.5, 1.2, 1.8, 18.5, "dark"), B(-2, -1.2, 10.5, 2, -0.8, 17.5, "gore"),
         B(1.4, -3.2, 15.5, 2, -1, 16.2, "teeth"), B(-2, -3.6, 15, -1.4, -1, 15.7, "teeth"), B(1.5, -1.9, 11, 2, -1, 14, "teeth"), B(-2, -1.9, 12, -1.5, -1, 14.5, "teeth"),
         B(-3.8, 2.2, 9, 3.8, 3.5, 10.5, "hair"), B(2.3, 1.0, 9.5, 3.6, 2.2, 10.1, "glow_red"), B(-3.6, 1.0, 9.5, -2.3, 2.2, 10.1, "glow_red"),
         B(1.8, 3.5, 4, 3.2, 7.5, 5.5, "hair"), B(-3.2, 3.5, 4, -1.8, 5.5, 5.5, "hair"), B(-3.9, -1, 4, -3.5, 2, 8, "gore")]
wjaw = [B(-2, -1.8, 0, 2, 0, 8, "feather"), B(-1.5, -0.1, 0.5, 1.5, 0.3, 7.2, "gore"),
        B(1.3, 0, 5, 1.9, 1.5, 5.6, "teeth"), B(-1.9, 0, 6.2, -1.3, 1.7, 6.8, "teeth"), B(1.3, 0, 2, 1.9, 0.8, 4, "teeth"), B(-1.9, 0, 2.5, -1.3, 0.8, 4.5, "teeth"),
        B(-0.6, -3, 3, 0.6, -1.8, 4, "gore")]
wfleg = [B(-1.6, -9, -1.6, 1.6, 1, 1.6, "hair"), B(-1, -15, -1, 1, -9, 1, "feather"), B(-1.4, -15, -1.2, 1.4, -14, 2.6, "dark"),
         B(-1.2, -15, 2.6, -0.6, -14.4, 3.6, "bone_old"), B(0.6, -15, 2.6, 1.2, -14.4, 3.6, "bone_old")]
wbleg = [B(-2, -8, -2, 2, 1.5, 2, "hair"), B(-1, -15, -1.5, 1, -8, 0.5, "feather"), B(-1.4, -15, -1.2, 1.4, -14, 2.6, "dark"),
         B(-1.2, -15, 2.6, -0.6, -14.4, 3.4, "bone_old"), B(0.6, -15, 2.6, 1.2, -14.4, 3.4, "bone_old")]
wtail = [B(-1, -1, -6, 1, 1, 0, "hair"), B(-0.7, -0.7, -12, 0.7, 0.7, -6, "hair"), B(-0.4, -0.4, -14, 0.4, 0.4, -12, "feather")]
# the torso is too long for the model limits: shrunk, the display scales it back
model("warg_torso", wtorso, s=0.75); model("warg_head", whead); model("warg_jaw", wjaw); model("warg_fleg", wfleg); model("warg_bleg", wbleg); model("warg_tail", wtail)
# T-020: the heath wolf (the cursed miller's son): the same skeleton and poses as the warg, its own look: rust-red fur with heather in the mane,
# a heavy shaggy collar, amber eyes (not the warg's red), a gold ring on the left fore paw, a shorter, more human brow
def recolour(boxes, m): return [B(*b[:6], m.get(b[6], b[6])) for b in boxes]
HM = {"hair": "rust_fur", "feather": "rust_fur", "glow_red": "glow_amber"}
htorso = recolour(wtorso, HM) + [B(-7.5, -5, -1, 7.5, 9.5, 6.5, "rust_fur"), B(-6, 9, 0, -4.5, 12, 1.5, "heather"), B(3, 9.5, 2, 4.5, 12.5, 3.5, "heather"),
                                 B(-1, 10, -3, 0.5, 12, -1.5, "heather"), B(5.5, 2, 2, 7.8, 5, 4, "heather")]
hhead = recolour(whead, HM) + [B(-3.8, 3.5, 6, 3.8, 4.8, 9.5, "rust_fur"), B(-4.2, -2.5, 3, -3.6, 3, 9, "rust_fur"), B(3.6, -2.5, 3, 4.2, 3, 9, "rust_fur")]
hfleg = recolour(wfleg, HM) + [B(-1.4, -12, -1.4, 1.4, -11, 1.4, "gold")]
model("heath_torso", htorso, s=0.75); model("heath_head", hhead); model("heath_jaw", recolour(wjaw, HM)); model("heath_fleg", hfleg); model("heath_flegr", recolour(wfleg, HM))
model("heath_bleg", recolour(wbleg, HM)); model("heath_tail", recolour(wtail, HM))
WARG_POSES = {
    "idle0": {"head": (8, 0, 0), "jaw": (18, 0, 0), "tail": (-40, 0, 0)},
    "idle1": {"head": (4, 0, 0), "jaw": (28, 0, 0), "tail": (-35, 8, 0), "torso": (-2, 0, 0), "root": (0, 0, 0, 0.02)},
    "run0": {"leg_fl": (-38, 0, 0), "leg_fr": (-28, 0, 0), "leg_bl": (32, 0, 0), "leg_br": (40, 0, 0), "torso": (4, 0, 0), "head": (12, 0, 0), "jaw": (32, 0, 0), "tail": (-12, 0, 0), "root": (0, 0, 0, -0.03)},
    "run1": {"leg_fl": (22, 0, 0), "leg_fr": (30, 0, 0), "leg_bl": (-28, 0, 0), "leg_br": (-20, 0, 0), "torso": (-6, 0, 0), "head": (2, 0, 0), "jaw": (22, 0, 0), "tail": (-25, 0, 0), "root": (0, 0, 0, 0.07)},
    "run2": {"leg_fl": (-30, 0, 0), "leg_fr": (-38, 0, 0), "leg_bl": (40, 0, 0), "leg_br": (32, 0, 0), "torso": (4, 0, 0), "head": (12, 0, 0), "jaw": (34, 0, 0), "tail": (-10, 6, 0), "root": (0, 0, 0, -0.03)},
    "run3": {"leg_fl": (30, 0, 0), "leg_fr": (22, 0, 0), "leg_bl": (-20, 0, 0), "leg_br": (-28, 0, 0), "torso": (-6, 0, 0), "head": (2, 0, 0), "jaw": (24, 0, 0), "tail": (-25, -6, 0), "root": (0, 0, 0, 0.07)},
    "bite0": {"head": (-25, 0, 0), "jaw": (65, 0, 0), "torso": (-8, 0, 0), "leg_fl": (-15, 0, 0), "leg_fr": (-10, 0, 0), "tail": (-5, 0, 0)},
    "bite1": {"head": (22, 0, 0), "jaw": (4, 0, 0), "torso": (10, 0, 0), "leg_bl": (15, 0, 0), "leg_br": (18, 0, 0), "tail": (-5, 0, 0), "root": (0, 0, 0, -0.06)},
    "crouch": {"root": (0, 0, 0, -0.32), "torso": (6, 0, 0), "head": (18, 0, 0), "jaw": (36, 0, 0), "tail": (-60, 0, 0), "leg_fl": (-40, 0, 0), "leg_fr": (-40, 0, 0), "leg_bl": (40, 0, 0), "leg_br": (40, 0, 0)},
    "leap": {"leg_fl": (-65, 0, 0), "leg_fr": (-58, 0, 0), "leg_bl": (55, 0, 0), "leg_br": (62, 0, 0), "torso": (-14, 0, 0), "head": (-6, 0, 0), "jaw": (60, 0, 0), "tail": (5, 0, 0)},
    "die0": {"head": (-35, 0, 0), "jaw": (62, 0, 0), "torso": (-10, 0, 14), "leg_fl": (-20, 0, 15), "leg_br": (25, 0, -10), "tail": (-50, 0, 0)},
    "die1": {"root": (0, 0, 82, 0.28), "head": (14, 12, 0), "jaw": (48, 0, 0), "torso": (0, 0, 0), "leg_fl": (-22, 0, 8), "leg_fr": (-8, 0, -6), "leg_bl": (24, 0, 6), "leg_br": (10, 0, -8), "tail": (-15, 0, 0)},
}
make_rig("warg", "le.wp_",
         {"torso": ("root", (0, 0.98, 0.5)), "head": ("torso", (0, 0.12, 0.38)), "jaw": ("head", (0, -0.13, 0.62)), "tail": ("torso", (0, 0.12, -1.6)),
          "leg_fl": ("root", (0.3, 0.92, 0.35)), "leg_fr": ("root", (-0.3, 0.92, 0.35)), "leg_bl": ("root", (0.27, 0.92, -1.0)), "leg_br": ("root", (-0.27, 0.92, -1.0))},
         {"torso": "warg_torso", "head": "warg_head", "jaw": "warg_jaw", "tail": "warg_tail", "leg_fl": "warg_fleg", "leg_fr": "warg_fleg", "leg_bl": "warg_bleg", "leg_br": "warg_bleg"},
         {"torso": 1 / 0.75}, 1.392 * 1.9 / 1.7, WARG_POSES, ("head", "jaw"), ("idle", "run"), size=1.9 / 1.7)

# ---------------------------------------------------------------- 5. the scolopendra: body segments that follow the path of the head
# The carrier (an invisible silverfish, the head rides it) leaves a path: a marker le.cmark (same le.lnk) keeps points every 0.25 block in data.h
# (newest first); segment k stands on point 3+4k and faces point 1+4k; its hit box (interaction le.cb<k>) goes with it.
NSEG = 10
SCALES = [1.5, 1.5, 1.45, 1.4, 1.35, 1.3, 1.25, 1.2, 1.12, 1.1]
cl = ["# GENERATED: as the path marker after a new point: every segment to its point of the path (ch = the path)"]
for k in range(NSEG):
    i, j = 3 + 4 * k, 1 + 4 * k
    cl += [f"execute unless data storage last_ember:lab ch[{i}] run return 0",
           f"data modify storage last_ember:lab cp set from storage last_ember:lab ch[{i}]",
           f"data modify storage last_ember:lab cp.fx set from storage last_ember:lab ch[{j}].x",
           f"data modify storage last_ember:lab cp.fz set from storage last_ember:lab ch[{j}].z",
           f"execute as @e[type=minecraft:item_display,tag=le.cs{k}] if score @s le.lnk = #id le.l run function last_ember:lab/cent/tp with storage last_ember:lab cp"]
wtext(os.path.join(gd, "cent_place.mcfunction"), "\n".join(cl) + "\n")
bl = ["# GENERATED: as the new carrier at itself: its path marker, the body segments (le.cs<k>) and their hit boxes (le.cb<k>), all with its le.lnk"]
bl.append('summon minecraft:marker ~ ~ ~ {Tags:["le.cmark","le.cnew"],data:{h:[]}}')
for k in range(NSEG):
    mdl = "cent_tail" if k == NSEG - 1 else ("cent_seg_a" if k % 2 == 0 else "cent_seg_b")
    sc = SCALES[k]
    bl.append('summon minecraft:item_display ~ ~ ~ {Tags:["le.cseg","le.cs%d","le.cnew"],teleport_duration:2,view_range:1.5f,item_display:"none",item:{id:"minecraft:stick",count:1,components:{"minecraft:item_model":"last_ember:lab/%s"}},transformation:{translation:[0f,0f,0f],left_rotation:[0f,0f,0f,1f],scale:[%sf,%sf,%sf],right_rotation:[0f,0f,0f,1f]}}' % (k, mdl, sc, sc, sc))
    bl.append('summon minecraft:interaction ~ ~ ~ {Tags:["le.cbox","le.cb%d","le.cnew"],width:%sf,height:%sf,response:1b}' % (k, round(0.9 * sc, 2), round(0.5 * sc, 2)))
bl.append("scoreboard players operation @e[tag=le.cnew] le.lnk = @s le.lnk")
for k in range(NSEG): bl.append(f"scoreboard players set @e[tag=le.cnew,tag=le.cs{k}] le.lfr {k}")
bl.append("tag @e[tag=le.cnew] remove le.cnew")
wtext(os.path.join(gd, "cent_build.mcfunction"), "\n".join(bl) + "\n")
# the feelers twitch: 8 random sway poses per side (base out to the side and up), a new one every 4 ticks, 4 ticks of interpolation
ANT = {"l": (0.31, 28), "r": (-0.31, -28)}
ar = random.Random(7)
for side, (ax, base) in ANT.items():
    disp = [f"# GENERATED: as the carrier: a new random sway of the {side} feeler"]
    disp.append(f"execute store result score #ra le.l run random value 0..7")
    for i in range(8):
        q = qeul(-18 + ar.uniform(-22, 22), base + ar.uniform(-24, 24), ar.uniform(-25, 25))
        disp.append(f"execute if score #ra le.l matches {i} on passengers if entity @s[tag=le.lab_ant_{side}] run data merge entity @s " + merge((ax, 0.18, 0.47), q, 1.5, 4))
    wtext(os.path.join(gd, f"cent_ant_{side}.mcfunction"), "\n".join(disp) + "\n")
    q = qeul(35, base * 1.4, 0)
    open(os.path.join(gd, "cent_ant_droop.mcfunction"), "a").write(f"execute on passengers if entity @s[tag=le.lab_ant_{side}] run data merge entity @s " + merge((ax, 0.1, 0.47), q, 1.5, 14) + "\n")
# the venom claws: chewing (a random small opening every 5 ticks), opened wide before a bite, snapped shut
CLAW = {"l": 0.431, "r": -0.431}
def claws(open_deg, dur, jitter=0.0, rr=None):
    out = []
    for side, cx in CLAW.items():
        sgn = 1 if side == "l" else -1
        q = qeul(4 + (rr.uniform(-6, 6) if rr else 0), sgn * (open_deg + (rr.uniform(-jitter, jitter) if rr else 0)), 0)
        out.append(f"execute on passengers if entity @s[tag=le.lab_claw_{side}] run data merge entity @s " + merge((cx, -0.2875, 0.469), q, 1.5, dur))
    return out
cr = random.Random(9)
chew = ["# GENERATED: as the carrier: the venom claws chew (a random opening)", "execute store result score #ra le.l run random value 0..5"]
for i in range(6):
    for ln in claws(cr.uniform(-4, 14), 5, 4, cr): chew.append(f"execute if score #ra le.l matches {i} run " + ln)
wtext(os.path.join(gd, "cent_claw_chew.mcfunction"), "\n".join(chew) + "\n")
wtext(os.path.join(gd, "cent_claw_open.mcfunction"), "# GENERATED: the claws open wide\n" + "\n".join(claws(34, 4)) + "\n")
wtext(os.path.join(gd, "cent_claw_snap.mcfunction"), "# GENERATED: the claws snap shut\n" + "\n".join(claws(-10, 1)) + "\n")
# the rearing (Edward: it rears up on its hind part to frighten, then strikes with its whole body): the head and everything riding it
# (feelers, claws) move as one piece: head origin + D, turned by Q; the children keep their place on the head
HEAD_T0 = (0, -0.475, 0)
KIDS = {"le.lab_chead": ((0, 0, 0), (0, 0, 0)), "le.lab_ant_l": ((0.31, 0.655, 0.47), (-18, 28, 0)), "le.lab_ant_r": ((-0.31, 0.655, 0.47), (-18, -28, 0)),
        "le.lab_claw_l": ((0.431, 0.1875, 0.469), (4, 30, 0)), "le.lab_claw_r": ((-0.431, 0.1875, 0.469), (4, -30, 0))}
def rear(fname, D, pitch, dur, claws_open):
    Q = qeul(pitch, 0, 0); out = [f"# GENERATED: the rearing of the scolopendra: {fname} (as the carrier)"]
    for tg, (o, e) in KIDS.items():
        if tg.startswith("le.lab_claw"): e = (e[0], e[1] if claws_open else (-10 if e[1] > 0 else 10), 0)
        t = tuple(a + b + c for a, b, c in zip(HEAD_T0, D, qrot(Q, o)))
        out.append(f"execute on passengers if entity @s[tag={tg}] run data merge entity @s " + merge(t, qmul(Q, qeul(*e)), 1.5, dur))
    wtext(os.path.join(gd, f"cent_rear_{fname}.mcfunction"), "\n".join(out) + "\n")
rear("up", (0, 3.1, -1.2), -35, 12, True)
rear("slam", (0, 0.1, 1.4), 25, 3, False)
rear("back", (0, 0, 0), 0, 6, False)
lg = ["# GENERATED: the legs of the body step (models a/b swap; neighbours in the other phase), macro p = 0 or 1"]
for k in range(NSEG - 1):
    a, b = ("cent_seg_a", "cent_seg_b") if k % 2 == 0 else ("cent_seg_b", "cent_seg_a")
    lg.append(f'$execute if score #lp le.l matches $(p) as @e[type=minecraft:item_display,tag=le.cs{k}] if score @s le.lnk = #id le.l run data modify entity @s item.components."minecraft:item_model" set value "last_ember:lab/{a}"')
    lg.append(f'$execute unless score #lp le.l matches $(p) as @e[type=minecraft:item_display,tag=le.cs{k}] if score @s le.lnk = #id le.l run data modify entity @s item.components."minecraft:item_model" set value "last_ember:lab/{b}"')
wtext(os.path.join(gd, "cent_legs.mcfunction"), "\n".join(lg) + "\n")
print(f"lab: {len(MATS)} materials, models, drowner skin, warg variant, rigs: leshy {len(LESHY_POSES)} poses, warg {len(WARG_POSES)} poses")

# T-020: the parts of the contract monsters that share a skeleton: the heath wolf (warg rig) and the grove leshy (leshy rig), only other models
wp = open(os.path.join(gd, "warg_parts.mcfunction"), encoding="utf-8").read()
hp_ = wp.replace("warg_parts", "heath_parts").replace("lab/warg_", "lab/heath_")
hp_ = hp_.replace('"le.wp_leg_fr"],teleport_duration:3,view_range:1.5f,item_display:"none",item:{id:"minecraft:stick",count:1,components:{"minecraft:item_model":"last_ember:lab/heath_fleg"', '"le.wp_leg_fr"],teleport_duration:3,view_range:1.5f,item_display:"none",item:{id:"minecraft:stick",count:1,components:{"minecraft:item_model":"last_ember:lab/heath_flegr"')
assert "heath_flegr" in hp_
wtext(os.path.join(gd, "heath_parts.mcfunction"), hp_)
lp = open(os.path.join(gd, "leshy_parts.mcfunction"), encoding="utf-8").read()
gp = lp.replace("leshy_parts", "grove_parts").replace("lab/leshy_torso", "lab/grove_torso"); assert "grove_torso" in gp
wtext(os.path.join(gd, "grove_parts.mcfunction"), gp)
print("T-020: heath wolf and grove leshy parts")
