#!/usr/bin/env python3
"""T-004 two-player test: Cam and Cam2 online. Independent modes, simultaneous transitions, death of one inside a zone."""
import importlib.util, os, socket, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("rcon", os.path.join(ROOT, "tools/rcon.py")); rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
p = rc.props(); S = socket.create_connection(("127.0.0.1", int(p["rcon.port"])), timeout=30); rc.pkt(S, 1, 3, p["rcon.password"]); rc.read(S)
def R(c): return rc.exchange(S, c)
res = []
def mode(n):
    for m in ("adventure", "survival", "spectator", "creative"):
        if "passed" in R(f"execute if entity @a[name={n},gamemode={m}]"): return m
def check(name, want, wait=0.6):
    time.sleep(wait); got = {n: mode(n) for n in want}; good = got == want
    res.append(good); print(("PASS " if good else "FAIL ") + name + f"  {got}", flush=True)
for n in ("Cam", "Cam2"):
    R(f"gamemode survival {n}"); R(f"effect give {n} minecraft:resistance infinite 255 true"); R(f"effect give {n} minecraft:slow_falling infinite 0 true")
R("tp Cam 300 120 300"); R("tp Cam2 300 120 302"); check("both outside", {"Cam": "survival", "Cam2": "survival"})
R("tp Cam 16 80 16"); check("Cam in box, Cam2 outside", {"Cam": "adventure", "Cam2": "survival"})
R("tp Cam 300 120 300"); R("tp Cam2 16 80 16"); check("swap in the same tick", {"Cam": "survival", "Cam2": "adventure"})
R("tp Cam -75 80 0"); R("tp Cam2 -95 80 0"); check("both in overlapping zones", {"Cam": "adventure", "Cam2": "adventure"})
R("tp Cam -40 80 0"); check("Cam leaves B, Cam2 still in A", {"Cam": "survival", "Cam2": "adventure"})
R("spawnpoint Cam2 300 120 300"); R("effect clear Cam2 minecraft:resistance"); R("kill Cam2"); time.sleep(2.5)
check("Cam2 died in zone, respawned outside", {"Cam": "survival", "Cam2": "survival"}, 1.5)
print(f"\n{sum(res)}/{len(res)} passed")
