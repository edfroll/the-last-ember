#!/usr/bin/env python3
"""Walk bot (T-008): the dev client player really walks a route (vanilla physics, survival/adventure), driven by the shot agent
(!fwd_on / !fwd_off) and RCON (yaw via tp, position polling). Reports where it gets stuck or falls, with a screenshot.
Usage: walkbot.py route.json [--player Cam] [--out DIR]
route.json: {"start": [x, y, z], "points": [[x, z, expected_y], ...]}   (block-centre coordinates are used as given)"""
import argparse, json, math, os, sys, time, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sp = importlib.util.spec_from_file_location("rcon", os.path.join(ROOT, "tools/rcon.py")); rc = importlib.util.module_from_spec(sp); sp.loader.exec_module(rc)
CL = os.path.join(ROOT, "server/client")
def agent(cmd):
    d = os.path.join(CL, "shot-done.txt")
    if os.path.exists(d): os.remove(d)
    open(os.path.join(CL, "shot-request.txt"), "w").write(cmd + "\n")
    for _ in range(100):
        time.sleep(0.05)
        if os.path.exists(d): return open(d).read()
    return "timeout"
def pos(p):
    r = rc.run(f"data get entity {p} Pos")
    v = r.split(":", 1)[1].strip().strip("[]").replace("d", "").split(",")
    return [float(t) for t in v]
NOT = ",".join("type=!" + t for t in ("player", "item", "arrow", "spectral_arrow", "trident", "experience_orb", "interaction", "item_display", "text_display",
                                      "block_display", "marker", "armor_stand", "item_frame", "glow_item_frame", "painting", "leash_knot", "area_effect_cloud"))
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("route"); ap.add_argument("--player", default="Cam"); ap.add_argument("--out", default=os.path.join(ROOT, "server/build/walk")); ap.add_argument("--jump", action="store_true"); ap.add_argument("--clear", action="store_true", help="remove mobs within 6 blocks of the bot while it walks (tests the route, not the fauna)")
    a = ap.parse_args(); route = json.load(open(a.route)); os.makedirs(a.out, exist_ok=True); P = a.player
    rc.run(f"gamemode survival {P}"); rc.run(f"effect give {P} minecraft:saturation infinite 1 true"); rc.run(f"effect give {P} minecraft:resistance infinite 4 true")
    sx, sy, sz = route["start"]; rc.run(f"tp {P} {sx} {sy} {sz}"); time.sleep(2)
    for _ in range(20):                       # far routes: wait until the client is really there (chunks loaded, the tp applied)
        x, y, z = pos(P)
        if math.hypot(x - sx, z - sz) < 1.5 and abs(y - sy) < 2: break
        rc.run(f"tp {P} {sx} {sy} {sz}"); time.sleep(0.5)
    problems = []; jumps = [0]; i = 0; top = -999; pts = route["points"]
    while i < len(pts):
        tx, tz, ey = pts[i]; prev_ey = pts[i - 1][2] if i else ey; x, y, z = pos(P)
        yaw = math.degrees(math.atan2(-(tx - x), tz - z))
        rc.run(f"rotate {P} {yaw:.1f} 20"); agent("!fwd_on"); cur = yaw
        used = False; side = False; last_jump = 0; t0 = time.time(); best = math.hypot(tx - x, tz - z); last_improve = t0
        while True:
            time.sleep(0.12); x, y, z = pos(P); d = math.hypot(tx - x, tz - z)
            if a.clear: rc.run(f"execute at {P} run tp @e[distance=..6,{NOT}] ~ -200 ~")
            if d < 0.6: break
            if d < best - 0.05: best = d; last_improve = time.time()
            if y < min(ey, prev_ey) - 1.6:
                problems.append(("fall", i, round(x, 1), round(y, 1), round(z, 1), ey)); break
            if a.jump and time.time() - last_improve > 0.5 and time.time() - last_jump > 0.8: agent("!jump_on"); time.sleep(0.25); agent("!jump_off"); last_jump = time.time(); jumps[0] += 1
            if not used and time.time() - last_improve > 1.0: agent("!use"); used = True   # a closed door in the way: open it
            if not side and time.time() - last_improve > 1.6:              # try a short sidestep (corners, posts) before giving up
                for off in (50, -50):
                    rc.run(f"rotate {P} {cur + off:.1f} 20"); time.sleep(0.35)
                rc.run(f"rotate {P} {cur:.1f} 20"); side = True
            if time.time() - last_improve > 3.5:
                problems.append(("stuck", i, round(x, 1), round(y, 1), round(z, 1), ey)); break
            yaw = math.degrees(math.atan2(-(tx - x), tz - z))
            if abs((yaw - cur + 180) % 360 - 180) > 4: rc.run(f"rotate {P} {yaw:.1f} 20"); cur = yaw   # rotate only: a tp would cancel step-ups
        agent("!fwd_off")
        if problems and problems[-1][1] == i:
            pr = problems[-1]; agent(f"walk_{len(problems)}_{pr[0]} 0"); print("PROBLEM", pr, flush=True)
            if len(problems) >= 6: break
            rc.run(f"tp {P} {tx} {ey} {tz}"); time.sleep(0.5); top = ey           # put the bot back on the route and go on
        i += 1
    x, y, z = pos(P); print("END at", round(x, 1), round(y, 1), round(z, 1), "problems:", len(problems), "jumps:", jumps[0])
    rc.run(f"gamemode spectator {P}"); rc.run(f"effect clear {P}")
    json.dump(problems, open(os.path.join(a.out, "problems.json"), "w"))
if __name__ == "__main__": main()
