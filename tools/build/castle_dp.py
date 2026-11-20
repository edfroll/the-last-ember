"""T-028: the generated part of the datapack of the castle approaches (function/castle/gen/*), the zones `castle` and `castle_rock`,
the points in storage for the next task. Called by tools/build/r1_castle.py with the plan and the build metadata.

Scores (le.cas, globals): #gt gametime, #t tick counter of the loop, #eyes desired eye state (0 asleep, 1 lit, 2 dim, 3 empty), #eyesv
what the eyes show now (-1 unknown: set when the chunks are loaded), #eyet gametime when the eyes go back to sleep, #recog gametime
until which «the colossi know the seal» is not shown again, #faded 0/1 (the faded lake, set by the region hook), #lt<k> the state of lake
tile k in the world (0 alive, 1 faded, -1 unknown), #arm the south colossus's raised arm in the world (0 up, 1 broken, -1 unknown),
#amb 0 ambush ready / 1 fired, #ambt seconds without players within 32 of the rest platform, #kn knock point counter.
Players: tags le.sealh (carries the seal), le.cpass (let through: the colossi do not wake for him), le.cwake (awakening: le.cw ticks
left), le.cfly (thrown: le.cf ticks flown, start le.csx/csy/csz and end le.cex/cey/cez x100), le.cg gametime of the end of the grace,
le.co loop passes (5 ticks) outside the rock and the trigger (20 -> le.cpass goes), le.ck the knock point index."""
import os
import numpy as np
import castle_plan as P

ROOT = P.ROOT; DP = os.path.join(ROOT, "datapack/data/last_ember")
FLY_TICKS = 24                  # 1.2 s of flight
ARC = 1000                      # the arc over the straight line, x100 (10 blocks)

def w(rel, lines):
    p = os.path.join(DP, "function/castle/gen", rel + ".mcfunction"); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write("\n".join(lines) + "\n")

def boxsel(b):
    x1, y1, z1, x2, y2, z2 = b
    return "x=%d,y=%d,z=%d,dx=%d,dy=%d,dz=%d" % (x1, y1, z1, x2 - x1, y2 - y1, z2 - z1)

def rock_boxes(rl, gr):
    """the zones castle_rock_* (indestructible like `castle`, no_blink, no_chorus): the bounding boxes of the bridgehead, the peak, the stair,
    the rest platform, the rift, the table. The colossi test players against exact_boxes (the shape of the rock)."""
    X, Z = gr["X"], gr["Z"]
    def bbox(m):
        xs, zs = X[m], Z[m]; return int(xs.min()), int(zs.min()), int(xs.max()), int(zs.max())
    hd = bbox(rl["pred"]); pk = bbox(rl["peak"]); tb = bbox(rl["table"]); rf = bbox(rl["rift"])
    ry = [c for c in P.stair()[0] if c[4] == "L" and c[0] == P.REST[0]][0][3]
    out = [("castle_rock_head", (hd[0], P.W - 12, hd[1], hd[2], 260, hd[3])),
           ("castle_rock_peak", (pk[0], P.W - 12, pk[1], pk[2], 260, pk[3])),
           ("castle_rock_stair", (P.FACE_X, P.W + 1, P.LANE_A[0] - 1, P.FACE_X + 15, P.PRED_Y, P.LANE_B[1] + 1)),
           ("castle_rock_rest", (P.REST[0] - 1, ry, P.REST[1] - 1, P.REST[2], ry + 6, P.REST[3] + 1)),
           ("castle_rock_rift", (rf[0], P.W - 12, rf[1], rf[2], 260, rf[3])),
           ("castle_rock_table", (tb[0], P.W - 12, tb[1], tb[2], 260, tb[3]))]
    return out

def exact_boxes(rl, gr):
    """the colossi's test of «on the rock» (castle/gen/in_rock): boxes hugging the shape of the rock (bands of 4 rows, split to rows and
    runs where a box would reach ground outside the rock), each from 3 under the lowest rock top in it; the stair, the rest platform and
    the rift as in rock_boxes"""
    X, Z = gr["X"], gr["Z"]; T = rl["T"]; rock = rl["rock"]; out = []
    def ok(x1, z1, x2, z2, y1):
        m = (X >= x1) & (X <= x2) & (Z >= z1) & (Z <= z2) & ~rock
        top = np.maximum(T, np.where(rl["Wt"] != P.NONE, rl["Wt"], -999))
        return not (m & (top + 2.3 >= y1)).any()
    def add(rows):
        sub = rock[rows[0] - gr["z1"]:rows[-1] - gr["z1"] + 1]
        xs = np.nonzero(sub.any(axis=0))[0]
        if not len(xs): return
        x1, x2 = int(xs.min() + gr["x1"]), int(xs.max() + gr["x1"])
        y1 = int(T[rows[0] - gr["z1"]:rows[-1] - gr["z1"] + 1][sub].min()) - 3
        if ok(x1, rows[0], x2, rows[-1], y1): out.append((x1, y1, rows[0], x2, 260, rows[-1])); return
        if len(rows) > 1:
            for r in rows: add([r])
            return
        row = sub[0]; j = 0                                # one row: contiguous runs of rock
        while j < len(row):
            if not row[j]: j += 1; continue
            k = j
            while k + 1 < len(row) and row[k + 1]: k += 1
            xa, xb = j + gr["x1"], k + gr["x1"]; ya = int(T[rows[0] - gr["z1"], j:k + 1].min()) - 3
            if not ok(xa, rows[0], xb, rows[0], ya): raise SystemExit("castle_rock: no exact box for row %d %d..%d" % (rows[0], xa, xb))
            out.append((xa, ya, rows[0], xb, 260, rows[0])); j = k + 1
    zs = np.nonzero(rock.any(axis=1))[0] + gr["z1"]
    for z0 in range(int(zs.min()), int(zs.max()) + 1, 4): add(list(range(z0, min(z0 + 3, int(zs.max())) + 1)))
    for name, b in rock_boxes(rl, gr):
        if name in ("castle_rock_stair", "castle_rock_rest", "castle_rock_rift"): out.append(b)
    return out

def check_boxes(boxes, rl, gr):
    """no player standing outside the rock can be inside a rock box (the ground there + 2.3 jump < the box bottom), except in the rift box"""
    X, Z = gr["X"], gr["Z"]; T = rl["T"]; bad = []
    for name, (x1, y1, z1, x2, y2, z2) in boxes:
        if name in ("castle_rock_rift", "castle_rock_stair", "castle_rock_rest"): continue
        m = (X >= x1) & (X <= x2) & (Z >= z1) & (Z <= z2) & ~rl["rock"] & gr["place"]
        hi = np.where(m, T + 2.3, -999)
        wt = np.where(m & (rl["Wt"] != P.NONE), rl["Wt"] + 2.3, -999)
        over = (np.maximum(hi, wt) >= y1)
        if over.any():
            zz, xx = np.nonzero(over); bad.append((name, [(int(X[a, b]), int(Z[a, b]), int(T[a, b])) for a, b in list(zip(zz, xx))[:5]]))
    return bad

def run(gr, rl, meta):
    from r1 import replace_lines
    boxes = rock_boxes(rl, gr); meta["rock_boxes"] = boxes
    ex = exact_boxes(rl, gr); meta["rock_test_boxes"] = len(ex)
    zl = ["castle          overworld cyl %d %d %d %d 260   # T-028: the castle and its approaches (indestructible; W-12 .. the keep)" % (P.CX, P.CZ, P.R_PLACE, P.W - 12)]
    for name, (x1, y1, z1, x2, y2, z2) in boxes:
        zl.append("%-15s overworld box  %d %d %d  %d %d %d   no_blink,no_chorus   # T-028: the castle rock" % (name, x1, y1, z1, x2, y2, z2))
    replace_lines(os.path.join(ROOT, "zones/zones.txt"), ["castle "] + ["%s " % n for n, _ in boxes], zl)
    hdr = "# generated by tools/build/castle_dp.py (T-028) - do not edit"
    # ------------------------------------------------------------------ init, points
    co = meta["colossi"]; br = meta["bridge"]; bb = meta["barbican"]; st = meta["stair"]
    kp = ",".join("[%.1fd,%.1fd,%.1fd]" % (x, P.W - 0.4, z) for (x, z) in P.KNOCK_PTS)
    pts = ('{palm_n:[%.1fd,%.1fd,%.1fd],palm_s:[%.1fd,%.1fd,%.1fd],knock:[%s],rest:[%.1fd,%dd,%.1fd],gate:[%.1fd,%dd,%.1fd]}'
           % tuple(co["n"]["strike"] + co["s"]["strike"] + [kp, (P.REST[0] + P.REST[2]) / 2 + 0.5, st["rest_y"] + 1, (P.REST[1] + P.REST[3]) / 2 + 0.5] + bb["gate"]))
    w("init", [hdr + ": the scores restored from storage after a reset of the scoreboard, the points",
               "data modify storage last_ember:castle pts set value " + pts,
               "data modify storage last_ember:r1 m.castle_bridge_mid set value {pos:[%.1fd,%dd,%.1fd]}" % tuple(br["mid"]),
               "data modify storage last_ember:r1 m.castle_gate set value {pos:[%.1fd,%dd,%.1fd]}" % tuple(bb["gate"]),
               "execute unless data storage last_ember:castle st run data modify storage last_ember:castle st set value {faded:0,amb:0,ambt:0}",
               "execute unless score #eyesv le.cas matches -1.. run scoreboard players set #eyesv le.cas -1",
               "execute unless score #arm le.cas matches -1.. run scoreboard players set #arm le.cas -1",
               "execute unless score #faded le.cas matches 0.. store result score #faded le.cas run data get storage last_ember:castle st.faded",
               "execute unless score #amb le.cas matches 0.. store result score #amb le.cas run data get storage last_ember:castle st.amb",
               "execute unless score #ambt le.cas matches 0.. store result score #ambt le.cas run data get storage last_ember:castle st.ambt"]
      + ["execute unless score #lt%d le.cas matches -1.. run scoreboard players set #lt%d le.cas -1" % (k, k) for k in range(len(meta["templates"]["lake_tiles"]))])
    # ------------------------------------------------------------------ the zones of the mechanics
    tr = " ".join("unless entity @s[%s]" % boxsel((t[0], t[1], t[2], t[3], t[4], t[5])) for t in P.TRIGGER)
    w("in_trigger", [hdr + ": 1 when @s is in the trigger of the colossi (the channel and the pier; the first flight up to its turn)",
                     "execute %s run return 0" % tr, "return 1"])
    w("in_rock", [hdr + ": 1 when @s is on the castle rock (the bridgehead and the peak, the stair, the rift, the table): boxes hugging the rock,",
                  "# from 3 under its top (no ground outside the rock reaches into them)"]
      + ["execute if entity @s[%s] run return 1" % boxsel(b) for b in ex] + ["return 0"])
    w("near_hearth8", [hdr + ": 1 when @s is at bonfire 8 (its pad)",
                       "execute unless entity @s[%s] run return 0" % boxsel((P.PAD8[0] - 1, P.PAD8_Y - 1, P.PAD8[1] - 1, P.PAD8[2] + 1, P.PAD8_Y + 6, P.PAD8[3] + 1)), "return 1"])
    # ------------------------------------------------------------------ the eyes (4 sockets x 2 colossi, the eye block one deep)
    eyes = co["n"]["eyes"] + co["s"]["eyes"]
    ex = eyes[0]
    for nm, blk in (("asleep", "minecraft:polished_blackstone"), ("lit", "minecraft:pearlescent_froglight[axis=y]"), ("dim", "minecraft:crying_obsidian"), ("empty", "minecraft:air")):
        w("eyes_" + nm, [hdr + ": the eyes of both colossi: " + nm] + ["setblock %d %d %d %s" % (x, y, z, blk) for (x, y, z) in eyes])
    w("eyes_sync", [hdr + ": the eyes show #eyes (only when both colossi's chunks are loaded)",
                    "execute unless loaded %d %d %d run return 0" % (ex[0], ex[1], co["n"]["eyes"][0][2]),
                    "execute unless loaded %d %d %d run return 0" % (ex[0], ex[1], co["s"]["eyes"][0][2]),
                    "execute if score #eyes le.cas matches 0 run function last_ember:castle/gen/eyes_asleep",
                    "execute if score #eyes le.cas matches 1 run function last_ember:castle/gen/eyes_lit",
                    "execute if score #eyes le.cas matches 2 run function last_ember:castle/gen/eyes_dim",
                    "execute if score #eyes le.cas matches 3 run function last_ember:castle/gen/eyes_empty",
                    "scoreboard players operation #eyesv le.cas = #eyes le.cas"])
    # the palms: particles of the waking (charging) and of the strike
    for k in ("n", "s"):
        sx, sy, sz = co[k]["strike"]
        w("palm_" + k, [hdr + ": the palm of the %s colossus charges (particles)" % k,
                        "particle minecraft:gust %.1f %.1f %.1f 0.6 1.2 0.6 0 2 force @a[distance=..96]" % (sx, sy, sz),
                        "particle minecraft:small_gust %.1f %.1f %.1f 0.6 1.4 0.6 0.02 8 force @a[distance=..96]" % (sx, sy, sz),
                        "particle minecraft:dust_plume %.1f %.1f %.1f 0.5 1.2 0.5 0.02 6 force @a[distance=..96]" % (sx, sy, sz)])
        w("strike_" + k, [hdr + ": the strike from the palm of the %s colossus (the wind burst; the line of gusts to @s is drawn by castle/beam)" % k,
                          "particle minecraft:gust_emitter_large %.1f %.1f %.1f 0 0 0 0 1 force @a[distance=..128]" % (sx, sy, sz),
                          "playsound minecraft:entity.wind_charge.wind_burst hostile @a[distance=..96] %.1f %.1f %.1f 3 0.5" % (sx, sy, sz),
                          "playsound minecraft:entity.breeze.wind_burst hostile @a[distance=..96] %.1f %.1f %.1f 2 0.4" % (sx, sy, sz),
                          "execute positioned %.1f %.1f %.1f facing entity @s eyes run function last_ember:castle/beam" % (sx, sy, sz)])
        w("charge_" + k, [hdr + ": the colossus raises its palm: stone grinding at the %s colossus" % k,
                          "playsound minecraft:block.grindstone.use hostile @a[distance=..96] %.1f %.1f %.1f 3 0.3" % (sx, sy - 10, sz),
                          "playsound minecraft:entity.iron_golem.repair hostile @a[distance=..96] %.1f %.1f %.1f 3 0.4" % (sx, sy - 10, sz),
                          "particle minecraft:dust_plume %.1f %.1f %.1f 2 6 2 0.02 30 force @a[distance=..96]" % (sx + 4, sy - 12, sz)])
    # the knock points: one per index, the flight's end (x100)
    for k, (x, z) in enumerate(P.KNOCK_PTS):
        w("knock_%d" % k, [hdr + ": the end of the flight for knock point %d" % k,
                           "scoreboard players set @s le.cex %d" % round(x * 100), "scoreboard players set @s le.cey %d" % round((P.W - 0.4) * 100),
                           "scoreboard players set @s le.cez %d" % round(z * 100)])
    # ------------------------------------------------------------------ the ambush
    nis = [((a + c) / 2 + 0.5, P.NICHE_Y + 1, (b + d) / 2 + 0.5) for (a, b, c, d) in P.NICHES]
    rc = ((P.REST[0] + P.REST[2]) / 2 + 0.5, st["rest_y"] + 1, (P.REST[1] + P.REST[3]) / 2 + 0.5)
    w("on_rest", [hdr + ": 1 when @s stands on the rest platform", "execute unless entity @s[%s] run return 0" % boxsel((P.REST[0] - 1, st["rest_y"], P.REST[1] - 1, P.REST[2] + 1, st["rest_y"] + 3, P.REST[3] + 1)), "return 1"])
    w("ambush_near", [hdr + ": the number of players within 16 / 32 of the rest platform -> #n16 / #n32",
                      "execute positioned %.1f %d %.1f store result score #n16 le.cas if entity @a[distance=..16,gamemode=!spectator,gamemode=!creative]" % rc,
                      "execute positioned %.1f %d %.1f store result score #n32 le.cas if entity @a[distance=..32,gamemode=!spectator]" % rc])
    w("ambush_one", [hdr + ": one skeleton out of each niche (dust, the knock of stone), jumping down onto the platform"]
      + ["summon minecraft:skeleton %.1f %d %.1f {Tags:[\"le.noelite\",\"le.camb\"],Motion:[-0.42d,0.36d,0.0d],PersistenceRequired:1b}" % (x, y, z) for (x, y, z) in nis]
      + ["particle minecraft:block{block_state:\"minecraft:cobbled_deepslate\"} %.1f %d %.1f 0.8 1 0.8 0 24 force @a[distance=..48]" % (x, y + 1, z) for (x, y, z) in nis]
      + ["playsound minecraft:block.stone.break hostile @a[distance=..48] %.1f %d %.1f 1.5 0.5" % (x, y, z) for (x, y, z) in nis]
      + ["playsound minecraft:entity.zombie.attack_wooden_door hostile @a[distance=..48] %.1f %d %.1f 0.8 0.5" % nis[0]])
    # ------------------------------------------------------------------ the gate of the barbican (a click box in the gateway)
    g = bb["gate"]
    w("gate_box", [hdr + ": the click box over the locked gate (once; again when it is missing and the chunk is loaded)",
                   "execute unless loaded %d %d %d run return 0" % (int(g[0]), int(g[1]), int(g[2])),
                   "execute positioned %.1f %d %.1f if entity @e[type=minecraft:interaction,tag=le.cgate,distance=..3] run return 0" % (g[0], g[1], g[2] + 0.6),
                   "summon minecraft:interaction %.1f %d %.1f {Tags:[\"le.cgate\"],width:3.2f,height:4.0f,response:1b}" % (g[0], g[1], g[2] + 0.6)])
    # ------------------------------------------------------------------ the fade: the lake tiles, the south colossus's arm
    tiles = meta["templates"]["lake_tiles"]; ts = []
    for k, (name, o) in enumerate(tiles):
        w("lt_%d" % k, [hdr + ": lake tile %d (%s) shows #faded" % (k, name),
                        "execute if score #faded le.cas matches 1 run place template last_ember:castle/%s_faded %d %d %d" % (name, o[0], o[1], o[2]),
                        "execute if score #faded le.cas matches 0 run place template last_ember:castle/%s_alive %d %d %d" % (name, o[0], o[1], o[2]),
                        "scoreboard players operation #lt%d le.cas = #faded le.cas" % k])
        ts.append("execute unless score #lt%d le.cas = #faded le.cas if loaded %d %d %d if loaded %d %d %d run function last_ember:castle/gen/lt_%d" % (k, o[0], o[1], o[2], o[0] + 31, o[1], o[2] + 31, k))
    cs = co["s"]; hb = meta["templates"]["colossus_s_hi"]
    w("arm_sync", [hdr + ": the raised arm of the south colossus: broken off in the faded lake (the hi piece without it), whole again after"]
      + ["execute unless loaded %d %d %d run return 0" % (hb[0], hb[1], hb[2]), "execute unless loaded %d %d %d run return 0" % (hb[0] + 11, hb[1], hb[2] + 10),
         "execute if score #faded le.cas matches 1 run place template last_ember:castle/colossus_s_hi_broken %d %d %d" % tuple(meta["templates"]["colossus_s_hi_broken"]),
         "execute if score #faded le.cas matches 0 run place template last_ember:castle/colossus_s_hi %d %d %d" % tuple(hb),
         "scoreboard players operation #arm le.cas = #faded le.cas", "scoreboard players set #eyesv le.cas -1"])
    w("fade_sync", [hdr + ": every second: the world shows the faded / living lake where its chunks are loaded"] + ts
      + ["execute unless score #arm le.cas = #faded le.cas run function last_ember:castle/gen/arm_sync"])
    meta["dp"] = dict(eyes=eyes, niches=nis, rest=rc, fly_ticks=FLY_TICKS)
    # the flight arc (x100): 4 * ARC * t * (N - t) / N^2 for every tick t
    w("arc", [hdr + ": #arc = the height of the arc over the straight line at flight tick @s le.cf (x100)"]
      + ["execute if score @s le.cf matches %d run scoreboard players set #arc le.cas %d" % (t, round(4 * ARC * t * (FLY_TICKS - t) / FLY_TICKS ** 2)) for t in range(0, FLY_TICKS + 1)])
