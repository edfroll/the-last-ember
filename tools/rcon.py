#!/usr/bin/env python3
"""Minimal RCON client. Usage: rcon.py <command...>  (host/port/password from server/server.properties)"""
import os, socket, struct, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def props():
    p = {}
    with open(os.path.join(ROOT, "server", "server.properties")) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.rstrip("\n").split("=", 1)
                p[k] = v
    return p

def pkt(sock, rid, typ, body):
    data = struct.pack("<ii", rid, typ) + body.encode() + b"\0\0"
    sock.sendall(struct.pack("<i", len(data)) + data)

def read(sock):
    raw = b""
    while len(raw) < 4:
        raw += sock.recv(4 - len(raw))
    n = struct.unpack("<i", raw)[0]
    buf = b""
    while len(buf) < n:
        buf += sock.recv(n - len(buf))
    rid, typ = struct.unpack("<ii", buf[:8])
    return rid, typ, buf[8:-2].decode(errors="replace")

def exchange(s, cmd):
    """Send one command, return the full reply. Replies >= ~4 KB arrive split into several packets; only then a bogus packet
    (type 200, id 3) is sent as an end marker (the server echoes it after the last fragment)."""
    pkt(s, 2, 2, cmd)
    _, _, out = read(s)
    if len(out.encode()) >= 4000:
        pkt(s, 3, 200, "")
        while True:
            rid, _, body = read(s)
            if rid == 3: break
            out += body
    return out

def run(cmd, host="127.0.0.1"):
    p = props()
    s = socket.create_connection((host, int(p.get("rcon.port", 25575))), timeout=30)
    pkt(s, 1, 3, p["rcon.password"])
    if read(s)[0] == -1:
        raise SystemExit("RCON auth failed")
    out = exchange(s, cmd)
    s.close()
    return out

if __name__ == "__main__":
    print(run(" ".join(sys.argv[1:])))
