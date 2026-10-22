#!/usr/bin/env python3
"""T-012: the ring and the server crash (kill -9) / a normal logout. Restarts the local test server several times and relaunches the dev client Cam.
Usage: python3 tools/test_ring_crash.py [s1 s2 s3 s4 ...]   (s1: kill -9 after a save in the ring, s2: the same with the storage record lost,
s3: kill -9 right after putting the ring on (old save), s4: a normal logout in the ring, s5: kill -9 while the player data is newer than the storage)"""
import importlib.util, os, re, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
tr = load("test_ring"); rc = tr.rc; tc = tr.tc
chk = tr.chk
def sh(cmd): return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT).stdout
def server_pid():
    o = sh("pgrep -f 'server-26.3.jar nogui'").split(); return int(o[0]) if o else None
def rcon_up():
    try: return "players" in rc.run("list") or "There are" in rc.run("list")
    except Exception: return False
def kill_clients(): sh("pkill -f 'username Cam' ; pkill -f 'username Cam2'; true")
def crash():
    pid = server_pid(); sh(f"kill -9 {pid}"); time.sleep(2.0); kill_clients(); time.sleep(1.0)
def start_server():
    subprocess.Popen("nohup tools/server.sh start > /tmp/ring_srv.out 2>&1 &", shell=True, cwd=ROOT, start_new_session=True)
    for _ in range(120):
        time.sleep(2)
        if rcon_up(): return True
    return False
def join(name="Cam"):
    subprocess.Popen(f"nohup python3 tools/client_launch.py > /tmp/ring_cl.out 2>&1 &", shell=True, cwd=ROOT, start_new_session=True)
    for _ in range(90):
        time.sleep(2)
        try:
            if name in rc.run("list"): break
        except Exception: pass
    time.sleep(6.0)
def prep_ring(dress_after_save=False):
    tr.arena(); tr.halfling(); tr.dress(); time.sleep(0.4); return tr.snap("Cam")
def dup_count():
    inv = rc.run("data get entity Cam Inventory"); return inv.count("diamond_chestplate") + inv.count("iron_boots") + inv.count("leather_leggings")
def verdict(name, before):
    time.sleep(3.0)
    chk(f"{name}: the armor is on him, identical", tr.snap("Cam") == before, [(k, before[k][:60], tr.snap("Cam")[k][:60]) for k in before if before[k] != tr.snap("Cam")[k]])
    chk(f"{name}: nothing doubled (no armor pieces in the inventory)", dup_count() == 0, dup_count())
    chk(f"{name}: no ring state (not on, no invisibility, armor value back)", not tr.on() and "invisibility" not in tr.effects() and abs((tr.num(rc.run("attribute Cam minecraft:armor get")) or 0) - 12.0) < 0.01, (tr.on(), tr.effects()[:80], rc.run("attribute Cam minecraft:armor get")))
    chk(f"{name}: the ring is not lost (in the inventory)", tr.has_ring(), None)
    chk(f"{name}: the storage record is gone", "No elements" in rc.run('data get storage last_ember:ring p') or "Found no" in rc.run('data get storage last_ember:ring p') or "{}" in rc.run('data get storage last_ember:ring p'), rc.run('data get storage last_ember:ring p')[:80])
def run_case(name, setup):
    print(f"[{name}]"); before = setup(); crash(); assert start_server(), "server did not come up"; join(); verdict(name, before)
def s1():
    def setup():
        b = prep_ring(); tr.put_ring_on(); time.sleep(1.0); assert tr.on(); rc.run("save-all flush"); time.sleep(2.0); return b
    run_case("kill -9 after a save, in the ring", setup)
def s2():
    def setup():
        b = prep_ring(); tr.put_ring_on(); time.sleep(1.0); assert tr.on(); rc.run("data remove storage last_ember:ring p"); rc.run("save-all flush"); time.sleep(2.0); return b
    run_case("kill -9, the storage has no record (the copy in the ring)", setup)
def s3():
    def setup():
        b = prep_ring(); rc.run("save-all flush"); time.sleep(2.0); tr.put_ring_on(); time.sleep(1.0); assert tr.on(); return b
    run_case("kill -9 right after putting on (the save is older)", setup)
def s4():
    print("[normal logout in the ring]"); b = prep_ring(); tr.put_ring_on(); time.sleep(1.0); assert tr.on()
    rc.run("kick Cam"); time.sleep(3.0); rc.run("save-all flush"); time.sleep(2.0); kill_clients(); time.sleep(1.0); join(); verdict("logout and login in the ring", b)
def s5():
    def setup():
        b = prep_ring(); tr.put_ring_on(); time.sleep(1.0); assert tr.on(); rc.run("save-all flush"); time.sleep(2.0)
        # the player data of the save has the ring on; now the ring is taken off (the armor is back), the storage is cleaned: both are newer than the save, none of it is saved
        rc.run("item replace entity Cam armor.head with minecraft:air"); time.sleep(1.0); return b
    run_case("kill -9: the save has the ring on, the armor returned after it (an older save than the world state)", setup)
if __name__ == "__main__":
    for w in (sys.argv[1:] or ["s1", "s2", "s3", "s4", "s5"]): globals()[w]()
    print(f"\n{tr.ok} ok, {tr.bad} failed")
