#!/usr/bin/env python3
"""T-029: the frames of the report (docs/reports/T-029/*.jpg, 1280 wide) from the dev client Cam (the camera, spectator); Cam2 is the
actor in the fight (survival, unhurt). Dark rooms are shot with night vision on the camera (the rooms are dark for the spawn: a frame
`*_dark` shows one of them as the player sees it).
  python3 tools/build/castle_keep_shots.py [name ...]"""
import importlib.util, json, math, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def load(n, path):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, path)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon", "tools/rcon.py")
R = rc.run
OUT = os.path.join(ROOT, "docs/reports/T-029"); os.makedirs(OUT, exist_ok=True)
CL = os.path.join(ROOT, "server/client")
sys.path.insert(0, os.path.join(ROOT, "tools/build")); import castle_layout as L
M = json.load(open(os.path.join(ROOT, "server/build/r1/castle.json"))); K = M["keep"]
P, HY, HG = L.P, L.HALL_Y, L.HALL_Y + L.HG
KING = "@e[type=minecraft:zombie,tag=le.king,limit=1]"
def yawpitch(f, t):
    dx, dy, dz = t[0] - f[0], t[1] - f[1], t[2] - f[2]
    return math.degrees(math.atan2(-dx, dz)), -math.degrees(math.atan2(dy, math.hypot(dx, dz)))
def jpg(name):
    from PIL import Image
    src = os.path.join(CL, "screenshots", name + ".png")
    if os.path.exists(src): Image.open(src).convert("RGB").resize((1280, 720)).save(os.path.join(OUT, name + ".jpg"), quality=80); os.remove(src)
LAST = [0.0]
def gap(sec=12.5):
    """the «Saved screenshot» line of the frame before comes asynchronously a few seconds after it; the next frame (with clean) only
    after it came, else it lands in the frame"""
    t = LAST[0] + sec - time.time()
    if t > 0: time.sleep(t)
def snap(name, hud=False, pre=False):
    gap()
    for nm in ((name + "__pre",) if pre else ()) + (name,):
        d = os.path.join(CL, "shot-done.txt")
        if os.path.exists(d): os.remove(d)
        open(os.path.join(CL, "shot-request.txt"), "w").write(f"{nm} {1 if hud else 0} clean\n")
        for _ in range(120):
            if os.path.exists(d): break
            time.sleep(0.5)
        time.sleep(0.6 if nm == name else 1.5)
        if nm != name:
            p = os.path.join(CL, "screenshots", nm + ".png")
            if os.path.exists(p): os.remove(p)
    LAST[0] = time.time(); jpg(name); print("  shot", name, flush=True)
def place(f, t, nv=True):
    R("gamemode spectator Cam"); yw, pt = yawpitch((f[0], f[1] + 1.62, f[2]), t)
    if nv: R("effect give Cam minecraft:night_vision infinite 0 true")
    else: R("effect clear Cam minecraft:night_vision")
    R(f"tp Cam {f[0]} {f[1]} {f[2]} {yw:.1f} {pt:.1f}")
def shot(name, f, t, hud=False, settle=6, nv=True):
    place(f, t, nv); time.sleep(settle); snap(name, hud)

def static():
    R("function last_ember:castle/kg/reset_all"); time.sleep(2)            # the king asleep on his throne, the doors as built
    R("time set noon"); R("weather clear")
    R("time set 12600"); shot("castle_sunset", (436, 170, -26), (452, 200, 60), settle=10, nv=False)
    R("time set noon")
    shot("castle_day", (452, 215, -14), (452, 195, 60), settle=10, nv=False)
    shot("court", (462, P + 6, 42), (440, P + 6, 56))
    shot("gallery", (468, L.GAL + 1, 42), (468, L.GAL + 2, 57))
    shot("chapel", (430, P + 2, 46), (410, P + 4, 46))
    shot("library", (418.5, L.GAL + 1, 80), (412, P + 2, 62))
    shot("riddle_wall", (417.5, P + 1, 61), (417.5, P + 2.5, 55))
    shot("library_dark", (418.5, L.GAL + 1, 80), (412, P + 2, 62), nv=False)
    shot("kitchens", (473.5, P + 4, 49.5), (481, P + 1, 46))
    shot("armoury", (472, P + 2, 56), (480, P + 2, 66))
    shot("vestibule", (446.5, P + 1, 84), (446.5, P + 2, 66))
    shot("gaol", (414.5, L.GAOL_Y + 1, 68), (414.5, L.GAOL_Y + 2, 82))
    shot("crypt", (431, L.CRYPT_Y + 2, 53), (418, L.CRYPT_Y + 1, 43))
    shot("throne_hall_gallery", (432.5, HG + 1, 60.5), (458, HY + 3, 75))
    shot("throne_hall_door", (431.5, HY + 1, 67.5), (458, HY + 4, 75))
    shot("throne_hall_dark", (431.5, HY + 1, 67.5), (458, HY + 4, 75), nv=False)
    shot("king_on_throne", (450.5, HY + 2, 74.5), (458.5, HY + 3.5, 75))
    shot("king_closeup", (455.2, HY + 3.4, 73.2), (458.5, HY + 4.3, 75))
    shot("north_tower", (500, P + 20, 20), (477, P + 26, 38), nv=False)
    shot("secret_tunnel", (471, L.TUN_Y + 1, 40), (471, L.TUN_Y + 2, 20))
    shot("spiral", (475.5, HY - 10, 73.5), (478, HY - 25, 76))
    shot("pier_door_outside", (426, L.DOOR_Y + 1, -32), (432, L.DOOR_Y + 2, -32), nv=False)

def fight():
    """Cam2 the actor: the waking, standing, the sweep, the quake, the guard on the gallery, the bar with the HUD, the death, the throne after"""
    R("difficulty normal"); R("gamemode survival Cam2"); R("tag Cam2 add le.cpass"); R("scoreboard players set Cam2 le.co 0"); R("effect give Cam2 minecraft:resistance infinite 4 true")
    R("effect give Cam2 minecraft:invisibility infinite 0 true"); R("function last_ember:castle/kg/reset_all"); time.sleep(2)
    print("  king", R("scoreboard players get #king le.cs"), R("execute if entity " + KING), flush=True)
    place((448.5, HY + 2, 74.5), (458.5, HY + 3.5, 75)); time.sleep(4)
    gap(); R(f"tp Cam2 {L.HALL[0] + 2.5} {HY + 1} 67.5")
    time.sleep(0.9); snap("king_wakes", pre=False)
    time.sleep(2.5); R(f"execute as {KING} run data merge entity @s {{NoAI:1b}}"); R(f"tp {KING} 452.5 {HY + 1} 74.5 90 0")
    print("  king at", R(f"data get entity {KING} Pos"), R("scoreboard players get #king le.cs"), flush=True)
    snap("king_stands", pre=False)
    R("scoreboard players set #sw le.cs 100000")             # no sweep of his own while he poses (a sweep's end lets him walk)
    R(f"execute as {KING} run data merge entity @s {{NoAI:1b}}"); R(f"tp {KING} 448.5 {HY + 1} 74.5 90 0"); R(f"tp Cam2 445.5 {HY + 1} 76.5 -90 0")
    place((444.8, HY + 2.6, 72.2), (448.5, HY + 2.6, 74.5)); time.sleep(3); snap("king_closeup_fight", pre=False)
    gap(); R(f"execute as {KING} at @s run function last_ember:castle/kg/sweep_try"); time.sleep(0.5); snap("sweep_windup", pre=False)
    time.sleep(1.2)
    real = int(R("scoreboard players get #real le.cs").split("has ")[1].split(" ")[0])
    R("scoreboard players set #sw le.cs 100000"); R(f"execute as {KING} run data merge entity @s {{NoAI:1b}}"); R(f"tp {KING} 448.5 {HY + 1} 74.5 90 0")
    gap(); R(f"data modify entity {KING} Health set value {500 + real // 2 - 1}f"); time.sleep(0.6); snap("kneel", pre=False)
    time.sleep(3)
    place((452.5, HY + 2, 82.5), (446.5, HG + 1.5, 61)); time.sleep(3); snap("guards_gallery", pre=False)
    R(f"execute as {KING} run data merge entity @s {{NoAI:1b}}"); R(f"tp {KING} 448.5 {HY + 1} 74.5 90 0"); R(f"tp Cam2 442.5 {HY + 1} 74.5 -90 0")
    place((452.5, HY + 12, 78.5), (447.5, HY + 1, 74.5)); time.sleep(2)
    gap(); R("function last_ember:castle/kg/quake_start"); time.sleep(1.0); snap("quake_windup", pre=False)
    for k, name in enumerate(("quake_ring", "quake_ring2")):      # the ring at two radii (the dust lingers: an expanding lilac disc)
        R("scoreboard players set #sw le.cs 100000"); R("scoreboard players set #qk le.cs 100000")
        R(f"execute as {KING} run data merge entity @s {{NoAI:1b}}"); R(f"tp {KING} 448.5 {HY + 1} 74.5 90 0")
        place((452.5, HY + 12, 78.5), (447.5, HY + 1, 74.5)); gap()
        R("function last_ember:castle/kg/quake_start"); time.sleep(2.5 + 0.5 * k); snap(name, pre=False); time.sleep(3)
    R("kill @e[tag=le.kguard]")
    R("gamemode survival Cam"); R("effect give Cam minecraft:resistance infinite 4 true"); R("tag Cam add le.cpass"); R("scoreboard players set Cam le.co 0"); R("effect give Cam minecraft:night_vision infinite 0 true")
    R(f"tp Cam 440.5 {HY + 1} 74.5 -90 0"); time.sleep(2); snap("bossbar_hud", hud=True, pre=False)
    R(f"execute as {KING} run data merge entity @s {{NoAI:1b}}")
    place((450.5, HY + 2, 70.5), (452.5, HY + 2, 74.5)); R(f"tp {KING} 452.5 {HY + 1} 74.5 90 0"); time.sleep(2)
    gap(); R(f"data modify entity {KING} Health set value 500.5f"); R(f"damage {KING} 2 minecraft:player_attack by Cam2"); time.sleep(1.2)
    snap("king_dies", pre=False); time.sleep(3)
    shot("throne_after", (452.5, HY + 3, 74.5), (458.5, HY + 3.5, 75))
    time.sleep(2); shot("reliquary_signet", (465.5, HY + 2, 73.5), (468.5, HY + 1.5, 76.5))
    R("effect clear Cam2"); R("function last_ember:castle/kg/t_pier_door_open")
    shot("pier_door_inside", (437.5, L.DOOR_Y + 1, -32), (432, L.DOOR_Y + 2.2, -32))
    shot("pier_door_open_outside", (426, L.DOOR_Y + 1, -32), (432, L.DOOR_Y + 2, -32), nv=False)

if __name__ == "__main__":
    R("forceload add 400 -40 490 95"); R("gamerule advance_time false")
    names = sys.argv[1:] or ["static", "fight"]
    if "static" in names: static()
    if "fight" in names: fight()
    R("effect clear Cam"); R("forceload remove 400 -40 490 95")
