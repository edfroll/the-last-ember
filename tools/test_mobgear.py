#!/usr/bin/env python3
"""T-001b dynamic test: natural-gear mobs killed by a player must not drop metal gear.
Needs: server running + player 'Cam' online (tools/client_launch.py). Summons N bare mobs (vanilla finalizeSpawn = natural gear),
control: killed immediately (before the datapack scan fixes drop chances); treated: killed after 1.5 s. 'damage ... by Cam' makes the
kill count as player-kill (equipment only drops then). Usage: test_mobgear.py [N=200]
"""
import importlib.util, json, os, sys, time, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("rcon", os.path.join(ROOT, "tools/rcon.py")); rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
import socket
class Conn:  # one persistent RCON connection (thousands of reconnects get reset by the server)
    def __init__(self):
        p = rc.props(); self.s = socket.create_connection(("127.0.0.1", int(p["rcon.port"])), timeout=30)
        rc.pkt(self.s, 1, 3, p["rcon.password"]); rc.read(self.s)
    n = 0
    def run(self, cmd):
        Conn.n += 1
        try:
            return rc.exchange(self.s, cmd)
        except Exception as e:
            print(f"RCON died at command #{Conn.n}: {cmd[:100]} ({e!r})", flush=True); raise
rc.run = Conn().run
GEAR = json.load(open(os.path.join(ROOT, "datapack/data/last_ember/tags/item/metal_gear.json")))["values"]
TYPES = ["zombie", "skeleton", "husk", "drowned", "stray", "zombified_piglin", "piglin", "pillager", "vindicator", "wither_skeleton"]

def count_items():
    out = {}
    for g in GEAR:
        r = rc.run(f'execute if entity @e[type=item,nbt={{Item:{{id:"{g}"}}}}]')
        if "passed" in r:
            n = rc.run(f'execute store result score #n le.init if entity @e[type=item,nbt={{Item:{{id:"{g}"}}}}]')
            m = re.search(r"(\d+)", rc.run("scoreboard players get #n le.init")); out[g.split(":")[1]] = int(m.group(1)) if m else 1
    return out

EQUIP = ('{equipment:{mainhand:{id:"minecraft:iron_sword"},head:{id:"minecraft:diamond_helmet"},chest:{id:"minecraft:iron_chestplate"},'
         'legs:{id:"minecraft:golden_leggings"},feet:{id:"minecraft:chainmail_boots"}}}')

def batch(t, n, wait, equipped=False):
    rc.run("kill @e[type=item]"); rc.run("kill @e[type=experience_orb]")
    for i in range(n):
        rc.run(f"summon minecraft:{t} {2 + (i % 12)} 200 {2 + (i // 12) % 12}" + (" " + EQUIP if equipped else ""))
    time.sleep(wait)
    rc.run(f"execute as @e[type=minecraft:{t},x=0,y=199,z=0,dx=16,dy=3,dz=16] run damage @s 1000 minecraft:player_attack by Cam")
    time.sleep(1)
    res = count_items()
    rc.run("kill @e[type=item]"); rc.run("kill @e[type=experience_orb]")
    return res

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    rc.run("execute in minecraft:overworld run forceload add 0 0 15 15")
    rc.run("fill 0 199 0 15 199 15 minecraft:stone"); rc.run("fill 0 200 0 15 215 15 minecraft:air")
    rc.run("time set midnight")  # undead burn in daylight
    rc.run("difficulty hard")
    tot_c = tot_t = 0
    for t in TYPES:
        c = batch(t, n, 0.0); tr = batch(t, n, 1.5)
        tot_c += sum(c.values()); tot_t += sum(tr.values())
        print(f"{t}: control(drops before fix) {sum(c.values())} {c if c else ''} | treated {sum(tr.values())} {tr if tr else ''}")
    print("-- explicit /summon with iron/diamond/gold/chainmail gear in 5 slots")
    for t in ("zombie", "skeleton"):
        c = batch(t, n, 0.0, True); tr = batch(t, n, 1.5, True)
        tot_c += sum(c.values()); tot_t += sum(tr.values())
        print(f"{t}+gear: control {sum(c.values())} {c} | treated {sum(tr.values())} {tr if tr else ''}")
    print(f"TOTAL control {tot_c}  treated {tot_t}  (N={n} per type per run)")
    rc.run("fill 0 199 0 15 199 15 minecraft:air"); rc.run("kill @e[type=item]"); rc.run("kill @e[type=experience_orb]")

main()
