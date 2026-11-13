"""T-022: read tools/terrain.sh scan files and write grid files for tools/terrain.sh apply (numpy)."""
import struct, numpy as np
NONE = -32768
class Scan:
    def __init__(self, path):
        d = open(path, "rb").read(); assert d[:4] == b"LETS"
        self.x0, self.z0, self.w, self.h = struct.unpack("<4i", d[4:20]); n = self.w * self.h; o = 20
        a = np.frombuffer(d, "<i2", 3 * n, o).reshape(3, self.h, self.w).astype(np.int32)
        self.ground, self.top, self.water = a[0], a[1], a[2]
        self.flags = np.frombuffer(d, np.uint8, n, o + 6 * n).reshape(self.h, self.w)
    def ix(self, x, z): return z - self.z0, x - self.x0
    def g(self, x, z): return int(self.ground[z - self.z0, x - self.x0])
def write_grid(path, x0, z0, H, F, W, S, R, A):
    h, w = H.shape
    with open(path, "wb") as f:
        f.write(b"LETA" + struct.pack("<4i", x0, z0, w, h))
        for a in (H, F, W): f.write(np.ascontiguousarray(a, "<i2").tobytes())
        for a in (S, R, A): f.write(np.ascontiguousarray(a, np.uint8).tobytes())
