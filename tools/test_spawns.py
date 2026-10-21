#!/usr/bin/env python3
"""T-006 spawn test: for each place, Cam (survival, immune) stands there at midnight for N game minutes at accelerated tick rate;
lists every mob type that exists within 128 blocks afterwards (worldgen-spawned animals are removed first).
Usage: test_spawns.py [minutes=10] [place ...]   (server + client Cam online)"""
import importlib.util, os, re, socket, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("rcon", os.path.join(ROOT, "tools/rcon.py")); rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
p = rc.props(); S = socket.create_connection(("127.0.0.1", int(p["rcon.port"])), timeout=120); rc.pkt(S, 1, 3, p["rcon.password"]); rc.read(S)
def R(c): return rc.exchange(S, c)
PLACES = {"twilight_refuge": (0, 0), "mushroom_grove": (-420, 60), "weeping_vale": (0, 300), "barrows": (200, 450), "crooked_fens": (-380, 330), "castle_dream": (450, 0), "early_winter": (-560, -815)}
TYPES = ("zombie husk drowned zombie_villager skeleton stray bogged parched wither_skeleton creeper spider cave_spider enderman endermite silverfish witch slime magma_cube phantom pillager vindicator evoker ravager "
         "vex blaze ghast hoglin zoglin piglin piglin_brute zombified_piglin guardian breeze creaking shulker cow chicken pig sheep rabbit fox wolf frog cat horse donkey bat villager wandering_trader squid glow_squid cod salmon").split()
BIOME = {"barrows": "last_ember:barrows_faded", "castle_dream": "last_ember:castle_dream"}  # barrows was faded earlier by the fade test
MONSTERS = set(TYPES[:TYPES.index("cow")])
def now(): return int(re.search(r"(\d+)", R("time query gametime")).group(1))
minutes = float(sys.argv[1]) if len(sys.argv) > 1 and re.match(r"^[\d.]+$", sys.argv[1]) else 10
names = [a for a in sys.argv[1:] if a in PLACES] or list(PLACES)
R("gamerule advance_time false"); R("gamerule advance_weather false"); R("weather clear"); R("difficulty normal")
for name in names:
    x, z = PLACES[name]
    R(f"execute in minecraft:overworld run forceload add {x-64} {z-64} {x+64} {z+64}"); time.sleep(5)
    R("kill @e[type=!player,type=!item_display,type=!interaction]")
    R("gamemode survival Cam"); R("effect give Cam minecraft:resistance infinite 255 true"); R("time set 18000"); R(f"tp Cam {x} 150 {z}")
    # stand on the ground: drop onto terrain
    R(f"effect give Cam minecraft:slow_falling 6 0 true"); time.sleep(8)
    R("kill @e[type=!player,type=!item_display,type=!interaction]")  # drop what the chunks around the arrival point brought along from worldgen
    R("tick rate 100"); t0 = now(); target = t0 + int(minutes * 1200)
    while now() < target:
        time.sleep(3); R("time set 18000")
    R("tick rate 20")
    found = {}
    for t in TYPES:
        R("scoreboard players set #n le.z 0")
        R(f"execute at Cam as @e[type=minecraft:{t},distance=..128] at @s if biome ~ ~ ~ {BIOME.get(name, 'last_ember:' + name)} run scoreboard players add #n le.z 1")
        n = int(re.search(r"has (\d+)", R("scoreboard players get #n le.z")).group(1))
        if n: found[t] = n
    mon = {k: v for k, v in found.items() if k in MONSTERS}
    print(f"{name:18} {minutes:g} min ({now()-t0} ticks): in biome {found if found else 'none'} | monsters in biome: {sum(mon.values())}", flush=True)
    R("kill @e[type=!player,type=!item_display,type=!interaction]"); R(f"execute in minecraft:overworld run forceload remove {x-64} {z-64} {x+64} {z+64}")
R("gamerule advance_time true")
