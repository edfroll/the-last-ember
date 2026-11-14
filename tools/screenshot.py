#!/usr/bin/env python3
"""Automatic in-game screenshots from given points/angles (real 26.3 client, spectator camera driven by RCON).
Usage: screenshot.py shots.json [--out DIR] [--settle SECONDS] [--player Cam]
shots.json: {"time": "noon", "weather": "clear", "shots": [{"name": "a", "x": 0, "y": 150, "z": 0, "yaw": 30, "pitch": 40, "hud": false, "settle": 8}, ...]}
yaw/pitch as in /tp (yaw 0 = south, 90 = west, 180 = north, -90 = east; pitch 90 = straight down).
Requires: server running (tools/server.sh start) and client joined (tools/client_launch.py). Output: PNG per shot (2560x1440 on a 1280x720 retina window).
"""
import argparse, importlib.util, json, os, shutil, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("rcon", os.path.join(ROOT, "tools/rcon.py"))
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
CLIENT = os.path.join(ROOT, "server/client")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("--out", default=os.path.join(ROOT, "docs/reports/shots"))
    ap.add_argument("--settle", type=float, default=6); ap.add_argument("--player", default="Cam")
    ap.add_argument("--double", action="store_true", help="capture twice, keep the second: the software-GL cloud client can hand back the frame of the previous request")
    a = ap.parse_args()
    cfg = json.load(open(a.spec)); os.makedirs(a.out, exist_ok=True)
    rc.run(f"gamemode spectator {a.player}")   # only the camera; the server default stays survival for real players
    time.sleep(2)  # the client agent auto-respawns a dead camera player
    rc.run(f"gamemode spectator {a.player}")
    if "time" in cfg: rc.run(f"time set {cfg['time']}")
    if "weather" in cfg: rc.run(f"weather {cfg['weather']}")
    for s in cfg["shots"]:
        rc.run(f"tp {a.player} {s['x']} {s['y']} {s['z']} {s.get('yaw', 0)} {s.get('pitch', 0)}")
        time.sleep(s.get("settle", a.settle))  # chunks + lighting
        done = os.path.join(CLIENT, "shot-done.txt")
        for nm in ([s["name"] + "__pre"] if a.double else []) + [s["name"]]:
            if os.path.exists(done): os.remove(done)
            with open(os.path.join(CLIENT, "shot-request.txt"), "w") as f: f.write(f"{nm} {1 if s.get('hud') else 0}\n")
            for _ in range(120):
                if os.path.exists(done): break
                time.sleep(0.5)
            if nm.endswith("__pre"):
                pre = os.path.join(CLIENT, "screenshots", nm + ".png")
                time.sleep(1)
                if os.path.exists(pre): os.remove(pre)
                time.sleep(11)          # the chat line «Saved screenshot…» fades after 10 s
        res = open(done).read().strip() if os.path.exists(done) else "timeout"
        src = os.path.join(CLIENT, "screenshots", s["name"] + ".png")
        if res.endswith("ok") and os.path.exists(src):
            shutil.move(src, os.path.join(a.out, s["name"] + ".png")); print("ok", s["name"])
        else:
            print("FAIL", s["name"], res)

main()
