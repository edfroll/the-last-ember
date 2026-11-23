#!/usr/bin/env python3
"""T-032: only the datapack part of the thicket again (tools/build/spiders_dp.py) from server/build/r1/spiders.json, without the step
(for the work on the mechanics; the step writes the same through tools/build/r1_spiders.py).
  python3 tools/build/spiders_dp_only.py"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spiders_plan as P, spiders_dp
p = os.path.join(P.OUT, "spiders.json"); meta = json.load(open(p))
spiders_dp.run(meta)
json.dump(meta, open(p, "w"), ensure_ascii=False)
print("spiders dp:", len(os.listdir(os.path.join(P.ROOT, "datapack/data/last_ember/function/spiders/gen"))), "generated functions")
