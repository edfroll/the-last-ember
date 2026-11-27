#!/usr/bin/env python3
"""T-034: only the datapack of the owners of the treasuries (function/treasury/gen/*, advancement/treasury/*, predicate/treasury/*) from
server/build/r1/ogre.json, grotto.json, tower.json (after the steps r1_ogre.py, r1_grotto.py and the castle's)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import treasury_dp as T
OUT = os.path.join(T.ROOT, "server/build/r1")
T.run_ogre(json.load(open(os.path.join(OUT, "ogre.json"))))
T.run_grotto(json.load(open(os.path.join(OUT, "grotto.json"))))
T.run_tower(json.load(open(os.path.join(OUT, "tower.json"))))
