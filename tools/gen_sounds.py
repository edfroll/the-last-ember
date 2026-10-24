#!/usr/bin/env python3
"""T-018: resourcepack/assets/last_ember/sounds.json (generated, do not edit) from three parts:
  1. the music slots of the biomes (biomes/registry.json "slots": placeholders until the real music);
  2. creature/<creature>/<event>[/<surface>]/*.ogg -> creature.<creature>.<event>[.<surface>] (every file of the folder is a variant;
     an event folder with surface sub-folders also gets an event of all its files); steps are heard from 12 blocks, the rest 16 x volume (voices are played at 1.8);
  3. the effects of Edward's pack: sounds/sfx_events.json (its own sounds.json, events kept as they are; amb/* and quest/ritual are streamed).
Usage: python3 tools/gen_sounds.py"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SND = os.path.join(ROOT, "resourcepack/assets/last_ember/sounds")
out = {}
reg = json.load(open(os.path.join(ROOT, "biomes/registry.json"), encoding="utf-8"))
for s in reg["slots"]: out[f"music.{s}"] = {"category": "music", "sounds": [{"name": "minecraft:music/game/ancestry", "stream": True, "volume": 0.6}]}
def dist(ev):
    # the server sends a sound of the pack within 16 blocks x volume, the client hears it within attenuation_distance x max(volume, 1):
    # steps keep 12 (played at volume <= 1), voices keep the default 16 and are played at volume 1.8 (~29 blocks)
    e = ev.split(".")[0]
    if any(e.startswith(p) for p in ("mv_", "movement", "footstep", "foley")) or "footstep" in e or "step" in e: return 12
    return 16
def snd(nm, ev): return {"name": nm} if dist(ev) == 16 else {"name": nm, "attenuation_distance": dist(ev)}
cre = os.path.join(SND, "creature"); n_cre = 0
if os.path.isdir(cre):
    for c in sorted(os.listdir(cre)):
        cd = os.path.join(cre, c)
        if not os.path.isdir(cd): continue
        for ev in sorted(os.listdir(cd)):
            ed = os.path.join(cd, ev)
            if not os.path.isdir(ed): continue
            allf = []
            for dp, dns, fns in sorted(os.walk(ed)):
                files = sorted(f for f in fns if f.endswith(".ogg"))
                if not files: continue
                rel = os.path.relpath(dp, ed); key = f"creature.{c}.{ev}" + ("" if rel == "." else "." + rel.replace(os.sep, "."))
                names = [f"last_ember:" + os.path.relpath(os.path.join(dp, f), SND)[:-4].replace(os.sep, "/") for f in files]
                allf += names
                out[key] = {"sounds": [snd(nm, ev) for nm in names]}; n_cre += 1
            if allf and f"creature.{c}.{ev}" not in out: out[f"creature.{c}.{ev}"] = {"sounds": [snd(nm, ev) for nm in allf]}; n_cre += 1
sfx = json.load(open(os.path.join(ROOT, "sounds/sfx_events.json"), encoding="utf-8")); n_sfx = 0
for k, v in sfx.items():
    if k.startswith("sfx.amb.") or k == "sfx.quest.ritual":
        for s in v["sounds"]:
            if isinstance(s, dict): s["stream"] = True
    out[k] = v; n_sfx += 1
    if k.startswith("sfx.mind."):   # every variant also on its own (Edward listens to them one by one: sfx.mind.whisper.1 ...)
        for i, snd in enumerate(v["sounds"], 1): out[f"{k}.{i}"] = {"sounds": [snd]}
missing = []
for k, v in out.items():
    for s in v["sounds"]:
        nm = s["name"] if isinstance(s, dict) else s
        if nm.startswith("last_ember:") and not os.path.exists(os.path.join(SND, nm[len("last_ember:"):] + ".ogg")): missing.append(nm)
if missing: raise SystemExit("missing files: %s" % missing[:5])
json.dump(out, open(os.path.join(ROOT, "resourcepack/assets/last_ember/sounds.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"sounds.json: {len(reg['slots'])} music slots, {n_cre} creature events, {n_sfx} effect events")
