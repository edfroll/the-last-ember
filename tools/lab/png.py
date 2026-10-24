"""Tiny PNG reader/writer (no PIL here): 8-bit RGBA output; reads color types 0, 2, 3 (palette, 1-8 bit, tRNS), 4, 6 at bit depth <= 8."""
import struct, zlib
def read(path):
    data = path if isinstance(path, bytes) else open(path, "rb").read(); assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos = 8; idat = b""; plte = None; trns = None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]; typ = data[pos + 4:pos + 8]; body = data[pos + 8:pos + 8 + ln]; pos += 12 + ln
        if typ == b"IHDR": w, h, bd, ct, _, _, il = struct.unpack(">IIBBBBB", body)
        elif typ == b"PLTE": plte = [tuple(body[i:i + 3]) for i in range(0, len(body), 3)]
        elif typ == b"tRNS": trns = body
        elif typ == b"IDAT": idat += body
    raw = zlib.decompress(idat); ch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]; bpp = max(1, ch * bd // 8); stride = (w * ch * bd + 7) // 8
    rows = []; prev = bytearray(stride); i = 0
    for y in range(h):
        f = raw[i]; line = bytearray(raw[i + 1:i + 1 + stride]); i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0; b = prev[x]; c = prev[x - bpp] if x >= bpp else 0
            if f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + b) & 255
            elif f == 3: line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c; pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        prev = line; px = []
        if bd < 8:
            vals = []
            for byte in line:
                for k in range(8 // bd): vals.append((byte >> (8 - bd * (k + 1))) & ((1 << bd) - 1))
            vals = vals[:w * ch]
        else: vals = list(line)
        for x in range(w):
            if ct == 3:
                idx = vals[x]; r, g, bb = plte[idx]; al = trns[idx] if trns and idx < len(trns) else 255; px.append((r, g, bb, al))
            elif ct == 6: px.append(tuple(vals[x * 4:x * 4 + 4]))
            elif ct == 2: px.append(tuple(vals[x * 3:x * 3 + 3]) + (255,))
            elif ct == 0: v = vals[x] * (255 // ((1 << bd) - 1)); px.append((v, v, v, 255))
            elif ct == 4: v = vals[x * 2]; px.append((v, v, v, vals[x * 2 + 1]))
        rows.append(px)
    return w, h, rows
def write(path, rows):
    h = len(rows); w = len(rows[0])
    raw = b"".join(b"\x00" + b"".join(bytes(p) for p in row) for row in rows)
    def chunk(t, d): c = struct.pack(">I", len(d)) + t + d; return c + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
