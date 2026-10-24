#!/usr/bin/env python3
"""T-018: creature sounds from Edward's library (server/sounds_src = <creature>/<event>/[<surface>/]<event>_NN.wav, not in git)
-> resourcepack/assets/last_ember/sounds/creature/<name>/<event>[/<surface>]/<file>.ogg  (mono via oggenc --downmix, Vorbis q4: positional sounds in Minecraft must be mono).
Names are made safe for resource ids (lower case, [a-z0-9_]). Usage: python3 tools/import_creature_sounds.py <name>[=<library folder>] ...
e.g.  python3 tools/import_creature_sounds.py drowner alghoul wild_dog toad water_hag=waterhag leshen=lessun endrega=endriaga"""
import os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "server/sounds_src"); DST = os.path.join(ROOT, "resourcepack/assets/last_ember/sounds/creature")
def safe(s): return re.sub(r"_+", "_", re.sub(r"[^a-z0-9_]", "_", s.lower())).strip("_")
for arg in sys.argv[1:]:
    name, _, folder = arg.partition("="); folder = folder or name
    base = os.path.join(SRC, folder); n = 0
    for dp, dns, fns in os.walk(base):
        for f in sorted(fns):
            if not f.lower().endswith(".wav"): continue
            rel = os.path.relpath(dp, base).split(os.sep)
            out_dir = os.path.join(DST, safe(name), *[safe(p) for p in rel if p != "."])
            os.makedirs(out_dir, exist_ok=True)
            out = os.path.join(out_dir, safe(os.path.splitext(f)[0]) + ".ogg")
            if os.path.exists(out): n += 1; continue
            subprocess.run(["oggenc", "-Q", "-q", "4", "--downmix", "-o", out, os.path.join(dp, f)], check=True); n += 1
    print(f"{name} ({folder}): {n} sounds")
