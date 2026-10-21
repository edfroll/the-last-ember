"""T-008 builder library: a voxel model of one piece (absolute or anchor-relative coordinates) with palette mixing,
then exported as
  - placement list for tools/blockwriter.sh apply  (offline write into the world),
  - .nbt structure template                       (tools/blockwriter.sh nbt),
  - mcfunction with relative setblocks            (pieces built at runtime: bonfire and urn variants).
States are full block state strings, e.g. "minecraft:stone_brick_stairs[facing=north]". Air is written as minecraft:air.
"""
import math, os

def h(x, y, z, s=0):
    n = (x * 73856093) ^ (y * 19349663) ^ (z * 83492791) ^ (s * 2654435761)
    n &= 0xffffffff; n = ((n ^ (n >> 13)) * 1274126177) & 0xffffffff; n ^= n >> 16
    return (n & 0xffffff) / 0x1000000

def ns(s):
    head = s.split("[", 1)[0].split("{", 1)[0]
    return s if ":" in head else "minecraft:" + s

class Mix:
    """weighted palette: Mix({'stone_bricks': 35, 'tuff_bricks': 20, ...}); picked by position hash (deterministic)"""
    def __init__(self, weights, salt=0):
        tot = sum(weights.values()); acc = 0; self.t = []
        for k, w in weights.items(): acc += w / tot; self.t.append((acc, ns(k)))
        self.salt = salt
    def at(self, x, y, z):
        r = h(x, y, z, self.salt)
        for a, k in self.t:
            if r <= a: return k
        return self.t[-1][1]

class B:
    def __init__(self, name):
        self.name = name; self.v = {}; self.cmds = []; self.markers = []
    def st(self, s, x, y, z):
        return s.at(x, y, z) if isinstance(s, Mix) else ns(s)
    def set(self, x, y, z, s): self.v[(x, y, z)] = self.st(s, x, y, z)
    def get(self, x, y, z): return self.v.get((x, y, z))
    def fill(self, x1, y1, z1, x2, y2, z2, s, only_empty=False, replace=None):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    if only_empty and (x, y, z) in self.v and self.v[(x, y, z)] != "minecraft:air": continue
                    if replace is not None and self.v.get((x, y, z)) not in replace: continue
                    self.set(x, y, z, s)
    def walls(self, x1, y1, z1, x2, y2, z2, s):
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1): self.set(x, y, z1, s); self.set(x, y, z2, s)
            for z in range(z1, z2 + 1): self.set(x1, y, z, s); self.set(x2, y, z, s)
    def disc(self, cx, y, cz, r, s, hollow_r=None):
        """filled circle of radius r (block centres), optional hole"""
        ri = int(math.ceil(r))
        for dx in range(-ri, ri + 1):
            for dz in range(-ri, ri + 1):
                d = math.hypot(dx, dz)
                if d <= r + 0.3 and (hollow_r is None or d > hollow_r + 0.3): self.set(cx + dx, y, cz + dz, s)
    def cyl(self, cx, y1, cz, y2, r, s, hollow_r=None):
        for y in range(y1, y2 + 1): self.disc(cx, y, cz, r, s, hollow_r)
    def marker(self, name, x, y, z, note=""): self.markers.append((name, x, y, z, note))
    def cmd(self, c): self.cmds.append(c)
    # ---- export ----
    def bbox(self):
        xs = [p[0] for p in self.v]; ys = [p[1] for p in self.v]; zs = [p[2] for p in self.v]
        return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)
    def write_placements(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            for (x, y, z), s in sorted(self.v.items(), key=lambda kv: (kv[0][1], kv[0][0], kv[0][2])): f.write(f"{x} {y} {z} {s}\n")
        return len(self.v)
    def write_mcfunction(self, path, ax, ay, az, header=""):
        """relative setblocks around the anchor; blocks with block entities are placed last (after their supports)"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        items = sorted(self.v.items(), key=lambda kv: (kv[0][1], kv[0][0], kv[0][2]))
        with open(path, "w") as f:
            if header: f.write(header.rstrip() + "\n")
            for (x, y, z), s in items: f.write(f"setblock ~{x - ax} ~{y - ay} ~{z - az} {s}\n")
            for c in self.cmds: f.write(c + "\n")

def stairs(block, facing, half="bottom", shape="straight"):
    return f"minecraft:{block}[facing={facing},half={half},shape={shape}]"
def slab(block, t="bottom"): return f"minecraft:{block}[type={t}]"
def lantern(hanging=False): return f"minecraft:lantern[hanging={'true' if hanging else 'false'}]"
def candle(n=1, lit=False): return f"minecraft:candle[candles={n},lit={'true' if lit else 'false'}]"
def log(block, axis="y"): return f"minecraft:{block}[axis={axis}]"
def fence(block="spruce_fence"): return f"minecraft:{block}"
