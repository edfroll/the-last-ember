#!/usr/bin/env python3
"""T-033: only the datapack part of the mines (function/mines/gen/*) from server/build/r1/mines.json (after a step of r1_mines.py)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_mines as R, mines_dp
mines_dp.run(json.load(open(os.path.join(R.OUT, "mines.json"))))
