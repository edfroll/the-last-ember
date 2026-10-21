"""Shared geometry for the Refuge: target terrain, rotation helpers."""
import math
PLAZA_R = 33          # flat plaza incl. arcade footprint
FLOOR = 102           # top block of the plaza (players stand at 103)
SMITHY = (52, 34, 100); TAVERN = (-54, 32, 100); WELL = (40, -44, 101); TOWER = (-110, -90)
def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def rect_d(x, z, cx, cz, hx, hz):  # distance outside an axis rectangle (0 inside)
    return math.hypot(max(abs(x - cx) - hx, 0), max(abs(z - cz) - hz, 0))
def target(x, z, natural):
    """(height, cut): cut=True means the height is exact (also lowers terrain)."""
    r = math.hypot(x, z)
    if r <= PLAZA_R + 1: return FLOOR, True
    best = None
    # building pads (exact) with a 6-block soft rim
    for (cx, cz, fy), (hx, hz) in ((SMITHY, (11, 13)), (TAVERN, (12, 14)), (WELL, (11, 11))):
        d = rect_d(x, z, cx, cz, hx, hz)
        if d == 0: return fy, True
        if d < 6: best = max(best or -999, fy - (fy - natural) * smooth(d / 6) if natural < fy else fy)
    # tower hill: flat top r 7 at 124 (tower base stands at 125), slopes ease into the surrounding ground (no cliff at the foot);
    # the foot radius wobbles with the angle so the hill does not read as a perfect cone
    rt = math.hypot(x - TOWER[0], z - TOWER[1])
    if rt <= 12.5: return 124, True
    ang = math.atan2(z - TOWER[1], x - TOWER[0])
    R = 62 + 9 * math.sin(3 * ang + 0.7) + 5 * math.sin(5 * ang + 2.1)
    hill = None
    if rt < R:
        t = (rt - 12.5) / (R - 12.5); hill = (124, 1 - smooth(t) ** 0.8)       # weight of the hill top over the base ground
    # plateau around the plaza: 102 at the plaza edge, 99 at r 90, blending into the natural ground by r 150
    base = natural
    if r <= 90: base = FLOOR - 3 * smooth((r - PLAZA_R) / (90 - PLAZA_R))
    elif r <= 150: base = 99 + (natural - 99) * smooth((r - 90) / 60) if natural < 99 else natural
    # gate vestibules buried under grassy mounds (T-008 review)
    for ga in GATE_ANGLES:
        u, v = unrot(0, 0, ga, x, z); d = math.hypot(max(0, abs(v) - 5.5), max(0, u - 43, 33 - u))
        if d < 9: base = max(base, FLOOR + 8 - 8 * smooth(d / 9) if d > 0 else FLOOR + 8)
    if hill: base = base + (hill[0] - base) * hill[1]
    if best is not None: base = max(base, best)
    return base, False
def rot(cx, cz, ang, u, v):
    """local (u outward radial, v to the right when looking outward) -> world, angle from north clockwise (deg)"""
    a = math.radians(ang); ox, oz = math.sin(a), -math.cos(a); rx, rz = math.cos(a), math.sin(a)
    return cx + u * ox + v * rx, cz + u * oz + v * rz
def unrot(cx, cz, ang, x, z):
    a = math.radians(ang); ox, oz = math.sin(a), -math.cos(a); rx, rz = math.cos(a), math.sin(a)
    dx, dz = x - cx, z - cz
    return dx * ox + dz * oz, dx * rx + dz * rz
GATE_ANGLES = (0, 45, 90, 160, 215, 270)   # = plaza.GATES
FACES = ["north", "east", "south", "west"]
def face_rot(local_face, ang):
    """local facings: 'out' (radially outward), 'in', 'right', 'left' -> nearest world facing"""
    base = {"out": 0, "right": 90, "in": 180, "left": 270}[local_face]
    return FACES[int(round(((ang + base) % 360) / 90)) % 4]
