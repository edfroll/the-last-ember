#!/usr/bin/env python3
"""Check placement files against docs/reference/blocks.json (ids, property names and values). Usage: validate.py files..."""
import json, re, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BL = json.load(open(os.path.join(ROOT, "docs/reference/blocks.json")))
bad = {}
for f in sys.argv[1:]:
    for n, line in enumerate(open(f), 1):
        s = line.split(" ", 3)[3].strip()
        m = re.match(r"([a-z_:0-9]+)(?:\[([^\]]*)\])?", s); bid, props = m.group(1), m.group(2)
        if bid not in BL: bad.setdefault(f"unknown block {bid}", f"{f}:{n}"); continue
        allowed = BL[bid].get("properties", {})
        for kv in filter(None, (props or "").split(",")):
            k, v = kv.split("=")
            if k not in allowed: bad.setdefault(f"{bid}: no property {k}", f"{f}:{n}")
            elif v not in allowed[k]: bad.setdefault(f"{bid}: {k}={v} not in {allowed[k]}", f"{f}:{n}")
for k, v in bad.items(): print(k, "  first at", v)
print("ok" if not bad else f"{len(bad)} problems"); sys.exit(1 if bad else 0)
