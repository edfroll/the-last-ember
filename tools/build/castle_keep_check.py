"""T-029: the checks of the castle's blocks (run by tools/build/r1_castle.py on the block model before it is written; SystemExit on a
failure): the arena by the card (32 x 32, height 20, 6 columns 3 x 3 of full height, the gallery at 6, 3 wide), the columns' reach, the
ways (castle_walkcheck.reach: no jumps, no dropping through floors): from the gate of the barbican the court, every room of the wings, the
galleries, the vestibule, the throne hall and its gallery are reached; the gaol and the crypt only through the gaol door (shut: 0), the
reliquary only through the door behind the throne (shut: 0), the secret way from outside only through the pier door (shut: 0); and back up
(the crypt -> the library, the pier door -> the reliquary)."""
import math
import castle_layout as L
import castle_walkcheck as CW

P = L.P


def targets():
    return {"court": (450, 50, P + 1), "chapel": (420, 46, P + 1), "loft": (430, 46, P + 9), "library": (414, 75, P + 1), "lib_balcony": (410, 70, P + 9),
            "kitchen": (473, 49, P + 1), "pantry": (479, 51, P + 1), "armoury": (476, 62, P + 1), "gal_w": (435, 45, P + 9), "gal_s": (450, 56, P + 9),
            "gal_e": (468, 45, P + 9), "annex_G": (424, 64, P + 9), "vestibule": (447, 74, P + 1), "hall": (444, 74, L.HALL_Y + 1),
            "hall_gallery": (450, 60, L.HALL_Y + L.HG + 1), "gaol": (414, 78, L.GAOL_Y + 1), "crypt": (420, 50, L.CRYPT_Y + 1),
            "reliquary": (466, 75, L.HALL_Y + 1), "spiral_bottom": (475, 79, L.TUN_Y + 1), "tunnel_door": (434, -32, L.DOOR_Y + 1)}


PUBLIC = ["court", "chapel", "loft", "library", "lib_balcony", "kitchen", "pantry", "armoury", "gal_w", "gal_s", "gal_e", "annex_G", "vestibule", "hall", "hall_gallery"]
LOCKED = ["gaol", "crypt", "reliquary", "spiral_bottom", "tunnel_door"]


def run(b, gr, rl, tpl):
    T = rl["Tw"]
    def mk(states):
        over = {}
        for s in states: over.update(tpl[s])
        def get(x, y, z):
            if (x, y, z) in over: return over[(x, y, z)]
            s = b.get(x, y, z)
            if s is not None: return s
            i, j = z - gr["z1"], x - gr["x1"]
            return "minecraft:stone" if 0 <= i < T.shape[0] and 0 <= j < T.shape[1] and y <= T[i, j] else None
        return get
    tg = targets(); out = {}; fail = []
    def reached(states, start, bx=(400, 28, 490, 96)):
        seen = CW.reach(mk(states), start, bx, 90, 262)
        return {n for n, (x, z, y) in tg.items() if any(abs(s - y) < 0.6 for (xx, zz, s) in seen if xx == x and zz == z)}
    gate = (451, 33, 163.0)
    shut = reached(["gate_closed", "gaol_door_closed", "reliq_door_closed", "pier_door_closed"], gate)
    opened = reached(["gate_closed", "gaol_door_open", "reliq_door_open", "pier_door_closed"], gate, (400, -40, 490, 96))
    PB = (420, -40, 490, 96)
    pier_shut = reached(["pier_door_closed"], (428, -32, 117.0), PB)
    pier_open = reached(["pier_door_open", "reliq_door_closed"], (428, -32, 117.0), PB)
    up_crypt = reached(["gaol_door_open"], (420, 47, float(L.CRYPT_Y + 1)))
    out["walk"] = dict(shut=sorted(shut), opened=sorted(opened), pier_shut=sorted(pier_shut), pier_open=sorted(pier_open), up_crypt=sorted(up_crypt))
    if set(PUBLIC) - shut: fail.append("from the gate not reached: %s" % sorted(set(PUBLIC) - shut))
    if shut & set(LOCKED): fail.append("reached with the doors shut: %s" % sorted(shut & set(LOCKED)))
    if set(PUBLIC + ["gaol", "crypt", "reliquary", "spiral_bottom", "tunnel_door"]) - opened: fail.append("with the doors open not reached: %s" % sorted(set(PUBLIC + LOCKED) - opened))
    if pier_shut & set(tg): fail.append("from the pier with its door shut: %s" % sorted(pier_shut & set(tg)))
    if not {"tunnel_door", "spiral_bottom", "reliquary"} <= pier_open: fail.append("from the pier (door open) the way up to the reliquary: %s" % sorted(pier_open))
    if not {"gaol", "library", "court"} <= up_crypt: fail.append("from the crypt back up: %s" % sorted(up_crypt))
    # the arena (the card): 32 x 32 of air 20 high over the floor (but the columns, the gallery, its posts and stairs, the dais)
    hx1, hz1, hx2, hz2 = L.inside(L.HALL); HY = L.HALL_Y
    air = lambda s: s is None or s == "minecraft:air"
    cols = [(x, z) for (a, c) in L.COLS_X for (d, e) in L.COLS_Z for x in range(a, c + 1) for z in range(d, e + 1)]
    col_full = all(not air(b.get(x, y, z)) for (x, z) in cols for y in range(HY + 1, HY + L.HALL_H + 1))
    ceiling = all(not air(b.get(x, HY + L.HALL_H + 1, z)) for x in range(hx1, hx2 + 1) for z in range(hz1, hz2 + 1))
    top_air = all(air(b.get(x, HY + L.HALL_H, z)) for x in range(hx1, hx2 + 1) for z in range(hz1, hz2 + 1) if (x, z) not in cols)
    walls = all(not air(b.get(x, HY + 12, z)) for x in (hx1 - 1, hx2 + 1) for z in range(hz1, hz2 + 1)) and all(not air(b.get(x, HY + 12, z)) for z in (hz1 - 1, hz2 + 1) for x in range(hx1, hx2 + 1))
    gal = [(x, z) for x in range(hx1, hx2 + 1) for z in range(hz1, hz2 + 1) if x <= hx1 + 2 or x >= hx2 - 2 or z <= hz1 + 2 or z >= hz2 - 2]
    gal_ok = all(b.get(x, HY + L.HG, z) == "minecraft:dark_oak_planks" for (x, z) in gal)
    reach_e = L.column_reach()
    cheb = 0
    for x in range(hx1 + 3, hx2 - 2):
        for z in range(hz1 + 3, hz2 - 2):
            if (x, z) in cols: continue
            cheb = max(cheb, min(max(max(a - x, 0, x - c), max(d - z, 0, z - e)) for (a, c) in L.COLS_X for (d, e) in L.COLS_Z))
    out["arena"] = dict(size=[hx2 - hx1 + 1, hz2 - hz1 + 1, L.HALL_H], columns=len(cols) // 9, columns_full=col_full, ceiling=ceiling, top_air=top_air, walls=walls,
                        gallery_at=L.HG, gallery_cells=len(gal), gallery_ok=gal_ok, reach_euclid=reach_e, reach_cheb_inside=cheb)
    if not (hx2 - hx1 + 1 == 32 and hz2 - hz1 + 1 == 32 and col_full and ceiling and top_air and walls and gal_ok and len(cols) == 54): fail.append("arena: %s" % out["arena"])
    if cheb > 6: fail.append("a floor cell inside the gallery line more than 6 from a column (Chebyshev %d)" % cheb)
    print("keep check: walk %s; arena %s" % ({k: len(v) for k, v in out["walk"].items()}, out["arena"]))
    if fail: raise SystemExit("castle keep check FAILED: " + "; ".join(fail))
    return out
