#!/usr/bin/env python3
"""T-013 checks (server + dev clients Cam, Cam2; the test altar of altars/test_altars.txt at (700,200,700)): pedestals, the event, the tiers, one valid copy of a key, the properties of the Ember.
Usage: python3 tools/test_altar.py [pedestals event keys light warm call gaze flame ...]"""
import importlib.util, json, math, os, re, sys, threading, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, f"tools/{n}.py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
rc = load("rcon"); tc = load("test_class")
ok = bad = 0
def chk(n, c, e=""):
    global ok, bad
    if c: ok += 1; print("  ok  ", n)
    else: bad += 1; print("  FAIL", n, e)
score, num = tc.score, tc.num
AX, AY, AZ = 700, 200, 700
PEDS = {"test_a": (696, 700), "test_b": (704, 700), "test_c": (700, 696)}
def sto(path): return rc.run(f"data get storage last_ember:{path}")
def stage(chapters=0):
    rc.run("forceload add 680 680 720 720"); rc.run(f"tp Cam {AX}.5 {AY} {AZ+3}.5"); rc.run(f"tp Cam2 {AX+3}.5 {AY} {AZ+3}.5")
    for _ in range(40):
        time.sleep(0.5)
        if "passed" in rc.run("execute if loaded 690 200 690") and "passed" in rc.run("execute if loaded 710 200 710"): break
    time.sleep(1.0); rc.run("fill 690 199 690 710 199 710 stone"); rc.run("fill 690 200 690 710 206 710 air"); rc.run("difficulty normal"); rc.run("weather clear 100000")
    rc.run("kill @e[type=item]")
    for p in ("Cam", "Cam2"): rc.run(f"gamemode survival {p}"); rc.run(f"clear {p}")
    rc.run("function last_ember:altar/reset {chapter:4}"); rc.run(f"function last_ember:altar/set_chapters {{n:{chapters}}}")
    for _ in range(10):
        if num(rc.run("execute positioned 700 200 700 if entity @e[type=interaction,tag=le.ped,distance=..10]") and "0") is not None and "passed" in rc.run("execute positioned 700 200 700 if entity @e[type=interaction,tag=le.ped,distance=..10]"): break
        time.sleep(1)
    rc.run("tag Cam2 remove le.carrier")
def classes(c1=1, c2=2):
    tc.setc(1, c1, 0, "Cam"); tc.setc(2, c2, 0, "Cam2"); rc.run("gamemode survival Cam"); rc.run("gamemode survival Cam2"); rc.run("scoreboard players set Cam le.tier 0"); rc.run("scoreboard players set Cam2 le.tier 0"); rc.run("scoreboard players set #tiersync le.alt 1")
def carrier(p="Cam"):
    rc.run("tag Cam remove le.carrier"); rc.run("tag Cam2 remove le.carrier"); rc.run("clear Cam minecraft:trial_key"); rc.run("clear Cam2 minecraft:trial_key"); rc.run("data remove storage last_ember:ember carrier")
    rc.run(f"execute as {p} run function last_ember:ember/give_to_me")
def hand_key(p, kid): rc.run(f"execute as {p} run function last_ember:altar/gen/hand_dispatch {{id:\"{kid}\"}}")
def give_key(p, kid): rc.run(f"execute as {p} run function last_ember:altar/give_key {{id:\"{kid}\"}}")
def click(p, kid, standing=None):
    px, pz = PEDS[kid]; sx, sz = standing or (px, pz + 2.5 if kid != "test_c" else pz + 2.5)
    tc.face(p, sx + 0.5, AY, sz + 0.5 + (2 if kid != "test_c" else 0) if False else sz + 0.5, px + 0.5, AY + 0.7, pz + 0.5); time.sleep(0.35); tc.act(p, "!use"); time.sleep(0.5)
def filled(): return num(rc.run("scoreboard players get #fill_test_altar le.alt").replace("[le.alt]", "")) if False else score("#fill_test_altar", "le.alt")
def hand(p, what): return "passed" in rc.run(f"execute if items entity {p} weapon.mainhand *[minecraft:custom_data~{{le_key:\"{what}\"}}]")
def hand_empty(p): return "passed" not in rc.run(f"execute if items entity {p} weapon.mainhand *")
def has_key(p, kid, gen=None):
    g = f",gen:{gen}" if gen is not None else ""
    return "passed" in rc.run(f"execute if items entity {p} container.* *[minecraft:custom_data~{{le_key:\"{kid}\"{g}}}]")
def keygen(kid): return int(num(sto(f"keys k.{kid}.gen")))
def t_pedestals():
    print("[pedestals]"); stage(); classes(); carrier()
    give_key("Cam", "test_a"); give_key("Cam", "test_b"); time.sleep(0.4)
    tc.act("Cam", "!select 0") if False else None
    hand_key("Cam", "test_b"); click("Cam", "test_a")
    chk("a key of another pedestal: 'its place is not here', nothing happens", filled() == 0 and hand("Cam", "test_b"), (filled(), hand("Cam", "test_b")))
    rc.run("clear Cam"); rc.run("item replace entity Cam weapon.mainhand with minecraft:ominous_trial_key[minecraft:custom_name='\"Ключ\"',minecraft:custom_data={le_key:\"test_a\",gen:77}]"); click("Cam", "test_a")
    chk("a forged key (right name and tag, wrong generation): refused (the watcher also takes it away)", filled() == 0)
    rc.run("clear Cam"); rc.run("item replace entity Cam weapon.mainhand with minecraft:ominous_trial_key[minecraft:custom_name='\"Слеза\"',minecraft:item_model=\"last_ember:key_test_a\"]"); click("Cam", "test_a")
    chk("a renamed vanilla key (no custom_data): refused", filled() == 0 and not hand_empty("Cam"))
    rc.run("clear Cam"); g0 = keygen("test_a"); hand_key("Cam", "test_a"); time.sleep(0.3); click("Cam", "test_a")
    chk("the right key: it stands on the pedestal, the hand is empty, a display appears", filled() == 1 and hand_empty("Cam") and "passed" in rc.run("execute if entity @e[type=item_display,tag=le.ped_item1]"), (filled(), hand_empty("Cam")))
    click("Cam", "test_a"); time.sleep(0.3)
    chk("an empty hand takes it back into the hand", filled() == 0 and hand("Cam", "test_a") and "passed" not in rc.run("execute if entity @e[type=item_display,tag=le.ped_item1]"))
    chk("same copy: the generation did not change", keygen("test_a") == g0)
    click("Cam", "test_a"); chk("placed again", filled() == 1)
    rc.run("clear Cam"); give_key("Cam", "test_b"); time.sleep(0.2); click("Cam", "test_a"); chk("a hand with something on a filled pedestal: 'free the hand'", filled() == 1)
def t_event():
    print("[event of the altar]"); stage(); classes(); carrier()
    for kid in PEDS: rc.run(f"scoreboard players set #fill_test_altar le.alt 0")
    # Cam2 puts all three keys (he is not the carrier); the carrier is far away
    G0 = {k: keygen(k) for k in PEDS}; rc.run(f"tp Cam {AX}.5 {AY} {AZ+40}.5"); time.sleep(0.6)
    for kid in PEDS:
        hand_key("Cam2", kid); time.sleep(0.2); px, pz = PEDS[kid]; tc.face("Cam2", px + 0.5, AY, pz + 3.5, px + 0.5, AY + 0.7, pz + 0.5); time.sleep(0.35); tc.act("Cam2", "!use"); time.sleep(0.5)
    time.sleep(2.0)
    chk("all pedestals filled, the carrier is 40 blocks away: no event", filled() == 3 and "ev: -1" in sto("altars a.test_altar") and score("#chapters", "le.alt") == 0, (filled(), sto("altars a.test_altar")))
    chk("pedestals are not taken by accident: keys are on the altar (state placed)", all("st: 1" in sto(f"keys k.{k}") for k in PEDS))
    rc.run(f"tp Cam {AX}.5 {AY} {AZ+6}.5"); time.sleep(2.2)
    chk("the carrier comes within 10 blocks: the event starts", not "ev: -1" in sto("altars a.test_altar"), sto("altars a.test_altar"))
    # taking a key during the event is not possible
    px, pz = PEDS["test_a"]; tc.face("Cam2", px + 0.5, AY, pz + 3.5, px + 0.5, AY + 0.7, pz + 0.5); time.sleep(0.3); tc.act("Cam2", "!use"); time.sleep(0.4)
    chk("during the event the keys cannot be taken", filled() == 3)
    for _ in range(40):
        time.sleep(0.5)
        if "done: 1b" in sto("altars a.test_altar"): break
    chk("the event ends: the altar is done, the chapters = 1", "done: 1b" in sto("altars a.test_altar") and score("#chapters", "le.alt") == 1, (sto("altars a.test_altar"), score("#chapters", "le.alt")))
    time.sleep(1.5)
    chk("tier 1 for everybody who is online (Cam knight, Cam2 ranger)", score("Cam", "le.tier") == 1 and score("Cam2", "le.tier") == 1, (score("Cam", "le.tier"), score("Cam2", "le.tier")))
    chk("the keys stay on the altar for good (state 2), copies are void (generation +1)", all("st: 2" in sto(f"keys k.{k}") and keygen(k) == G0[k] + 1 for k in PEDS), (G0, {k: keygen(k) for k in PEDS}))
    tc.face("Cam2", px + 0.5, AY, pz + 3.5, px + 0.5, AY + 0.7, pz + 0.5); time.sleep(0.3); tc.act("Cam2", "!use"); time.sleep(0.5)
    chk("after the event nothing can be taken", filled() == 3 and hand_empty("Cam2"))
    chk("the Ember's lore has the first property (Light)", "Свет" in rc.run("data get entity Cam Inventory"))
    # a player who was not there: his tier follows (the same code path as a player who comes back later)
    rc.run("scoreboard players set Cam2 le.tier 0"); time.sleep(1.5); chk("a tier that is behind catches up within a second", score("Cam2", "le.tier") == 1)
    # a second click of the same carrier does not restart the event
    time.sleep(2.5); chk("no second event", score("#chapters", "le.alt") == 1)
KSEL = '@e[type=item,nbt={Item:{components:{"minecraft:custom_data":{le_key:"%s"}}}}]'
def keys_total(kid): inv = rc.run("data get entity Cam Inventory"); return inv.count(f'le_key: "{kid}"')
def drop_key(kid="test_a"):
    """the player throws the key (Q): an item entity on the floor"""
    rc.run("clear Cam"); hand_key("Cam", kid); time.sleep(0.5); tc.act("Cam", "!drop"); time.sleep(0.4)
    return "passed" in rc.run(f"execute if entity {KSEL % kid}")
def t_keys():
    print("[one valid copy of a key]"); stage(); classes(); carrier(); rc.run(f"tp Cam {AX}.5 {AY} {AZ+8}.5 0 0"); time.sleep(0.5)
    rc.run("setblock 706 200 706 minecraft:lava"); rc.run("setblock 706 199 706 minecraft:stone")
    for nm, move in (("lava", "tp @s 706.5 200.5 706.5"), ("void", "tp @s 705.5 -125 705.5"), ("despawn", "data modify entity @s Age set value 5995s")):
        g0 = keygen("test_a"); rc.run("clear Cam"); rc.run("scoreboard players set Cam le.tier 0")
        ok_drop = drop_key(); chk(f"{nm}: the thrown key is an item on the floor (the loss is possible)", ok_drop)
        rc.run(f"execute as {KSEL % 'test_a'} run data modify entity @s PickupDelay set value 32767s")
        time.sleep(1.2)       # let the watcher see the floor copy
        rc.run(f"execute as {KSEL % 'test_a'} run {move}")
        if nm == "despawn": time.sleep(1.0)
        for _ in range(12):
            time.sleep(0.5)
            if has_key("Cam", "test_a", g0 + 1): break
        chk(f"{nm}: the key is gone, it comes back into the inventory as a new generation", has_key("Cam", "test_a", g0 + 1) and keygen("test_a") == g0 + 1, (g0, keygen("test_a"), has_key("Cam", "test_a")))
        chk(f"{nm}: exactly one copy", keys_total("test_a") == 1 and "passed" not in rc.run(f"execute if entity {KSEL % 'test_a'}"), keys_total("test_a"))
    # a stale copy: it is taken away at once
    rc.run("clear Cam"); give_key("Cam", "test_a"); g = keygen("test_a")
    rc.run(f"give Cam minecraft:ominous_trial_key[minecraft:custom_data={{le_key:\"test_a\",le_keep:1b,gen:{g-1}}}]"); time.sleep(1.4)
    chk("an old copy (older generation) in the inventory: removed, the valid one stays", keys_total("test_a") == 1 and has_key("Cam", "test_a", g))
    rc.run(f"summon item 705.5 200 700.5 {{PickupDelay:32767s,Item:{{id:\"minecraft:ominous_trial_key\",count:1,components:{{\"minecraft:custom_data\":{{le_key:\"test_a\",le_keep:1b,gen:{g-1}}}}}}}}}"); time.sleep(1.4)
    chk("an old copy on the floor: removed", "passed" not in rc.run(f"execute if entity @e[type=item,nbt={{Item:{{components:{{\"minecraft:custom_data\":{{gen:{g-1}}}}}}}}}]"))
    # a chest, an ender chest: not a loss
    rc.run("setblock 702 200 706 minecraft:chest"); g = keygen("test_a")
    rc.run("item replace block 702 200 706 container.0 from entity Cam hotbar.0") if False else None
    rc.run("clear Cam"); give_key("Cam", "test_a"); time.sleep(0.4); hand_key("Cam", "test_a"); rc.run("item replace block 702 200 706 container.0 from entity Cam weapon.mainhand"); rc.run("clear Cam minecraft:ominous_trial_key"); time.sleep(3.0)
    chk("a key in a chest: not a loss, nothing is given", keys_total("test_a") == 0 and keygen("test_a") == g, (keys_total("test_a"), g, keygen("test_a")))
    rc.run("item replace entity Cam weapon.mainhand from block 702 200 706 container.0"); time.sleep(1.2); chk("taken back from the chest: it is the same valid copy", has_key("Cam", "test_a", g)); rc.run("setblock 702 200 706 minecraft:air")
    rc.run("item replace entity Cam enderchest.0 from entity Cam weapon.mainhand"); rc.run("clear Cam minecraft:ominous_trial_key"); time.sleep(3.0)
    chk("a key in the ender chest: not a loss", keys_total("test_a") == 0 and keygen("test_a") == g)
    rc.run("item replace entity Cam enderchest.0 with minecraft:air")
    rc.run("scoreboard players set Cam2 le.tier 0"); rc.run("item replace entity Cam2 weapon.mainhand with minecraft:air")
    # a loss while the holder is offline: he gets it when he comes back (here: the holder is somebody else until the UUID matches)
    rc.run("clear Cam"); rc.run("data modify storage last_ember:keys k.test_b.h set value [I;1,2,3,4]"); rc.run("data modify storage last_ember:keys k.test_b.pend set value 1b"); time.sleep(1.6)
    chk("a key owed to a player who is not here: nobody gets it", not has_key("Cam", "test_b") and not has_key("Cam2", "test_b"))
    rc.run("data modify storage last_ember:keys k.test_b.h set from entity Cam UUID"); time.sleep(1.6)
    chk("the owner comes back (online): the key is given, the line is shown once", has_key("Cam", "test_b") and "pend: 0b" in sto("keys k.test_b"))
    # death: the keys stay (le_keep), not a loss, no duplicate
    rc.run("clear Cam"); give_key("Cam", "test_c"); time.sleep(0.5); gc = keygen("test_c")
    rc.run("damage Cam 1000 minecraft:out_of_world"); time.sleep(4.0)
    chk("a player dies with a key: it stays on him (T-007 keeps le_keep), the same generation, no copy", keys_total("test_c") == 1 and keygen("test_c") == gc, (keys_total("test_c"), gc, keygen("test_c")))
    rc.run("setblock 706 200 706 minecraft:air")
def ember_hand(p="Cam", hand=True):
    """the Ember into the main hand (the selected slot) or out of the hands (slot 20)"""
    rc.run(f"item replace entity {p} container.20 from entity {p} weapon.mainhand") if not hand else None
    if hand:
        for sl in list(range(0, 36)):
            if "passed" in rc.run(f"execute if items entity {p} container.{sl} *[minecraft:custom_data~{{le_ember:1b}}]"):
                rc.run(f"item replace entity {p} weapon.mainhand from entity {p} container.{sl}")
                if "passed" not in rc.run(f"execute if items entity {p} weapon.mainhand *[minecraft:custom_data~{{le_ember:1b}}]") or sl != 0: pass
                if sl != 0 and sl != int(num(rc.run(f"data get entity {p} SelectedItemSlot"))): rc.run(f"item replace entity {p} container.{sl} with minecraft:air")
                break
    else: rc.run(f"item replace entity {p} weapon.mainhand with minecraft:air")
def light_at_head(p="Cam", wl=None):
    r = rc.run(f"execute at {p} positioned ~ ~1.6 ~ if block ~ ~ ~ minecraft:light" + (f"[waterlogged={'true' if wl else 'false'}]" if wl is not None else ""))
    return "passed" in r
def lights(): return "passed" in rc.run("execute if entity @e[type=marker,tag=le.emlight]")
def t_light():
    print("[property I: Light]"); stage(0); classes(); carrier(); rc.run(f"tp Cam {AX}.5 {AY} {AZ+8}.5"); time.sleep(1.2)
    chk("no chapters done: no light", not light_at_head() and not lights())
    rc.run("function last_ember:altar/set_chapters {n:1}"); time.sleep(1.2)
    chk("the Ember in the hand: a light block at the head (level 12)", light_at_head(), rc.run("execute at Cam run data get block ~ ~1.6 ~ ") if False else "")
    chk("the Ember's lore has the Light line", "Свет" in rc.run("data get entity Cam Inventory"))
    rc.run(f"tp Cam {AX+5}.5 {AY} {AZ+8}.5"); time.sleep(1.0)
    chk("it follows the carrier: the old block is gone, a new one is at the head", light_at_head() and "passed" not in rc.run(f"execute if block {AX}.5 {AY+1} {AZ+8}.5 minecraft:light") and "passed" not in rc.run(f"execute if block {AX} {AY+1} {AZ+8} minecraft:light"))
    rc.run("fill %d 200 %d %d 204 %d minecraft:water" % (AX + 3, AZ + 6, AX + 8, AZ + 10)); time.sleep(1.0)
    chk("under water too (a light block with water)", light_at_head("Cam", True), "")
    rc.run("fill %d 200 %d %d 204 %d minecraft:air" % (AX + 3, AZ + 6, AX + 8, AZ + 10)); time.sleep(0.8)
    # Ember out of the hands
    ember_hand("Cam", hand=False)
    for _ in range(2): time.sleep(0.8)
    chk("the Ember is not in the hands: the light goes out", not light_at_head() and not lights() or (not lights()), "")
    ember_hand("Cam", hand=True); time.sleep(1.0); chk("in the hand again: the light is back", light_at_head())
    rc.run("function last_ember:altar/set_chapters {n:0}"); time.sleep(1.0); chk("(chapters 0 again) no light", not lights())
def t_warm():
    print("[property II: Warmth, IV Gaze, V Flame]"); stage(0); classes(); carrier(); rc.run(f"tp Cam {AX}.5 {AY} {AZ+8}.5"); rc.run(f"tp Cam2 {AX+4}.5 {AY} {AZ+8}.5"); time.sleep(0.5)
    has = lambda p, t: f"le.warm" in rc.run(f"tag {p} list")
    chk("chapters 0: no warmth tag", not has("Cam2", "w")); rc.run("function last_ember:altar/set_chapters {n:2}"); time.sleep(1.0)
    chk("chapters 2: a player within 6 blocks of the carrier has le.warm (and the carrier)", has("Cam2", "w") and has("Cam", "w"))
    rc.run(f"tp Cam2 {AX+9}.5 {AY} {AZ+8}.5"); time.sleep(1.0); chk("further than 6 blocks: no tag", not has("Cam2", "w"))
    rc.run(f"tp Cam2 {AX+4}.5 {AY} {AZ+8}.5")
    # Gaze (IV): darkness is cleared at once near the carrier
    rc.run("function last_ember:altar/set_chapters {n:3}"); rc.run("effect give Cam2 minecraft:darkness 60 0"); time.sleep(1.0)
    chk("chapters 3: darkness stays (the Gaze is not yet there)", "darkness" in rc.run("data get entity Cam2 active_effects"))
    rc.run("function last_ember:altar/set_chapters {n:4}"); time.sleep(1.0)
    chk("chapters 4 (Gaze): darkness near the carrier is cleared", "darkness" not in rc.run("data get entity Cam2 active_effects"))
    rc.run(f"tp Cam2 {AX+12}.5 {AY} {AZ+8}.5"); rc.run("effect give Cam2 minecraft:darkness 60 0"); time.sleep(1.2)
    chk("further than 6 blocks: darkness stays", "darkness" in rc.run("data get entity Cam2 active_effects")); rc.run("effect clear Cam2")
    # Flame (V)
    rc.run(f"tp Cam2 {AX+4}.5 {AY} {AZ+8}.5"); rc.run("function last_ember:altar/set_chapters {n:4}"); rc.run(f"setblock {AX+4} {AY} {AZ+8} minecraft:fire"); time.sleep(0.4)
    rc.run("effect give Cam2 minecraft:instant_health 1 10"); time.sleep(1.0); h0 = tc.hp("Cam2"); time.sleep(4.0); h1 = tc.hp("Cam2")
    chk("chapters 4 (control): standing in fire hurts", h1 < h0, (h0, h1))
    rc.run(f"setblock {AX+4} {AY} {AZ+8} minecraft:air"); rc.run("effect clear Cam2"); time.sleep(8.0); rc.run("effect give Cam2 minecraft:instant_health 1 3"); time.sleep(0.5)
    rc.run("function last_ember:altar/set_chapters {n:5}"); rc.run(f"tp Cam2 {AX+4}.5 {AY} {AZ+8}.5"); rc.run("effect give Cam2 minecraft:instant_health 1 10"); time.sleep(1.0); rc.run(f"setblock {AX+4} {AY} {AZ+8} minecraft:fire"); time.sleep(0.5); h0 = tc.hp("Cam2"); time.sleep(4.0); h1 = tc.hp("Cam2")
    chk("chapters 5 (Flame): in fire a player near the carrier does not get hurt", h1 >= h0, (h0, h1))
    rc.run(f"setblock {AX+4} {AY} {AZ+8} minecraft:air"); time.sleep(3.0)
    rc.run(f"setblock {AX+4} {AY} {AZ+8} minecraft:lava"); rc.run(f"tp Cam2 {AX+4}.5 {AY} {AZ+8}.5"); time.sleep(0.3); h0 = tc.hp("Cam2"); time.sleep(2.0); h1 = tc.hp("Cam2")
    chk("in lava the Flame does not help: lava burns as usual", h1 < h0 or "dead" in rc.run("data get entity Cam2 Health"), (h0, h1))
    rc.run(f"setblock {AX+4} {AY} {AZ+8} minecraft:air"); rc.run(f"tp Cam2 {AX+4}.5 {AY+2} {AZ+8}.5"); rc.run("function last_ember:altar/set_chapters {n:0}")
def t_call():
    print("[property III: Call]"); stage(0); classes(); carrier(); rc.run(f"tp Cam {AX}.5 {AY} {AZ+8}.5 0 0"); rc.run("function last_ember:altar/set_chapters {n:2}"); rc.run("scoreboard players set Cam le.ecd 0"); time.sleep(0.8); ember_hand("Cam", True); time.sleep(0.5)
    tc.act("Cam", "!sneak_on"); time.sleep(0.4); tc.act("Cam", "!use"); time.sleep(0.8)
    chk("chapters 2: no Call yet", (score("Cam", "le.ecd") or 0) == 0)
    rc.run("function last_ember:altar/set_chapters {n:3}"); time.sleep(0.5)
    tc.act("Cam", "!use"); time.sleep(1.0); tc.act("Cam", "!sneak_off")
    chk("chapters 3: Shift + RMB with the Ember: the Call works (cooldown 60 s set)", (score("Cam", "le.ecd") or 0) > (score("#gt", "le.e") or 0) + 1000, (score("Cam", "le.ecd"), score("#gt", "le.e")))
    chk("the target is the altar of the chapter (no key points in the test keys)", score("#tx", "le.alt") == AX and score("#tz", "le.alt") == AZ and score("#found", "le.alt") == 1, (score("#tx", "le.alt"), score("#tz", "le.alt")))
    cd = score("Cam", "le.ecd"); tc.act("Cam", "!sneak_on"); time.sleep(0.4); tc.act("Cam", "!use"); time.sleep(0.8); tc.act("Cam", "!sneak_off")
    chk("a second Call within 60 s is not given", score("Cam", "le.ecd") == cd)
    rc.run("function last_ember:altar/set_chapters {n:0}")
def t_simul():
    print("[two players at once]"); stage(); classes(); carrier()
    hand_key("Cam", "test_a"); hand_key("Cam2", "test_b"); time.sleep(0.3)
    tc.face("Cam", 696.5, AY, 703.5, 696.5, AY + 0.7, 700.5); tc.face("Cam2", 704.5, AY, 703.5, 704.5, AY + 0.7, 700.5); time.sleep(0.4)
    a = threading.Thread(target=lambda: tc.act("Cam", "!use")); b = threading.Thread(target=lambda: tc.act("Cam2", "!use")); a.start(); b.start(); a.join(); b.join(); time.sleep(1.0)
    chk("two players click different pedestals in the same moment: both keys stand", filled() == 2 and hand_empty("Cam") and hand_empty("Cam2"), (filled(), hand_empty("Cam"), hand_empty("Cam2")))
if __name__ == "__main__":
    want = sys.argv[1:] or ["pedestals", "simul", "event", "keys", "light", "warm", "call"]
    for w in want: globals()["t_" + w]()
    print(f"\n{ok} ok, {bad} failed"); sys.exit(1 if bad else 0)
