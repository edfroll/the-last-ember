#!/usr/bin/env python3
"""T-022: client FPS at 5 points of the Dol, day and night (Cam, spectator, render distance 12; server/client/options.txt needs
inactivityFpsLimit:"minimized"), and the server tick (MSPT from `perf`) with Cam and Cam2 standing in the Dol.
Usage: python3 tools/build/r1_perf.py"""
import glob, os, re, sys, time, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools")); import rcon as rc
import importlib.util
sp = importlib.util.spec_from_file_location("tc", os.path.join(ROOT, "tools/test_class.py")); tc = importlib.util.module_from_spec(sp); sp.loader.exec_module(tc)
R = rc.run
def fps():
    d = os.path.join(ROOT, "server/client/shot-done.txt")
    v = []
    for _ in range(5):
        if os.path.exists(d): os.remove(d)
        open(os.path.join(ROOT, "server/client/shot-request.txt"), "w").write("!fps\n")
        for _ in range(60):
            if os.path.exists(d): break
            time.sleep(0.05)
        m = re.search(r"fps (\d+)", open(d).read()) if os.path.exists(d) else None
        if m: v.append(int(m.group(1)))
        time.sleep(1)
    return v
PTS = [("Refuge wall, looking into the Dol", 120.5, 125, 120.5, -45, 10), ("north edge, the Wall", -300.5, 96, -700.5, 180, -15),
       ("south bridge over the rift", 20.5, 150, 600.5, 30, 15), ("castle hill and the east ridge", 360.5, 190, -60.5, -90, 5),
       ("western forest and the ridge", -560.5, 120, 0.5, 90, 0)]
R("gamemode spectator Cam"); R("gamemode survival Cam2"); R("effect give Cam2 minecraft:resistance infinite 255 true")
out = []
for tm in ("noon", "midnight"):
    R(f"time set {tm}")
    for name, x, y, z, yaw, pitch in PTS:
        R(f"tp Cam {x} {y} {z} {yaw} {pitch}"); time.sleep(12); v = fps()
        out.append((tm, name, min(v) if v else None, round(sum(v) / len(v)) if v else None)); print(out[-1], flush=True)
R("time set noon"); R("tp Cam -380.5 112 -180.5"); R("tp Cam2 200.5 100 -100.5"); time.sleep(15)
before = set(glob.glob(os.path.join(ROOT, "server/debug/profiling/*.zip")))
R("perf start"); time.sleep(11); R("perf stop"); time.sleep(3)
new = sorted(set(glob.glob(os.path.join(ROOT, "server/debug/profiling/*.zip"))) - before)
mspt = None
if new:
    z = zipfile.ZipFile(new[-1]); n = [f for f in z.namelist() if f.endswith("server/metrics/ticking.csv") or f.endswith("profiling.txt")]
    for f in z.namelist():
        if f.endswith("profiling.txt"):
            t = z.read(f).decode(); m = re.search(r"Tick time: ([\d.,]+) ms|tick:.*?([\d.]+)", t); 
            mm = re.search(r"Average tick time: ([\d.]+)", t) or re.search(r"(\d+\.\d+) ms per tick", t)
            print("profiling:", f, (mm.group(0) if mm else t[:400]))
print("FPS (min/avg):"); [print("  ", r) for r in out]
