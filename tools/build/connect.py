"""Offline placement has no block updates: fences, walls, panes and iron bars get their connection states computed here."""
from lib import ns
FENCES = ("_fence",); PANES = ("glass_pane", "iron_bars"); WALLS = ("_wall",)
NONSOLID = ("air", "lantern", "candle", "torch", "carpet", "slab", "stairs", "door", "trapdoor", "sign", "button", "pressure_plate", "flower_pot", "iron_chain",
            "rail", "ladder", "vine", "campfire", "bed", "banner", "head", "skull", "lever", "grass", "flower", "fern", "bush", "sapling", "cauldron", "anvil",
            "grindstone", "water", "lava", "light", "lichen", "roots", "snow", "kelp", "seagrass", "litter", "frame", "rod", "pot", "bell", "scaffolding", "cobweb")
def base(s): return s.split("[")[0].split("{")[0].replace("minecraft:", "")
def kind(b):
    if any(b.endswith(f) for f in FENCES) and "gate" not in b: return "fence"
    if b in PANES or b.endswith("stained_glass_pane"): return "pane"
    if any(b.endswith(w) for w in WALLS) and "sign" not in b and "banner" not in b and "torch" not in b and "fan" not in b: return "wall"
    return None
def solid(b): return b and not any(t in b for t in NONSOLID)
def connect(B):
    dirs = {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}
    upd = {}
    for (x, y, z), s in B.v.items():
        if "[" in s: continue
        b = base(s); k = kind(b)
        if not k: continue
        props = []
        for d, (dx, dz) in dirs.items():
            nb = B.v.get((x + dx, y, z + dz)); nbb = base(nb) if nb else None
            c = bool(nbb) and (kind(nbb) == k or (k == "fence" and kind(nbb) == "fence") or (k in ("pane", "wall") and kind(nbb) in ("pane", "wall")) or solid(nbb))
            props.append((d, ("low" if c else "none") if k == "wall" else ("true" if c else "false")))
        if k == "wall":
            above = B.v.get((x, y + 1, z)); props.append(("up", "true")); 
        upd[(x, y, z)] = ns(b) + "[" + ",".join(f"{a}={v}" for a, v in props) + "]"
    B.v.update(upd)
