#!/usr/bin/env python3
"""T-034 checks on the R1 world (world_cache.py redo grotto castle ogre): the treasuries of R1 and their owners. Clients Cam and Cam2 in
the game (real input through the dev agent: a raised shield (!use_on), a click on a chest (!use)). Difficulty easy unless said.
  build   tools/build/treasury_check.py on the saved world (the cave, the stair, the grotto, the channel, the room, the ledges, the three
          chests with their locks, the cover 8 / 6, the walks, the boat, the death trace in the rift)
  ogre    Cam comes into the den -> he wakes (140 + 40 x the players in the den); the blow over his head: Cam with a raised shield takes
          nothing, Cam2 without one <= 7 hearts on normal (14) and is thrown back; a bone at the far player (4, slowness); his death:
          the kneeling, the fall, the XP 15 at the spot, the lock off, a trophy to both of them, the chest opens (a real click)
  grotto  the Jelly wakes (80 + 25 x n), the touch (damage, slowness II), the big one throws back
  split   the big one torn -> 3 medium -> 6 small, never more than 10 bodies, all dead -> the lock off; no vanilla slime ever
  tower   the White Lady wakes (60 + 20 x n), the touch with the Frost, the wail (darkness), out of the wall behind the player, never
          outside the room; an arrow takes half; fire does nothing; her death -> the lock off, the window dark
  lock    while the owner lives the chest does not open (a real click), after his death it does
  leash   everybody out 10 s -> the owner on its point with full health (the Jelly whole again)
  peace   peaceful: no owners, the chests open
  bones   12..20 signs of the chain, the first two seen from the trail (a frame)
  window  at night the soul lantern in the window, by day none, none after the Lady's death
  vaults  10 layouts of T-019: the staff of R1 lies in each of the three at least once
  zones   the den, the grotto and the ledges cannot be broken
  restart a restart in the middle of a fight: the owner asleep, no doubles; a dead one stays dead
  perf    every fight with two players (the profiler), the Jelly at the peak of its splitting
Usage: python3 tools/test_treasury.py [build ogre grotto split tower lock leash peace bones window vaults zones restart perf]"""
import importlib.util, json, math, os, re, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
R = rc.run
ok = bad = 0
OUT = os.path.join(ROOT, "server/build/r1")
O = json.load(open(os.path.join(OUT, "ogre.json"))); G = json.load(open(os.path.join(OUT, "grotto.json"))); TW = json.load(open(os.path.join(OUT, "tower.json")))
F = O["F"]; W = G["W"]
OGRE = "@e[type=minecraft:zombie,tag=le.tr_ogre,limit=1]"; JELLY = "@e[type=minecraft:ghast,tag=le.tr_jelly]"; JELLY1 = "@e[type=minecraft:ghast,tag=le.tr_jelly,limit=1]"
def jel(extra): return "@e[type=minecraft:ghast,tag=le.tr_jelly,%s]" % extra
LADY = "@e[type=minecraft:vex,tag=le.tr_lady,limit=1]"
DEN_IN = (236.5, F + 1, 150.5)            # in the den, 11 east of the bed
DEN_FAR = (245.5, F + 1, 160.5)           # in the den, far side
DEN_OUT = (O["exit"][4][0] + 0.5, O["top"], O["exit"][4][1] + 2.5)    # outside, by the mouth
LEDGE = ((G["ledge"][0] + G["ledge"][2] + 1) / 2, W + 2, (G["ledge"][1] + G["ledge"][3] + 1) / 2)
GOUT = (G["mouth"][0], W + 1, G["mouth"][2] + 6)
ROOM_IN = (477.5, TW["floor"] + 1, 35.5)
TOUT = tuple(TW["start"])

def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n, flush=True)
    else: bad += 1; print("  FAIL", n, e, flush=True)
def passed(cmd): return "passed" in R(cmd)
def pos(sel):
    v = re.findall(r"(-?\d+\.?\d*(?:E-?\d+)?)d", R(f"data get entity {sel} Pos")); return [float(x) for x in v] if len(v) == 3 else None
def wait(cond, t=10.0, step=0.3):
    t0 = time.time()
    while time.time() - t0 < t:
        if cond(): return True
        time.sleep(step)
    return cond()
def count(sel):
    m = re.search(r"Count: (\d+)", R(f"execute if entity {sel}")); return int(m.group(1)) if m else 0
def blk(x, y, z, b): return passed(f"execute if block {x} {y} {z} {b}")
def sc(k): return tc.score(k, "le.tr")
def nbt(sel, path): return R(f"data get entity {sel} {path}")
def hp(sel): return tc.hp(sel)
def tpp(p, x, y, z, yaw=0, pitch=0):
    if 400 <= x <= 500 and -60 <= z <= 100: R(f"tag {p} add le.cpass")       # the castle's rock: the pass of the colossi (from the bridge in the game)
    R(f"tp {p} {x} {y} {z} {yaw} {pitch}")
def look_at(p, x, y, z): R(f"execute as {p} at @s anchored eyes run tp @s ~ ~ ~ facing {x} {y} {z}")
def stor(k): return tc.num(R(f"data get storage last_ember:treasury {k}.state"), r"(-?\d+)$")
def taken(p):
    """the statistic damage_taken (tenths of a point: blocked damage and natural regeneration do not hide it)"""
    R("scoreboard objectives add t.dmg minecraft.custom:minecraft.damage_taken"); return (tc.score(p, "t.dmg") or 0) / 10.0
def trophies(p):
    m = re.search(r"Found (\d+)", R(f'clear {p} minecraft:nautilus_shell[minecraft:custom_data~{{le_trophy:"r1"}}] 0')); return int(m.group(1)) if m else 0

class tm:
    @staticmethod
    def relaunch(name):
        if name == "Cam": subprocess.Popen(f"cd {ROOT} && python3 -I tools/client_launch.py > server/client.out 2>&1", shell=True)
        else: subprocess.Popen(f"cd {ROOT} && python3 -I tools/client_launch.py --name Cam2 --dir server/client2 --mem 1500M --size 640x360 > server/client2.out 2>&1", shell=True)
    @staticmethod
    def join(name):
        for _ in range(60):
            time.sleep(3)
            try:
                l = R("list")
                if (name == "Cam2" and "Cam2" in l) or (name == "Cam" and re.search(r"\bCam(?!2)\b", l)): return True
            except Exception: pass
        return False
    @staticmethod
    def restart():
        subprocess.run([os.path.join(ROOT, "tools/server.sh"), "stop"], capture_output=True); time.sleep(8)
        subprocess.Popen(f"cd {ROOT} && tools/server.sh start > server/console.out 2>&1", shell=True)
        for _ in range(90):
            time.sleep(2)
            try:
                if "players online" in R("list"): break
            except Exception: pass
        subprocess.run("pkill -f net.minecraft.client.main.Main", shell=True); time.sleep(3)
        for name in ("Cam", "Cam2"): tm.relaunch(name); tm.join(name); time.sleep(6)
        time.sleep(20)
    @staticmethod
    def fresh():
        """the clients relaunched (Cam, then Cam2: the focus with Cam2); the clicks of a fresh client settle ~25 s (T-033)"""
        subprocess.run("pkill -f net.minecraft.client.main.Main", shell=True); time.sleep(4)
        for name in ("Cam", "Cam2"): tm.relaunch(name); tm.join(name); time.sleep(6)
        time.sleep(25)
        for name in ("Cam", "Cam2"): tc.act(name, "!sneak_off"); tc.act(name, "!use"); time.sleep(1)
    @staticmethod
    def prof(sec=10):
        import glob, zipfile
        before = set(glob.glob(os.path.join(ROOT, "server/debug/profiling/*.zip"))); R("perf start")
        time.sleep(sec + 1); R("perf stop"); new = []
        for _ in range(40):
            new = sorted(set(glob.glob(os.path.join(ROOT, "server/debug/profiling/*.zip"))) - before)
            if new: break
            time.sleep(0.5)
        if not new: return {}
        time.sleep(1.0); t = zipfile.ZipFile(new[-1]).read("server/profiling.txt").decode()
        span = float(re.search(r"Time span: (\d+) ms", t).group(1)); ticks = float(re.search(r"Tick span: (\d+) ticks", t).group(1))
        out = {"tick": span / ticks}
        for m in re.finditer(r"\[05\][ |]*function (last_ember:[a-z_/0-9]+)\(\d+/\d+\) - [0-9.]+%/([0-9.]+)%", t): out[m.group(1)] = span * float(m.group(2)) / 100 / ticks
        return out

def stage(diff="easy", prot=True, mode="survival"):
    for p in ("Cam", "Cam2"):
        if not passed(f"execute if entity @a[name={p},tag=le.cinit]"): tc.setc(1, 1, 0, p)
        R(f"gamemode {mode} {p}"); R(f"effect clear {p}"); R(f"clear {p}")
        if prot: R(f"effect give {p} minecraft:resistance infinite 4 true"); R(f"effect give {p} minecraft:regeneration infinite 4 true")
        R(f"effect give {p} minecraft:saturation infinite 1 true"); R(f"effect give {p} minecraft:night_vision infinite 0 true")
        R(f"execute as {p} run function last_ember:sleep/set_awake {{ticks:0}}")
        R(f'execute as {p} run function last_ember:cemetery/give {{key:"seal"}}'); R(f"tag {p} add le.cpass")      # the colossi let them by
        tc.act(p, "!sneak_off"); tc.act(p, "!fwd_off"); tc.act(p, "!attack_off"); tc.act(p, "!use_off")
    R("weather clear 100000"); R("gamerule advance_time false"); R(f"difficulty {diff}"); R("time set 6000")
    R("kill @e[type=minecraft:experience_orb]"); R("kill @e[type=minecraft:item]")
LOCKS = {"ogre": O["lock"], "grotto": G["lock"], "tower": TW["lock"]}
def reset_all():
    """every owner alive and asleep, the locks back (their chunks forceloaded for the setblock; the owners are summoned by the second
    of a loaded lair)"""
    for k, (x, y, z) in LOCKS.items():
        R(f"forceload add {x} {z}"); time.sleep(0.3); R(f"function last_ember:treasury/gen/{k}/reset"); R(f"forceload remove {x} {z}")
def away(p="Cam2"): tpp(p, *TOUT)
def into_den(p, at=DEN_IN):
    tpp(p, *at); wait(lambda: passed("execute if loaded %d %d %d" % (O["cave"][0] + 2, F + 1, O["cave"][1] + 2)), 15)

# ---------------------------------------------------------------- the chest: a real click
def try_open(p, front, chest):
    R("scoreboard objectives add t.open minecraft.custom:minecraft.open_chest"); n0 = tc.score(p, "t.open") or 0    # a statistic: read, not reset
    tpp(p, front[0] + 0.5, front[1], front[2] + 0.5); time.sleep(1.0)
    look_at(p, chest[0] + 0.5, chest[1] + 0.5, chest[2] + 0.5); time.sleep(0.5)
    tc.act(p, "!use"); time.sleep(1.2)
    n = tc.score(p, "t.open") or 0
    tpp(p, *TOUT); time.sleep(0.8)          # far away: the server closes the screen
    return n > n0
def front_of(chest, facing):
    d = {"east": (1, 0), "west": (-1, 0), "south": (0, 1), "north": (0, -1)}[facing]
    return (chest[0] + d[0], chest[1], chest[2] + d[1])

# ---------------------------------------------------------------- groups
def t_build():
    print("[build]"); away("Cam"); away("Cam2"); reset_all(); R("save-all flush"); time.sleep(3)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools/build/treasury_check.py")], capture_output=True, text=True)
    print("\n".join("     " + l for l in r.stdout.strip().splitlines()))
    chk("treasury_check (the cover 8/6, no light, the chests and locks, the walks, the boat, the ledges, the rift)", r.returncode == 0, r.stdout[-400:] + r.stderr[-300:])
    c = O["chest"]; g = G["chest"]; t = TW["chest"]
    def vault(ch, v):      # the loot table of T-019 until the first opening (then the loot is in the chest: opened in the tests)
        return "vault/" + v in R("data get block %d %d %d LootTable" % tuple(ch)) or "Items" in R("data get block %d %d %d" % tuple(ch))
    for k, (x, y, z) in LOCKS.items(): R(f"forceload add {x} {z}")
    time.sleep(1)
    chk("three chests, the vaults of T-019 (r1_ogre, r1_grotto, r1_tower)", blk(*c, "minecraft:chest") and blk(*g, "minecraft:chest") and blk(*t, "minecraft:chest")
        and vault(c, "r1_ogre") and vault(g, "r1_grotto") and vault(t, "r1_tower"))
    for k, (x, y, z) in LOCKS.items(): R(f"forceload remove {x} {z}")

def t_ogre():
    print("[ogre]"); stage(diff="normal", prot=False); away("Cam"); away("Cam2"); reset_all(); into_den("Cam", DEN_OUT); time.sleep(3)
    chk("asleep on his bed: a zombie of scale 2 riding the seat, NoAI, his name hidden, the skin and the club", count(OGRE) == 1 and "1b" in nbt(OGRE, "NoAI")
        and "1b" not in nbt(OGRE, "CustomNameVisible") and "2.0" in R(f"attribute {OGRE} minecraft:scale get") and "ogre_club" in nbt(OGRE, "equipment.mainhand")
        and passed(f"execute as {OGRE} on vehicle if entity @s[tag=le.tr_oseat]"))
    c0 = sc("#o.chews") or 0; time.sleep(10)
    chk("asleep he chews every 4..8 s (heard from the mouth of the stair): %d in 10 s" % ((sc("#o.chews") or 0) - c0), (sc("#o.chews") or 0) - c0 >= 1)
    R("item replace entity Cam weapon.offhand with minecraft:shield"); R("effect give Cam minecraft:regeneration infinite 2 true"); R("effect give Cam2 minecraft:regeneration infinite 2 true")
    into_den("Cam", DEN_IN); tpp("Cam2", *DEN_IN); time.sleep(1.5)
    chk("Cam and Cam2 in the den: he wakes, 140 + 40 x 2 = 220 true (+500), his name shown", sc("#o.st") == 1 and abs((hp(OGRE) or 0) - 720) < 1 and "1b" in nbt(OGRE, "CustomNameVisible"))
    # the blow: Cam raises the shield toward him, Cam2 beside without one
    R(f"data merge entity {OGRE} {{NoAI:1b}}"); R("scoreboard players set #o.cd le.tr 100000"); R("scoreboard players set #o.bt le.tr 100000")
    ox, oy, oz = 232.5, F + 1, 150.5
    R(f"tp {OGRE} {ox} {oy} {oz} -90 0"); tpp("Cam", ox + 2.6, oy, oz - 0.8, 90, 0); tpp("Cam2", ox + 2.6, oy, oz + 1.0, 90, 0); time.sleep(0.8)
    tc.act("Cam", "!use_on"); time.sleep(0.8)
    h1, h2 = hp("Cam"), hp("Cam2"); p2 = pos("Cam2")
    R(f"execute as {OGRE} at @s run function last_ember:treasury/gen/ogre/swing_try"); time.sleep(1.6)
    d1, d2 = h1 - hp("Cam"), h2 - hp("Cam2"); q2 = pos("Cam2")
    thrown = math.dist(p2[::2], q2[::2]) if p2 and q2 else 0
    tc.act("Cam", "!use_off")
    chk("the blow over his head (normal): Cam behind his raised shield loses %.1f (0), Cam2 without one %.1f (<= 14 = 7 hearts, > 0)" % (d1, d2), d1 <= 0.01 and 0 < d2 <= 14.01)
    chk("Cam2 thrown back %.1f blocks (~6)" % thrown, thrown >= 4.0)
    # the bone at the far player
    away("Cam"); tpp("Cam2", *DEN_FAR); time.sleep(0.5)
    b0 = sc("#o.bonehits") or 0; h2 = taken("Cam2")
    R("scoreboard players set #o.bt le.tr 1"); R(f"data merge entity {OGRE} {{NoAI:0b}}")
    hit = wait(lambda: (sc("#o.bonehits") or 0) > b0, 5)
    slow = passed("execute if entity @a[name=Cam2,nbt={active_effects:[{id:\"minecraft:slowness\"}]}]"); d = taken("Cam2") - h2
    chk("a bone thrown at Cam2 (farther than 7) hits (%d hit): %.1f (4 on normal), slowness %s" % ((sc("#o.bonehits") or 0) - b0, d, slow), hit and slow and 3.5 <= d <= 4.5)
    # the death
    R("tp Cam %s %s %s" % DEN_IN); tpp("Cam2", *DEN_IN)
    R(f"damage {OGRE} 5 minecraft:player_attack by Cam2"); time.sleep(0.7)
    R("kill @e[type=minecraft:experience_orb]")
    t0 = trophies("Cam"), trophies("Cam2")
    R(f"damage {OGRE} 300 minecraft:player_attack by Cam"); time.sleep(0.5)
    chk("true health 0: the dying starts (on his knees, still)", (sc("#o.die") or -1) >= 0 and passed(f"execute as {OGRE} on vehicle if entity @s[tag=le.tr_okneel]"))
    chk("in 3 s: dead, the XP 15 at the spot (no other), the lock off (the hide over the chest gone), «Нора затихла.»", wait(lambda: sc("#o.st") == 2, 5) and count(OGRE) == 0
        and count("@e[type=minecraft:experience_orb]") == 1 and "15s" in nbt("@e[type=minecraft:experience_orb,limit=1]", "Value") and blk(*O["lock"], "minecraft:air"))
    t1 = trophies("Cam"), trophies("Cam2")
    chk("a trophy to each of the fight (Cam %d -> %d, Cam2 %d -> %d)" % (t0[0], t1[0], t0[1], t1[1]), t1[0] == t0[0] + 1 and t1[1] == t0[1] + 1)
    chk("the chest opens now (a real click)", try_open("Cam", front_of(O["chest"], "east"), O["chest"]))
    time.sleep(2); chk("he does not come back", count(OGRE) == 0 and stor("ogre") == 2)

def t_grotto():
    print("[grotto]"); stage(); away("Cam"); away("Cam2"); reset_all(); tpp("Cam", *GOUT); time.sleep(4)
    chk("asleep in the water by the ledge: one big body (an invisible ghast, scale 1, NoAI) with its model, no name", count(JELLY) == 1 and "1b" in nbt(JELLY1, "NoAI")
        and count("@e[type=minecraft:item_display,tag=le.tr_jm]") == 1 and passed("execute if entity @e[type=minecraft:ghast,tag=le.tr_jelly,nbt={active_effects:[{id:\"minecraft:invisibility\"}]}]"))
    tpp("Cam", *LEDGE); tpp("Cam2", LEDGE[0] + 2, LEDGE[1], LEDGE[2]); time.sleep(1.5)
    chk("Cam and Cam2 on the ledge: it wakes, 80 + 25 x 2 = 130 (+500), the name «Студень»", sc("#g.st") == 1 and abs((hp(JELLY1) or 0) - 630) < 1
        and "Студень" in nbt("@e[type=minecraft:text_display,tag=le.tr_jn,limit=1]", "text"))
    R("effect clear Cam minecraft:resistance"); time.sleep(0.3)
    t0 = sc("#g.touches") or 0; h0 = taken("Cam"); p0 = pos("Cam")
    R(f"execute as {JELLY1} run tp @s {LEDGE[0] + 0.5} {LEDGE[1]} {LEDGE[2] + 1.2}"); time.sleep(1.2)
    p1 = pos("Cam")
    chk("the big one touches Cam: hurt (%.1f), slowness II (sticky), thrown %.1f" % (taken("Cam") - h0, math.dist(p0[::2], p1[::2]) if p0 and p1 else 0),
        (sc("#g.touches") or 0) > t0 and taken("Cam") - h0 > 0 and passed('execute if entity @a[name=Cam,nbt={active_effects:[{id:"minecraft:slowness",amplifier:1b}]}]'))
    R("effect give Cam minecraft:resistance infinite 4 true"); R("effect give Cam minecraft:regeneration infinite 4 true")
    d0 = sc("#g.dashes") or 0; time.sleep(4)
    chk("it lunges (dashes counted %d in 4 s), never a vanilla slime" % ((sc("#g.dashes") or 0) - d0), (sc("#g.dashes") or 0) > d0 and count("@e[type=minecraft:slime]") == 0)

def t_split():
    print("[split]"); stage(); away("Cam"); away("Cam2"); reset_all(); time.sleep(3)
    tpp("Cam", *LEDGE); tpp("Cam2", LEDGE[0] + 2, LEDGE[1], LEDGE[2]); time.sleep(1.5)
    t0 = trophies("Cam"), trophies("Cam2")
    R(f"damage {JELLY1} 10 minecraft:player_attack by Cam2"); time.sleep(0.7)
    R(f"execute as {JELLY} run damage @s 300 minecraft:player_attack by Cam"); time.sleep(0.5)
    chk("torn: 1 s of tearing (the model shudders)", (tc.score(JELLY1, "le.trp") or -1) >= 0)
    chk("-> 3 medium bodies thrown out", wait(lambda: count(jel("scores={le.trs=2}")) == 3, 3))
    time.sleep(1.5)
    R(f"execute as {JELLY} run damage @s 300 minecraft:player_attack by Cam"); time.sleep(0.3)
    chk("-> 6 small ones (peak %s, made %s <= 10)" % (sc("#g.peak"), sc("#g.made")), wait(lambda: count(jel("scores={le.trs=1}")) == 6, 3) and (sc("#g.made") or 99) <= 10)
    time.sleep(1.5)
    R("kill @e[type=minecraft:experience_orb]")
    R(f"execute as {JELLY} run damage @s 300 minecraft:player_attack by Cam"); time.sleep(0.3)
    chk("the small ones run out: no body left -> dead (2), the slime lock off, the XP 15, «Грот затих.»", wait(lambda: sc("#g.st") == 2, 4) and count(JELLY) == 0
        and blk(*G["lock"], "minecraft:air") and count("@e[type=minecraft:experience_orb]") == 1)
    t1 = trophies("Cam"), trophies("Cam2")
    chk("a trophy to each of the fight (Cam %d -> %d, Cam2 %d -> %d); no vanilla slime" % (t0[0], t1[0], t0[1], t1[1]), t1 == (t0[0] + 1, t0[1] + 1) and count("@e[type=minecraft:slime]") == 0)
    chk("the chest opens now (a real click)", try_open("Cam", front_of(G["chest"], G["chest_facing"]), G["chest"]))

def t_tower():
    print("[tower]"); stage(); away("Cam"); away("Cam2"); reset_all(); time.sleep(4)
    chk("asleep by the niche: an invisible vex (scale 2.5, NoAI) with her model, the name empty", count(LADY) == 1 and "1b" in nbt(LADY, "NoAI") and count("@e[type=minecraft:item_display,tag=le.tr_lm]") == 1)
    tpp("Cam", *ROOM_IN); tpp("Cam2", ROOM_IN[0] + 2, ROOM_IN[1], ROOM_IN[2]); time.sleep(1.5)
    chk("Cam and Cam2 in the room: she wakes, 60 + 20 x 2 = 100 (+500), her name «Белая Дама»", sc("#t.st") == 1 and abs((hp(LADY) or 0) - 600) < 1
        and "Белая Дама" in nbt("@e[type=minecraft:text_display,tag=le.tr_ln,limit=1]", "text"))
    R("effect clear Cam minecraft:resistance"); time.sleep(0.3); h0 = taken("Cam"); t0 = sc("#t.touches") or 0
    R(f"execute as {LADY} run data merge entity @s {{NoAI:1b}}"); R(f"execute at Cam run tp {LADY} ~0.4 ~0.2 ~0.4"); time.sleep(1.0)
    chk("her touch: hurt (%.1f) and the Frost (slowness, mining fatigue)" % (taken("Cam") - h0), (sc("#t.touches") or 0) > t0 and taken("Cam") - h0 > 0
        and passed('execute if entity @a[name=Cam,nbt={active_effects:[{id:"minecraft:mining_fatigue"}]}]'))
    R("effect give Cam minecraft:resistance infinite 4 true"); R(f"execute as {LADY} run data merge entity @s {{NoAI:0b}}")
    tpp("Cam", ROOM_IN[0], ROOM_IN[1], ROOM_IN[2] + 4, 180, 0); tpp("Cam2", ROOM_IN[0] + 2, ROOM_IN[1], ROOM_IN[2]); time.sleep(0.5)
    w0 = sc("#t.wails") or 0; R("scoreboard players set #t.wl le.tr 1"); time.sleep(0.4)
    lp = pos(LADY)
    chk("the wail (%d -> %d): darkness on Cam" % (w0, sc("#t.wails") or 0), (sc("#t.wails") or 0) > w0 and passed('execute if entity @a[name=Cam,nbt={active_effects:[{id:"minecraft:darkness"}]}]'))
    chk("darkness on Cam2 too (in the room)", passed('execute if entity @a[name=Cam2,nbt={active_effects:[{id:"minecraft:darkness"}]}]'))
    chk("she is inside a wall now %s" % lp, lp is not None and (lp[0] < 472 or lp[0] > 483 or lp[2] < 33 or lp[2] > 44))
    time.sleep(1.8)
    lp = pos(LADY); cp = pos("Cam")
    behind = False
    if lp and cp:
        ang = math.degrees(math.atan2(-(lp[0] - cp[0]), lp[2] - cp[2]))        # the yaw from Cam to her
        diff = abs((ang - 180 + 180) % 360 - 180)                              # Cam looks at yaw 180 (north)
        behind = diff > 120 or math.dist(lp[::2], cp[::2]) < 1.0
    chk("1.5 s later out of a wall behind the player nearest to her (> 120 degrees from the view)", behind, "she %s, Cam %s" % (lp, cp))
    # she never leaves the room: 10 s of watching
    out = 0
    for _ in range(20):
        p = pos(LADY)
        if p and not (471.3 <= p[0] <= 483.7 and 188.5 <= p[1] <= 197 and 32.3 <= p[2] <= 44.7): out += 1
        time.sleep(0.5)
    chk("never outside the room in 10 s of flying (outside seen %d times; the leash puts her back)" % out, out == 0)
    # an arrow: half
    R(f"execute as {LADY} run data merge entity @s {{NoAI:1b}}"); tpp("Cam", ROOM_IN[0], ROOM_IN[1], ROOM_IN[2], 0, 0); tpp("Cam2", ROOM_IN[0] + 3, ROOM_IN[1], ROOM_IN[2])
    R("scoreboard players set #t.wl le.tr 100000"); R(f"tp {LADY} {ROOM_IN[0]} {ROOM_IN[1]} {ROOM_IN[2] + 4}"); time.sleep(0.8)
    h0 = hp(LADY); hv = sc("#t.halved") or 0
    R(f"damage {LADY} 8 minecraft:arrow by Cam"); time.sleep(0.6)        # an arrow of Cam (the damage type of a projectile, by the player)
    d = h0 - hp(LADY)
    chk("an arrow of Cam (8): half of it taken back (halved %d -> %d, lost %.1f: 4)" % (hv, sc("#t.halved") or 0, d), (sc("#t.halved") or 0) > hv and abs(d - 4) < 0.6)
    h0 = hp(LADY); R(f"execute at {LADY} run setblock ~ ~ ~ minecraft:fire"); R(f"data merge entity {LADY} {{Fire:100s}}"); time.sleep(2)
    R(f"execute at {LADY} run fill ~-1 ~-1 ~-1 ~1 ~1 ~1 minecraft:air replace minecraft:fire")
    chk("fire does nothing (%.1f -> %.1f)" % (h0, hp(LADY)), abs(h0 - hp(LADY)) < 0.01)
    # her death
    R("kill @e[type=minecraft:experience_orb]"); t0 = trophies("Cam"), trophies("Cam2")
    R(f"damage {LADY} 5 minecraft:player_attack by Cam2"); time.sleep(0.7)
    R(f"damage {LADY} 300 minecraft:player_attack by Cam")
    chk("dead after 2 s of fading: the lock off, the XP 9, «Башня опустела.», the lantern out", wait(lambda: sc("#t.st") == 2, 5) and count(LADY) == 0
        and blk(*TW["lock"], "minecraft:air") and count("@e[type=minecraft:experience_orb]") == 1 and not blk(*TW["lantern"], "minecraft:soul_lantern"))
    t1 = trophies("Cam"), trophies("Cam2")
    chk("a trophy to each of the fight (Cam %d -> %d, Cam2 %d -> %d)" % (t0[0], t1[0], t0[1], t1[1]), t1 == (t0[0] + 1, t0[1] + 1))
    chk("the chest opens now (a real click)", try_open("Cam", front_of(TW["chest"], "north"), TW["chest"]))

def t_lock():
    print("[lock]"); stage(); away("Cam"); away("Cam2"); reset_all(); time.sleep(3)
    for name, ch, face, lockb in (("ogre", O["chest"], "east", "minecraft:brown_wool"), ("grotto", G["chest"], G["chest_facing"], "minecraft:slime_block"),
                                  ("tower", TW["chest"], "north", "minecraft:cracked_stone_bricks")):
        R(f"forceload add {ch[0]} {ch[2]}"); time.sleep(0.5)
        chk("%s: the lock (%s) over the chest" % (name, lockb), blk(ch[0], ch[1] + 1, ch[2], lockb))
        R(f"forceload remove {ch[0]} {ch[2]}")
        R(f"execute as {OGRE} run data merge entity @s {{NoAI:1b}}")
        chk("%s: while its owner lives the chest does not open (a real click)" % name, not try_open("Cam", front_of(ch, face), ch))
    R("setblock %d %d %d minecraft:air" % (G["lock"][0], G["lock"][1], G["lock"][2]))
    chk("(control) the grotto's chest without the lock opens with the same click", try_open("Cam", front_of(G["chest"], G["chest_facing"]), G["chest"]))
    reset_all()

def t_leash():
    print("[leash]"); stage(); away("Cam"); away("Cam2"); reset_all(); time.sleep(3)
    into_den("Cam", DEN_IN); time.sleep(1.5)
    R(f"tp {OGRE} {DEN_IN[0] + 30} {DEN_IN[1]} {DEN_IN[2]}"); time.sleep(0.5)
    p = pos(OGRE)
    chk("the Ogre put outside the den: back in the middle of it", p is not None and O["cave"][0] - 2 <= p[0] <= O["cave"][2] + 2)
    R(f"damage {OGRE} 50 minecraft:player_attack by Cam"); tpp("Cam", *DEN_OUT); time.sleep(12)
    chk("nobody in the den 10 s (Cam by the mouth): asleep on his bed with full health (640)", sc("#o.st") == 0 and abs((hp(OGRE) or 0) - 640) < 1
        and passed(f"execute as {OGRE} on vehicle if entity @s[tag=le.tr_oseat]"))
    tpp("Cam", *LEDGE); time.sleep(1.5)
    R(f"execute as {JELLY} run damage @s 300 minecraft:player_attack by Cam"); time.sleep(2)
    n = count(JELLY); g0 = sc("#g.g") or 0; away("Cam"); t0 = time.time()
    ok_ = wait(lambda: sc("#g.st") == 0, 60, 1.0)
    chk("the Jelly split (%d bodies), everybody far away: the grotto unloads, 10 s later asleep again, a new generation (%.0f s)" % (n, time.time() - t0),
        n == 3 and ok_ and (sc("#g.g") or 0) > g0)
    tpp("Cam", *GOUT); time.sleep(5)
    chk("back at the grotto: one big body asleep by the ledge, the old ones gone", count(JELLY) == 1 and count(jel("scores={le.trs=3}")) == 1
        and count("@e[type=minecraft:item_display,tag=le.tr_jm]") == 1 and "1b" in nbt(JELLY1, "NoAI"))
    tpp("Cam", *ROOM_IN); time.sleep(1.5); tpp("Cam", *TOUT); time.sleep(12)
    chk("the Lady: nobody in the room 10 s (Cam on the ledges' start): asleep by the niche again", sc("#t.st") == 0 and count(LADY) == 1 and "1b" in nbt(LADY, "NoAI"))

def t_peace():
    print("[peace]"); stage(); away("Cam"); away("Cam2"); reset_all(); time.sleep(2)
    R("difficulty peaceful"); into_den("Cam", DEN_OUT); time.sleep(3); tpp("Cam2", *LEDGE); time.sleep(3)
    chk("peaceful, the den and the grotto loaded: no Ogre, no Jelly, both dead (2) without trophies, the locks off",
        count(OGRE) == 0 and count(JELLY) == 0 and stor("ogre") == 2 and stor("grotto") == 2 and blk(*O["lock"], "minecraft:air") and blk(*G["lock"], "minecraft:air"))
    tpp("Cam", *ROOM_IN); time.sleep(3)
    chk("the tower: no Lady, the lock off", count(LADY) == 0 and stor("tower") == 2 and blk(*TW["lock"], "minecraft:air"))
    R("difficulty easy"); reset_all()

def t_bones():
    print("[bones]"); stage(prot=True)
    s = O["signs"]
    gaps = [math.dist((a[0], a[2]), (b[0], b[2])) for a, b in zip(s, s[1:])]
    chk("%d signs (12..20), %.1f..%.1f apart (8..12), the way %.0f from the trail at %s" % (len(s), min(gaps), max(gaps), O["way_len"], O["trail_start"]),
        12 <= len(s) <= 20 and min(gaps) >= 8 and max(gaps) <= 12)
    tpp("Cam", O["trail_start"][0] + 0.5, 200, O["trail_start"][1] + 0.5); time.sleep(3)
    R("execute as Cam at @s run tp @s ~ ~ ~"); R("spreadplayers %s %s 0 1 false Cam" % (O["trail_start"][0] + 0.5, O["trail_start"][1] + 0.5)); time.sleep(3)
    k = 0
    for (x, y, z, kind) in s:
        if kind == "skull": k += blk(x, y, z, "minecraft:skeleton_skull")
        elif kind == "ribs": k += blk(x, y, z, "minecraft:bone_block")
    nb = sum(1 for q in s if q[3] == "bone")
    chk("the skulls and ribs stand (%d of %d)" % (k, len(s) - nb), k == len(s) - nb)
    first = s[0]; d1 = math.dist((first[0], first[2]), O["trail_start"]); d2 = math.dist((s[1][0], s[1][2]), O["trail_start"])
    chk("the first two signs %.1f and %.1f from the trail (seen from it: the frame docs/reports/T-034/bones_trail.png)" % (d1, d2), d1 <= 14 and d2 <= 24)

def t_window():
    print("[window]"); stage(); reset_all(); tpp("Cam", 470.5, 167, 20.5); time.sleep(3)
    lan = TW["lantern"]
    R("time set 18000"); time.sleep(2.5)
    chk("night: the soul lantern hangs in the window", blk(*lan, "minecraft:soul_lantern"))
    R("time set 6000"); time.sleep(2.5)
    chk("day: none", blk(*lan, "minecraft:air"))
    R("time set 18000"); R("scoreboard players set #t.st le.tr 2"); time.sleep(2.5)
    chk("the Lady dead: the window stays dark at night", blk(*lan, "minecraft:air"))
    R("time set 6000"); reset_all()

def t_vaults():
    print("[vaults]")
    got = {"r1_ogre": 0, "r1_grotto": 0, "r1_tower": 0}; lines = []
    for i in range(10):
        for v in got: R(f"scoreboard players set #o.{v} le.vt 0")
        R("function last_ember:vault/reset_staffs"); R("function last_ember:vault/relayout_auto"); time.sleep(0.4)
        mains = {}
        for v in got:
            m = tc.score("#m.%s" % v, "le.vt")
            mains[v] = m
            if m is not None and 1 <= m <= 5: got[v] += 1
        lines.append(mains)
    print("     layouts:", lines)
    chk("in 10 layouts the staff of R1 (main 1..5) lay in each of the three at least once: %s" % got, all(n >= 1 for n in got.values()))

def t_zones():
    print("[zones]"); stage(prot=True); away("Cam2")
    def can_break(x, y, z):
        R(f"gamemode survival Cam"); tpp("Cam", x + 0.5, y + 1, z + 0.5); time.sleep(2.5)
        return "2" in nbt("Cam", "playerGameType")
    chk("the den: adventure (cannot be broken)", can_break(O["cave"][0] + 8, F, O["cave"][1] + 8))
    chk("the grotto: adventure", can_break(int(LEDGE[0]), W + 1, int(LEDGE[2])))
    c = TW["ledges"][12]
    chk("the ledges to the tower: adventure (the castle's zones)", can_break(c["x"], c["f"] - 1, c["z"]))
    chk("the tower's room: adventure", can_break(477, TW["floor"], 37))

def t_restart():
    print("[restart]"); stage(); away("Cam"); away("Cam2"); reset_all(); time.sleep(2)
    into_den("Cam", DEN_IN); time.sleep(1.5)
    chk("the Ogre awake before the restart", sc("#o.st") == 1)
    R("scoreboard players set #g.st le.tr 2"); R("function last_ember:treasury/gen/grotto/save")
    tm.restart(); stage(); away("Cam"); away("Cam2"); time.sleep(2)
    into_den("Cam", DEN_OUT)
    chk("after the restart: the Ogre asleep on his bed, one only (what the fight left gone)", wait(lambda: sc("#o.st") == 0 and count("@e[type=minecraft:zombie,tag=le.tr_ogre]") == 1
        and passed(f"execute as {OGRE} on vehicle if entity @s[tag=le.tr_oseat]"), 20, 1.0))
    tpp("Cam", *GOUT)
    chk("the dead Jelly stays dead (no body)", wait(lambda: sc("#g.st") == 2 and count(JELLY) == 0, 15, 1.0) and stor("grotto") == 2)
    reset_all()

def t_perf():
    print("[perf]"); stage(); away("Cam"); away("Cam2"); reset_all(); time.sleep(2)
    res = {}
    into_den("Cam", DEN_IN); tpp("Cam2", *DEN_FAR); time.sleep(2)
    p = tm.prof(10); res["ogre"] = p
    tpp("Cam", *LEDGE); tpp("Cam2", LEDGE[0] + 2, LEDGE[1], LEDGE[2]); time.sleep(2)
    R(f"execute as {JELLY} run damage @s 300 minecraft:player_attack by Cam"); time.sleep(2.5)
    R(f"execute as {JELLY} run damage @s 300 minecraft:player_attack by Cam"); time.sleep(2.0)
    p = tm.prof(10); res["grotto"] = p; peak = count(JELLY)
    tpp("Cam", *ROOM_IN); tpp("Cam2", ROOM_IN[0] + 2, ROOM_IN[1], ROOM_IN[2]); time.sleep(2)
    p = tm.prof(10); res["tower"] = p
    for k, v in res.items():
        tr = sum(t for f, t in v.items() if f.startswith("last_ember:treasury"))
        print("     %s: tick %.1f ms, treasury/* %.3f ms" % (k, v.get("tick", 0), tr))
        chk("%s with two players: treasury/* %.2f ms a tick (< 2.0)%s" % (k, tr, " (bodies %d)" % peak if k == "grotto" else ""), tr < 2.0)
    reset_all()

GROUPS = dict(build=t_build, ogre=t_ogre, grotto=t_grotto, split=t_split, tower=t_tower, lock=t_lock, leash=t_leash, peace=t_peace, bones=t_bones,
              window=t_window, vaults=t_vaults, zones=t_zones, restart=t_restart, perf=t_perf)
if __name__ == "__main__":
    which = sys.argv[1:] or list(GROUPS)
    for g in which:
        if g in ("ogre", "split", "tower", "lock"): tm.fresh()          # the clicks (chests, the shield) on fresh clients (T-033)
        GROUPS[g]()
    print("\nT-034 treasuries: %d ok, %d failed" % (ok, bad))
    sys.exit(1 if bad else 0)
