#!/usr/bin/env python3
"""T-021: region borders, chapter gates, shortcuts.  python3 tools/gen_gates.py [extra_file ...]   (then python3 tools/gen_zones.py)

Reads gates/gates.txt (+ extra test files, format in the comment of gates/gates.txt) and writes:
  datapack/data/last_ember/function/gate/gen/*   gate state/visuals/events, the Refuge side of the 6 shortcuts, region doors,
                                                 the transfer triggers, the sky guard over the border axes (do not edit)
  datapack/data/last_ember/function/gate/hook/<id>.mcfunction   stub hooks of the gates (only when missing; hand-written later)
  datapack/data/last_ember/structure/gate/test_{closed,open}.nbt   only with a test file (templates of the test gates)
  zones/gates.gen.txt                            adventure strips +-40 round the border axes (flag border), r8 round region doors
  gates/borders.gen.json                         the border lines for tools/borders.sh and tools/borders_check.py
The Refuge side (T-008 gates on the plaza) comes from tools/build/gates.py: the exact world cells of the portcullis, doors,
lanterns and the banner of every gate are computed from the same model the Refuge was built from."""
import json, math, os, re, shlex, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools/build"))
import gates as hubgates, plaza, geo, shortcut_door as sdoor
from connect import connect
D = os.path.join(ROOT, "datapack/data/last_ember")
GEN = os.path.join(D, "function/gate/gen"); HOOK = os.path.join(D, "function/gate/hook"); STRUCT = os.path.join(D, "structure/gate")
REGIONS = ["r1", "r2", "r3", "r4", "r5", "r6"]
DIMS = {"overworld", "the_nether", "the_end"}
J = lambda o: json.dumps(o, ensure_ascii=False)
def tx(t, c="gray", **k): d = {"text": t, "color": c}; d.update(k); return d

# ------------------------------------------------------------------ parse
def parse(path, test):
    borders, gates_, shorts = [], [], []
    for ln, raw in enumerate(open(path, encoding="utf-8"), 1):
        line = raw.split("#", 1)[0].strip() if not raw.lstrip().startswith("#") else ""
        if not line: continue
        f = shlex.split(line); kind = f[0]
        kv = {}; pos = []
        for t in f[1:]:
            if "=" in t: k, v = t.split("=", 1); kv.setdefault(k, []).append(v)
            else: pos.append(t)
        one = lambda k, d=None: kv[k][0] if k in kv else d
        where = "%s:%d" % (path, ln)
        if kind == "border":
            bid, ax, a, lo, hi = pos[0], pos[1], int(pos[2]), int(pos[3]), int(pos[4])
            if ax not in ("x", "z"): raise SystemExit(where + ": axis must be x or z")
            gaps = []
            for g in kv.get("gap", []):
                m = re.fullmatch(r"(-?\d+)\.\.(-?\d+)", g)
                if not m: raise SystemExit(where + ": bad gap " + g)
                gaps.append((int(m.group(1)), int(m.group(2))))
            borders.append({"id": bid, "axis": ax, "a": a, "lo": min(lo, hi), "hi": max(lo, hi), "gaps": gaps, "strip": int(one("strip", 40)), "test": test})
        elif kind == "gate":
            gid, reg = pos[0], pos[1]
            if reg not in REGIONS[1:] + ["final"]: raise SystemExit(where + ": region must be r2..r6 or final")
            g = {"id": gid, "reg": reg, "ch": int(one("chapter")), "dim": one("dim", "overworld"), "text": one("text", "Где-то открылся путь."),
                 "closed": one("closed"), "open": one("open"), "at": None, "test": test}
            if one("at"):
                x, y, z = one("at").split(","); g["at"] = (int(x), None if y == "~" else int(y), int(z))
            if (g["closed"] or g["open"]) and (not g["at"] or g["at"][1] is None): raise SystemExit(where + ": templates need at=x,y,z")
            gates_.append(g)
        elif kind == "shortcut":
            reg = pos[0]
            if reg not in REGIONS: raise SystemExit(where + ": region r1..r6")
            x, y, z = map(int, one("door").split(",")); op = one("open", "near:24")
            if op != "click" and not re.fullmatch(r"near:\d+", op): raise SystemExit(where + ": open=click|near:<r>")
            shorts.append({"reg": reg, "hub": one("hub", reg), "door": (x, y, z), "yaw": sdoor.norm_yaw(one("yaw", "0")), "open": op,
                           "build": one("build", "1") == "1", "dim": one("dim", "overworld"), "test": test})
        else: raise SystemExit(where + ": unknown line " + kind)
    return borders, gates_, shorts

# ------------------------------------------------------------------ the Refuge side of a shortcut (T-008 model)
def hub(reg):
    ang = {r: a for a, r in plaza.GATES.items()}[reg]
    b = hubgates.build(ang, reg); connect(b)
    cells = {}                                       # local (u, v, dy) -> world (x, y, z)
    for (x, y, z), s in b.v.items():
        u, v = geo.unrot(0, 0, ang, x, z); key = (int(round(u - hubgates.R0)), int(round(v)), y - geo.FLOOR)
        cells.setdefault(key, []).append((x, y, z))
    mk = {m[0]: (m[1], m[2], m[3]) for m in b.markers}
    bars = [(k, s) for k, s in b.v.items() if "iron_bars" in s]
    doors = [(k, s) for k, s in b.v.items() if "dark_oak_door" in s and "half=lower" in s]
    def cell(u, v, dy):
        """the air cell of the piece nearest to local (u, v) at that height (diagonal gates are rasterized)"""
        best = None
        for (x, y, z), s in b.v.items():
            if y != geo.FLOOR + dy or s != "minecraft:air": continue
            uu, vv = geo.unrot(0, 0, ang, x, z); d = (uu - hubgates.R0 - u) ** 2 + (vv - v) ** 2
            if best is None or d < best[0]: best = (d, (x, y, z))
        if best is None or best[0] > 1.0: raise SystemExit("hub %s: no air cell near %s" % (reg, (u, v, dy)))
        above = b.v.get((best[1][0], best[1][1] + 1, best[1][2]), "")
        if "air" in above or not above: raise SystemExit("hub %s: no ceiling above %s" % (reg, best[1]))
        return best[1]
    lant = [cell(5, 0, 6), cell(9, 0, 6)]
    bx, by, bz = mk["gate_banner_" + reg]; bface = geo.face_rot("in", ang)
    back = {"north": (0, 1), "south": (0, -1), "east": (-1, 0), "west": (1, 0)}[bface]
    behind = b.v.get((bx + back[0], by, bz + back[1]), "")
    if not behind or "air" in behind: raise SystemExit("hub %s: nothing behind the banner at %s (%s)" % (reg, (bx, by, bz), behind))
    ex, ey, ez = mk["gate_exit_" + reg]
    trig = None
    if ang % 90 == 0:
        tc = [w for (u, v, dy), ws in cells.items() if 9 <= u <= 11 and -2 <= v <= 2 and 1 <= dy <= 3 for w in ws]
        xs, ys, zs = [c[0] for c in tc], [c[1] for c in tc], [c[2] for c in tc]
        trig = ("box", min(xs), min(ys), min(zs), max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    else:
        cx, cz = geo.rot(0, 0, ang, hubgates.R0 + 10, 0)
        trig = ("cyl", cx + 0.5, geo.FLOOR + 1, cz + 0.5, 2.5)
    ix, iz = geo.rot(0, 0, ang, hubgates.R0, 0)
    return {"reg": reg, "ang": ang, "bars": bars, "doors": doors, "lanterns": lant, "banner": (bx, by, bz, bface), "exit": (ex + 0.5, ey, ez + 0.5, ang),
            "trig": trig, "click": (ix + 0.5, geo.FLOOR + 1, iz + 0.5)}

# region banners: the sign of the region (card «Ворота шорткатов»), builder's choice of patterns
BANNERS = {
    "r1": ("green", [("stripe_bottom", "black"), ("stripe_center", "lime"), ("triangle_top", "green"), ("half_horizontal_bottom", "black"), ("border", "black")]),
    "r2": ("blue", [("triangle_bottom", "gray"), ("triangles_bottom", "cyan"), ("border", "black")]),
    "r3": ("white", [("bricks", "light_gray"), ("triangles_top", "white"), ("stripe_bottom", "gray"), ("border", "light_blue")]),
    "r4": ("orange", [("circle", "yellow"), ("stripe_center", "brown"), ("stripe_bottom", "brown"), ("border", "red")]),
    "r5": ("gray", [("stripe_downleft", "black"), ("stripe_downright", "black"), ("stripe_top", "black"), ("border", "black")]),
    "r6": ("black", [("triangle_bottom", "gray"), ("gradient_up", "red"), ("rhombus", "orange"), ("border", "black")]),
}
def banner_block(reg, face):
    base, pats = BANNERS[reg]
    p = ",".join('{pattern:"minecraft:%s",color:"%s"}' % (a, c) for a, c in pats)
    return "minecraft:%s_wall_banner[facing=%s]{patterns:[%s]}" % (base, face, p)

# ------------------------------------------------------------------ outputs
FILES = {}
def w(name, lines): FILES[name] = lines
def sel_box(t):
    _, x, y, z, dx, dy, dz = t; return "x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d" % (x, y, z, dx, dy, dz)

def main():
    files = [os.path.join(ROOT, "gates/gates.txt")] + sys.argv[1:]
    borders, gates_, shorts = [], [], []
    for i, f in enumerate(files):
        b, g, s = parse(f, i > 0); borders += b; gates_ += g; shorts += s
    ids = [g["id"] for g in gates_] + [b["id"] for b in borders]
    if len(ids) != len(set(ids)): raise SystemExit("duplicate ids")
    if len({s["reg"] for s in shorts}) != len(shorts): raise SystemExit("one shortcut per region")
    test = len(files) > 1
    check_bonfires(borders)
    hubs = {r: hub(r) for r in REGIONS}
    sc = {s["reg"]: s for s in shorts}
    init = ["# generated by tools/gen_gates.py: scores of the gates and shortcuts (kept across reloads)",
            "scoreboard objectives add le.gate dummy", "scoreboard objectives add le.sct dummy", "scoreboard objectives add le.scw dummy",
            "scoreboard objectives add le.sccd dummy", "scoreboard objectives add le.bside dummy",
            "scoreboard players set #open_r0 le.gate 1", "scoreboard players set #open_r1 le.gate 1"]
    def keep0(s): init.append("execute unless score %s matches -2147483648.. run scoreboard players set %s 0" % (s, s))
    for r in REGIONS[1:] + ["final"]: keep0("#open_%s le.gate" % r)
    sec = ["# generated: every second: pending templates and visuals (when the chunk is loaded), region doors, opening by approach"]
    fast = ["# generated: every 5 ticks: players in the transfer triggers of open shortcuts start the transfer"]
    still = ["# generated: as a player in transfer (le.scw = code): left the trigger -> cancelled"]
    arrive = ["# generated: as a player whose transfer ended: the teleport by the code le.scw"]
    status = ["# generated: gate/status", "tellraw @s %s" % J(tx("Ворота и шорткаты:", "gold"))]
    chapters = {}
    # ---- chapter gates
    for g in gates_:
        i, st, vs = g["id"], "#gate_%s le.gate" % g["id"], "#gatev_%s le.gate" % g["id"]
        keep0(st); keep0(vs)
        flag = "#open_%s le.gate" % g["reg"]
        chapters.setdefault(g["ch"], []).append(i)
        ev = ["# generated: open the gate %s (chapter %d -> %s); a repeat does nothing" % (i, g["ch"], g["reg"]),
              "execute if score %s matches 1 run return 0" % st, "scoreboard players set %s 1" % st, "scoreboard players set %s 1" % flag,
              "data modify storage last_ember:gates g.%s set value {open:1b}" % i,
              "execute as @a at @s run playsound minecraft:entity.lightning_bolt.thunder weather @s ~ ~ ~ 0.8 0.6",
              "title @a actionbar %s" % J(tx(g["text"], "gold"))]
        if g["at"]:
            x, y, z = g["at"]; d = g["dim"]
            if y is None:
                ev += ["execute in minecraft:%s positioned %d 0 %d positioned over world_surface as @a[distance=..64] run playsound minecraft:block.iron_door.open block @s ~ ~ ~ 2 0.5" % (d, x, z),
                       "execute in minecraft:%s positioned %d 0 %d positioned over world_surface run particle minecraft:large_smoke ~ ~2 ~ 3 2 3 0.02 80 force" % (d, x, z)]
            else:
                ev += ["execute in minecraft:%s positioned %d %d %d as @a[distance=..64] run playsound minecraft:block.iron_door.open block @s ~ ~ ~ 2 0.5" % (d, x, y, z),
                       "execute in minecraft:%s positioned %d %d %d run particle minecraft:large_smoke ~ ~2 ~ 3 2 3 0.02 80 force" % (d, x, y, z),
                       "execute in minecraft:%s positioned %d %d %d run particle minecraft:flash{color:[1.0,0.9,0.7,1.0]} ~ ~2 ~ 0 0 0 0 1 force" % (d, x, y, z)]
        ev.append("function last_ember:gate/hook/%s" % i)
        w("open_" + i, ev)
        cl = ["# generated: TEST ONLY: close the gate %s again" % i, "scoreboard players set %s 0" % st, "data modify storage last_ember:gates g.%s set value {open:0b}" % i]
        if not any(o["reg"] == g["reg"] and o["id"] != i for o in gates_): cl.append("scoreboard players set %s 0" % flag)
        else: cl.append("scoreboard players set %s 0" % flag + "\n" + "\n".join("execute if score #gate_%s le.gate matches 1 run scoreboard players set %s 1" % (o["id"], flag) for o in gates_ if o["reg"] == g["reg"] and o["id"] != i))
        w("close_" + i, cl)
        if g["closed"] or g["open"]:
            x, y, z = g["at"]; d = g["dim"]
            for state, tpl in ((1, g["open"]), (0, g["closed"])):
                if not tpl: continue
                fn = "vis_%s_%d" % (i, state)
                w(fn, ["# generated: the template of %s (%s)" % (i, "open" if state else "closed"), "place template %s %d %d %d" % (tpl, x, y, z),
                       "scoreboard players set %s %d" % (vs, state)])
                sec.append("execute if score %s matches %d unless score %s matches %d in minecraft:%s if loaded %d %d %d run function last_ember:gate/gen/%s"
                           % (st, state, vs, state, d, x, y, z, fn))
        status.append("execute if score %s matches 1 run tellraw @s %s" % (st, J([tx(" %s → %s: " % (i, g["reg"]), "gray"), tx("открыты", "green")])))
        status.append("execute if score %s matches 0 run tellraw @s %s" % (st, J([tx(" %s → %s: " % (i, g["reg"]), "gray"), tx("закрыты", "red")])))
        hp = os.path.join(HOOK, i + ".mcfunction")
        if not os.path.exists(hp) and not g["test"]:
            os.makedirs(HOOK, exist_ok=True)
            open(hp, "w").write("# the gate %s is open (gate/gen/open_%s): the region task fills this hook (the event of the gate)\n" % (i, i))
        if g["test"] and not os.path.exists(hp): w("../hook/" + i, ["# TEST gate hook (generated, removed without the test file)"])
    for n in range(1, 7):
        w("chapter_%d" % n, ["# generated: altar/hook/chapter_%d: the gates of chapter %d" % (n, n)] +
          ["function last_ember:gate/gen/open_%s" % i for i in chapters.get(n, [])])
    w("open_dispatch", ["# generated: macro gate/open {id}", "$function last_ember:gate/gen/open_$(id)"])
    w("close_dispatch", ["# generated: macro gate/close {id}", "$function last_ember:gate/gen/close_$(id)"])
    # ---- shortcuts: the Refuge side (all six), the region side (lines `shortcut`)
    code = 0; codes = {}
    for r in REGIONS:
        h = hubs[r]; n = int(r[1:]); S = "#sc_%s le.gate" % r; VH = "#scvh_%s le.gate" % r; HB = "#schb_%s le.gate" % r
        keep0(S); keep0(VH); keep0(HB)
        op = ["# generated: the Refuge side of the shortcut %s: open (portcullis up, doors open, lanterns, banner)" % r]
        cl = ["# generated: the Refuge side of the shortcut %s: closed (T-008 state)" % r]
        for (x, y, z), s in h["bars"]: op.append("setblock %d %d %d minecraft:air" % (x, y, z)); cl.append("setblock %d %d %d %s" % (x, y, z, s))
        for (x, y, z), s in h["doors"]:
            op.append("setblock %d %d %d %s" % (x, y, z, s.replace("open=false", "open=true"))); cl.append("setblock %d %d %d %s" % (x, y, z, s))
        lt = "soul_lantern" if r == "r6" else "lantern"
        for (x, y, z) in h["lanterns"]: op.append("setblock %d %d %d minecraft:%s[hanging=true]" % (x, y, z, lt)); cl.append("setblock %d %d %d minecraft:air" % (x, y, z))
        bx, by, bz, bf = h["banner"]
        op.append("setblock %d %d %d %s" % (bx, by, bz, banner_block(r, bf))); cl.append("setblock %d %d %d minecraft:air" % (bx, by, bz))
        op += ["kill @e[type=minecraft:interaction,tag=le.schub,scores={le.scw=%d}]" % n, "scoreboard players set %s 1" % VH]
        ix, iy, iz = h["click"]
        cl += ["kill @e[type=minecraft:interaction,tag=le.schub,scores={le.scw=%d}]" % n,
               "summon minecraft:interaction %.1f %d %.1f {Tags:[\"le.schub\",\"le.scclick\",\"le.scnew\"],width:5f,height:7f,response:1b}" % (ix, iy, iz),
               "scoreboard players set @e[type=minecraft:interaction,tag=le.scnew] le.scw %d" % n, "tag @e[type=minecraft:interaction,tag=le.scnew] remove le.scnew",
               "scoreboard players set %s 0" % VH, "scoreboard players set %s 1" % HB]
        w("hub_open_" + r, op); w("hub_close_" + r, cl)
        ex, ey, ez, ea = h["exit"]
        sec.append("execute if score %s matches 1 unless score %s matches 1 in minecraft:overworld if loaded %d %d %d run function last_ember:gate/gen/hub_open_%s" % (S, VH, ex, ey, ez, r))
        sec.append("execute if score %s matches 0 unless score %s matches 0 in minecraft:overworld if loaded %d %d %d run function last_ember:gate/gen/hub_close_%s" % (S, VH, ex, ey, ez, r))
        sec.append("execute if score %s matches 0 if score %s matches 0 in minecraft:overworld if loaded %d %d %d run function last_ember:gate/gen/hub_close_%s" % (S, HB, ex, ey, ez, r))
        # transfer codes: 2n = from the Refuge, 2n+1 = from the region
        d = sc.get(r)
        hc, rc = 2 * n, 2 * n + 1
        tr = h["trig"]
        if tr[0] == "box": hsel = "@a[%s,tag=!le.sct]" % sel_box(tr); hstill = "@s[%s]" % sel_box(tr); hpos = ""
        else: hsel = "@a[distance=..%.1f,tag=!le.sct]" % tr[4]; hstill = "@s[distance=..%.1f]" % tr[4]; hpos = "positioned %.1f %d %.1f " % (tr[1], tr[2], tr[3])
        if d:
            dx_, dy_, dz_ = d["door"]; yaw = d["yaw"]; dim = d["dim"]
            tc = [sdoor.world(d["door"], yaw, u, v, dy) for u in range(sdoor.TRIGGER[0][0], sdoor.TRIGGER[0][1] + 1)
                  for v in range(sdoor.TRIGGER[1][0], sdoor.TRIGGER[1][1] + 1) for dy in range(sdoor.TRIGGER[2][0], sdoor.TRIGGER[2][1] + 1)]
            xs, ys, zs = [c[0] for c in tc], [c[1] for c in tc], [c[2] for c in tc]
            dbox = ("box", min(xs), min(ys), min(zs), max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
            rex, rey, rez = sdoor.world(d["door"], yaw, *sdoor.EXIT)
            fast.append("execute if score %s matches 1 in minecraft:overworld %sas %s unless score @s le.sccd > #gt le.gate run function last_ember:gate/gen/go_%d" % (S, hpos, hsel, hc))
            fast.append("execute if score %s matches 1 in minecraft:%s as @a[%s,tag=!le.sct] unless score @s le.sccd > #gt le.gate run function last_ember:gate/gen/go_%d" % (S, dim, sel_box(dbox), rc))
            still.append("execute if score @s le.scw matches %d in minecraft:overworld %sunless entity %s run return 0" % (hc, hpos, hstill))
            still.append("execute if score @s le.scw matches %d in minecraft:%s unless entity @s[%s] run return 0" % (rc, dim, sel_box(dbox)))
            for cd, (dm, px, py, pz, pyaw) in ((hc, (dim, rex + 0.5, rey, rez + 0.5, yaw)), (rc, ("overworld", ex, ey, ez, ea))):
                arrive.append("execute if score @s le.scw matches %d run return run function last_ember:gate/gen/tp_%d" % (cd, cd))
                w("go_%d" % cd, ["# generated: the transfer %d starts (%s side of %s)" % (cd, "Refuge" if cd == hc else "region", r), "scoreboard players set @s le.scw %d" % cd, "function last_ember:gate/sc_start"])
                w("tp_%d" % cd, ["# generated: the transfer %d arrives: %s %.1f %d %.1f facing %d" % (cd, dm, px, py, pz, pyaw), "function last_ember:gate/sc_pre",
                                 "execute in minecraft:%s run tp @s %.1f %d %.1f %d 0" % (dm, px, py, pz, pyaw), "function last_ember:gate/sc_post"])
            # the door: template, interaction, states
            DB, VD = "#scb_%s le.gate" % r, "#scvd_%s le.gate" % r
            keep0(DB); keep0(VD)
            ox, oy, oz = sdoor.origin(d["door"], yaw); rot = sdoor.ROT[yaw]; face = sdoor.FACE[yaw]
            cx, cy, cz = sdoor.world(d["door"], yaw, *sdoor.CLICK)
            door_lower = "minecraft:dark_oak_door[facing=%s,half=lower,hinge=left,open=%%s]" % face
            chains = [sdoor.world(d["door"], yaw, *c) for c in sdoor.CHAINS]
            lants = [sdoor.world(d["door"], yaw, *c) for c in sdoor.LANTERNS]
            ichain = "minecraft:iron_chain[axis=y]"; dl = sdoor.REG[r][4]
            spawn_i = ["kill @e[type=minecraft:interaction,tag=le.scdoor,scores={le.scw=%d}]" % n,
                       "summon minecraft:interaction %.1f %d %.1f {Tags:[\"le.scdoor\",\"le.scclick\",\"le.scnew\"],width:1.2f,height:2.2f,response:1b}" % (cx + 0.5, cy, cz + 0.5),
                       "scoreboard players set @e[type=minecraft:interaction,tag=le.scnew] le.scw %d" % n, "tag @e[type=minecraft:interaction,tag=le.scnew] remove le.scnew"]
            if d["build"]:
                w("door_build_" + r, ["# generated: the shortcut door of %s is placed (template, locked) once its chunk is loaded" % r,
                                      "place template last_ember:shortcut/door_%s %d %d %d %s" % (r, ox, oy, oz, rot)] + spawn_i +
                  ["scoreboard players set %s 1" % DB, "scoreboard players set %s 0" % VD])
                sec.append("execute if score %s matches 0 in minecraft:%s if loaded %d %d %d run function last_ember:gate/gen/door_build_%s" % (DB, dim, dx_, dy_, dz_, r))
            else:
                init.append("scoreboard players set %s 1" % DB)
            w("door_open_" + r, ["# generated: the shortcut door of %s: open (chains off, lanterns, the door open)" % r] +
              ["setblock %d %d %d minecraft:air" % c for c in chains] + ["setblock %d %d %d minecraft:%s[hanging=true]" % (c + (dl,)) for c in lants] +
              ["setblock %d %d %d %s" % (dx_, dy_, dz_, door_lower % "true"), "kill @e[type=minecraft:interaction,tag=le.scdoor,scores={le.scw=%d}]" % n,
               "scoreboard players set %s 1" % VD])
            w("door_close_" + r, ["# generated: the shortcut door of %s: locked (TEST)" % r] +
              ["setblock %d %d %d %s" % (c + (ichain,)) for c in chains] + ["setblock %d %d %d minecraft:air" % c for c in lants] +
              ["setblock %d %d %d %s" % (dx_, dy_, dz_, door_lower % "false")] + spawn_i + ["scoreboard players set %s 0" % VD])
            sec.append("execute if score %s matches 1 if score %s matches 1 unless score %s matches 1 in minecraft:%s if loaded %d %d %d run function last_ember:gate/gen/door_open_%s" % (S, DB, VD, dim, dx_, dy_, dz_, r))
            sec.append("execute if score %s matches 0 if score %s matches 1 unless score %s matches 0 in minecraft:%s if loaded %d %d %d run function last_ember:gate/gen/door_close_%s" % (S, DB, VD, dim, dx_, dy_, dz_, r))
            if d["open"].startswith("near:"):
                rr = int(d["open"].split(":")[1])
                sec.append("execute if score %s matches 0 if score %s matches 1 in minecraft:%s positioned %d %d %d if entity @a[distance=..%d,gamemode=!spectator] run function last_ember:gate/gen/sc_open_%s" % (S, DB, dim, dx_, dy_, dz_, rr, r))
            codes[r] = d
        else:
            init.append("scoreboard players set #scb_%s le.gate 0" % r)
        w("sc_open_" + r, ["# generated: the shortcut %s is open from inside the region: both sides, forever" % r, "execute if score %s matches 1 run return 0" % S,
                           "scoreboard players set %s 1" % S, "data modify storage last_ember:gates s.%s set value {open:1b}" % r] +
          (["execute in minecraft:%s positioned %d %d %d as @a[distance=..32] at @s run playsound minecraft:block.chain.break block @s %d %d %d 1.5 0.7" % (d["dim"], d["door"][0], d["door"][1], d["door"][2], d["door"][0], d["door"][1], d["door"][2]),
            "execute in minecraft:%s positioned %d %d %d run title @a[distance=..32] actionbar %s" % (d["dim"], d["door"][0], d["door"][1], d["door"][2], J(tx("Путь в Приют открыт.", "gold")))] if d else []))
        w("sc_close_" + r, ["# generated: TEST ONLY: the shortcut %s is locked again" % r, "scoreboard players set %s 0" % S, "data modify storage last_ember:gates s.%s set value {open:0b}" % r])
        status.append("execute if score %s matches 1 run tellraw @s %s" % (S, J([tx(" шорткат %s: " % r, "gray"), tx("открыт", "green")])))
        status.append("execute if score %s matches 0 run tellraw @s %s" % (S, J([tx(" шорткат %s: " % r, "gray"), tx("заперт" + ("" if d else " (двери в регионе нет)"), "red")])))
    w("click", ["# generated: as the interaction of a shortcut that was clicked (le.scw = region number), @a[tag=le.scclicker] = the player"] +
      ["execute if entity @s[tag=le.schub] run return run title @a[tag=le.scclicker] actionbar %s" % J(tx("Заперто с той стороны.", "gray"))] +
      ["execute if entity @s[tag=le.scdoor,scores={le.scw=%d}] run return run function last_ember:gate/gen/sc_open_r%d" % (int(r[1:]), int(r[1:])) for r, d in codes.items() if d["open"] == "click"] +
      ["title @a[tag=le.scclicker] actionbar %s" % J(tx("Заперто.", "gray"))])
    w("sc_open_dispatch", ["# generated: macro gate/sc_open {r}", "$function last_ember:gate/gen/sc_open_$(r)"])
    w("sc_close_dispatch", ["# generated: macro gate/sc_close {r}", "$function last_ember:gate/gen/sc_close_$(r)"])
    # ---- borders: the sky guard (above y 316 the barrier ends with the world: elytra, pearls), zones, json for the offline tool
    sky = ["# generated: as/at a player in a border strip (tag le.zf.border), every 5 ticks: the side of each border axis is remembered",
           "# (le.bside = 2*border+side); crossing an axis outside a gap high above the world is undone"]
    pearl = ["# generated: as an ender pearl above y 316: killed inside a border strip (it would fly over the barrier)"]
    zl = ["# generated by tools/gen_gates.py: adventure strips round the border axes, cylinders r8 round the region shortcut doors"]
    bj = []
    for k, b in enumerate(borders, 1):
        a, lo, hi, s = b["a"], b["lo"], b["hi"], b["strip"]
        if b["axis"] == "x":
            box = "x=%d,y=-64,z=%d,dx=%d,dy=400,dz=%d" % (a - s, lo, 2 * s, hi - lo)
            west, east = "x=%d,y=-64,z=%d,dx=%d,dy=400,dz=%d" % (a - s - 1, lo, s, hi - lo), "x=%d,y=-64,z=%d,dx=%d,dy=400,dz=%d" % (a + 1, lo, s, hi - lo)
            gapsel = ["z=%d,dz=%d" % (g0, g1 - g0) for g0, g1 in b["gaps"]]; back = ("%.1f ~ ~" % (a - 1.5), "%.1f ~ ~" % (a + 2.5))
            zl.append("border_%s overworld box %d -64 %d %d 320 %d border" % (b["id"], a - s, lo, a + s, hi))
        else:
            box = "x=%d,y=-64,z=%d,dx=%d,dy=400,dz=%d" % (lo, a - s, hi - lo, 2 * s)
            west, east = "x=%d,y=-64,z=%d,dx=%d,dy=400,dz=%d" % (lo, a - s - 1, hi - lo, s), "x=%d,y=-64,z=%d,dx=%d,dy=400,dz=%d" % (lo, a + 1, hi - lo, s)
            gapsel = ["x=%d,dx=%d" % (g0, g1 - g0) for g0, g1 in b["gaps"]]; back = ("~ ~ %.1f" % (a - 1.5), "~ ~ %.1f" % (a + 2.5))
            zl.append("border_%s overworld box %d -64 %d %d 320 %d border" % (b["id"], lo, a - s, hi, a + s))
        A, B = 2 * k, 2 * k + 1
        ingap = "".join("unless entity @s[%s,y=-64,dy=400] " % g for g in gapsel)
        w("sky_%s" % b["id"], ["# generated: the sky guard of the border %s (%s=%d): side %d (low) / %d (high)" % (b["id"], b["axis"], a, A, B),
                               "scoreboard players set #side le.gate 0",
                               "execute if entity @s[%s] unless entity @s[%s] run scoreboard players set #side le.gate %d" % (west, east, A),
                               "execute if entity @s[%s] unless entity @s[%s] run scoreboard players set #side le.gate %d" % (east, west, B),
                               "execute if score #side le.gate matches 0 run return 0",
                               "execute if score @s le.bside matches %d if score #side le.gate matches %d if entity @s[y=300,dy=1000] %srun return run tp @s %s" % (A, B, ingap, back[0]),
                               "execute if score @s le.bside matches %d if score #side le.gate matches %d if entity @s[y=300,dy=1000] %srun return run tp @s %s" % (B, A, ingap, back[1]),
                               "scoreboard players operation @s le.bside = #side le.gate"])
        sky.append("execute if entity @s[%s] run function last_ember:gate/gen/sky_%s" % (box, b["id"]))
        pearl.append("execute if entity @s[%s] run return run kill @s" % box)
        bj.append({"id": b["id"], "axis": b["axis"], "a": a, "lo": lo, "hi": hi, "gaps": b["gaps"], "test": b["test"]})
    for r, d in codes.items():
        zl.append("scdoor_%s %s cyl %d %d 8 %d %d" % (r, d["dim"], d["door"][0], d["door"][2], d["door"][1] - 4, d["door"][1] + 10))
    init.append("data modify storage last_ember:gates n set value %d" % len(gates_))
    # ---- write
    import shutil
    if os.path.isdir(GEN): shutil.rmtree(GEN)
    os.makedirs(GEN)
    for p in os.listdir(HOOK) if os.path.isdir(HOOK) else []:          # stub hooks of test gates go away with the test file
        if open(os.path.join(HOOK, p), encoding="utf-8").readline().startswith("# TEST gate hook"): os.remove(os.path.join(HOOK, p))
    w("init", init); w("sec", sec); w("fast", fast); w("still", still + ["return 1"]); w("arrive", arrive + ["function last_ember:gate/sc_cancel"]); w("status", status)
    w("sky", sky); w("pearl", pearl)
    for name, lines in FILES.items():
        p = os.path.normpath(os.path.join(GEN, name + ".mcfunction")); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    open(os.path.join(ROOT, "zones/gates.gen.txt"), "w").write("\n".join(zl) + "\n")
    json.dump({"borders": bj}, open(os.path.join(ROOT, "gates/borders.gen.json"), "w"), indent=1)
    # test templates of the test gates (only with a test file)
    os.makedirs(STRUCT, exist_ok=True)
    for p in os.listdir(STRUCT):
        if p.startswith("test_"): os.remove(os.path.join(STRUCT, p))
    if test: test_templates()
    print("%d borders, %d gates, %d region doors, %d functions" % (len(borders), len(gates_), len(codes), len(FILES)))

def test_templates():
    """the test gate: closed = a cobblestone wall 5x5 with a portcullis look, open = an arch of air (5 wide, 1 deep)"""
    tmp = os.path.join(ROOT, "server/build/gate"); os.makedirs(tmp, exist_ok=True)
    for name, fn in (("test_closed", lambda x, y: "minecraft:cobblestone" if (x in (0, 4) or y == 4) else "minecraft:iron_bars[east=true,west=true]"),
                     ("test_open", lambda x, y: "minecraft:cobblestone" if (x in (0, 4) or y == 4) else "minecraft:air")):
        p = os.path.join(tmp, name + ".txt")
        open(p, "w").write("".join("%d %d 0 %s\n" % (x, y, fn(x, y)) for x in range(5) for y in range(5)))
        r = subprocess.run([os.path.join(ROOT, "tools/blockwriter.sh"), "nbt", p, "0", "0", "0", os.path.join(STRUCT, name + ".nbt")], capture_output=True, text=True)
        if r.returncode: raise SystemExit(r.stdout + r.stderr)

def check_bonfires(borders):
    """no bonfire (zone r6) touches a border axis outside its gaps"""
    for path in [os.path.join(ROOT, "bonfires/bonfires.txt")]:
        for raw in open(path, encoding="utf-8"):
            f = raw.split("#", 1)[0].split()
            if len(f) < 6 or f[2] != "overworld": continue
            x, z = int(f[3]), int(f[5])
            for b in borders:
                along, across = (z, x) if b["axis"] == "x" else (x, z)
                if b["lo"] - 7 <= along <= b["hi"] + 7 and abs(across - b["a"]) <= 7 and not any(g0 - 7 <= along <= g1 + 7 for g0, g1 in b["gaps"]):
                    raise SystemExit("bonfire %s at %d,%d is within 7 blocks of the border %s" % (f[1], x, z, b["id"]))

if __name__ == "__main__":
    main()
