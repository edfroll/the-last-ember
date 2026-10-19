#!/usr/bin/env python3
"""Roll vanilla chest-like loot tables N times via RCON and report banned items seen.
Usage: test_loot.py [rolls=100]  (server running; chunk containing 1,100,1 loaded — forceload it)
"""
import importlib.util, os, re, socket, struct, sys, json, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("rcon", os.path.join(ROOT, "tools/rcon.py"))
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)

BANNED = re.compile(r"^minecraft:(raw_(iron|gold|copper)(_block)?|(iron|gold|copper)_(ingot|nugget|block)|diamond(_block)?|"
                    r"emerald(_block)?|lapis_lazuli|lapis_block|redstone(_block)?|netherite_scrap|ancient_debris|\w+_ore)$")
POS = "1 100 1"

class Conn:
    def __init__(self):
        p = rc.props()
        self.s = socket.create_connection(("127.0.0.1", int(p["rcon.port"])), timeout=30)
        rc.pkt(self.s, 1, 3, p["rcon.password"]); rc.read(self.s)
    def run(self, cmd):
        rc.pkt(self.s, 2, 2, cmd); return rc.read(self.s)[2]

def tables():
    base = os.path.join(ROOT, "server/generated/data/minecraft/loot_table")
    for d in ("chests", "archaeology", "pots"):
        for dp, _, fns in os.walk(os.path.join(base, d)):
            for fn in sorted(fns):
                if fn.endswith(".json"):
                    yield "minecraft:" + os.path.relpath(os.path.join(dp, fn), base)[:-5]

def main():
    rolls = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    c = Conn()
    c.run(f"setblock {POS} minecraft:chest")
    total = collections.Counter(); per = {}; errors = []
    n_tables = 0
    for t in tables():
        seen = collections.Counter(); ok = 0
        for _ in range(rolls):
            c.run(f"data modify block {POS} Items set value []")
            r = c.run(f"loot insert {POS} loot {t}")
            if "Inserted" not in r and "Dropped" not in r and "items" not in r.lower():
                errors.append((t, r)); break
            ok += 1
            for m in re.findall(r'id: "(minecraft:[a-z_]+)"', c.run(f"data get block {POS} Items")):
                if BANNED.match(m): seen[m] += 1
        n_tables += 1
        if seen: per[t] = dict(seen); total.update(seen)
    print(f"tables: {n_tables}, rolls each: {rolls}, tables with banned items: {len(per)}, total banned stacks: {sum(total.values())}")
    for t, v in sorted(per.items())[:60]: print("  ", t, v)
    if errors: print("  not rollable via loot insert:", [e[0] for e in errors][:20], errors[0][1][:80])
    c.run(f"setblock {POS} minecraft:air")

main()
