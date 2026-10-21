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
    # tower cone: base diameter 70 at plaza level, top 124 (tower base stands at 125)
    rt = math.hypot(x - TOWER[0], z - TOWER[1])
    if rt <= 7: return 124, True
    if rt <= 35: best = max(best or -999, 124 - (124 - 101) * ((rt - 7) / 28) ** 0.85)
    # plateau around the plaza: 102 at the plaza edge, 99 at r 90, blending into the natural ground by r 150
    if r <= 90: best = max(best or -999, FLOOR - 3 * smooth((r - PLAZA_R) / (90 - PLAZA_R)))
    elif r <= 150: best = max(best or -999, 99 + (natural - 99) * smooth((r - 90) / 60) if natural < 99 else natural)
    return best, False
def rot(cx, cz, ang, u, v):
    """local (u outward radial, v to the right when looking outward) -> world, angle from north clockwise (deg)"""
    a = math.radians(ang); ox, oz = math.sin(a), -math.cos(a); rx, rz = math.cos(a), math.sin(a)
    return cx + u * ox + v * rx, cz + u * oz + v * rz
def unrot(cx, cz, ang, x, z):
    a = math.radians(ang); ox, oz = math.sin(a), -math.cos(a); rx, rz = math.cos(a), math.sin(a)
    dx, dz = x - cx, z - cz
    return dx * ox + dz * oz, dx * rx + dz * rz
FACES = ["north", "east", "south", "west"]
def face_rot(local_face, ang):
    """local facings: 'out' (radially outward), 'in', 'right', 'left' -> nearest world facing"""
    base = {"out": 0, "right": 90, "in": 180, "left": 270}[local_face]
    return FACES[int(round(((ang + base) % 360) / 90)) % 4]
