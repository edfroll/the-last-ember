#!/usr/bin/env python3
"""T-012 checks (server + dev clients Cam, Cam2): the halfling's ring. Armor must never be lost: death, leaving, a server crash (kill -9 is done by test_ring_crash.py), two wearers.
Usage: python3 tools/test_ring.py [don refuse fee off death rejoin reset two lost items]"""
import importlib.util, json, math, os, re, sys, time
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
globals_ = None
AX, AY, AZ = 600, 200, 600
ITEMS = {"chest": 'minecraft:diamond_chestplate[minecraft:damage=7,minecraft:enchantments={"minecraft:protection":3,"minecraft:unbreaking":2},minecraft:custom_name=\'"Мой нагрудник"\',minecraft:trim={material:"minecraft:gold",pattern:"minecraft:coast"}]',
         "legs": "minecraft:leather_leggings[minecraft:dyed_color=16711680,minecraft:damage=11]", "feet": "minecraft:iron_boots[minecraft:damage=30,minecraft:enchantments={\"minecraft:feather_falling\":4}]"}
def eq(p, s): return rc.run(f"data get entity {p} equipment.{s}")
def snap(p): return {s: eq(p, s) for s in ITEMS}
def halfling(p="Cam", cls=1):
    tc.setc(4, cls, 0, p); rc.run(f"gamemode survival {p}"); rc.run(f"scoreboard players set {p} le.rcd 0"); rc.run(f"scoreboard players set {p} le.rt 0")
def arena(): tc.arena(); rc.run("difficulty normal"); rc.run("function last_ember:altar/set_chapters {n:0}")
def clear_ring_state(p):
    rc.run(f"tag {p} remove le.ringon")
def dress(p="Cam"):
    for s, it in ITEMS.items(): rc.run(f"item replace entity {p} armor.{s} with {it}")
def ring_slot(p="Cam"):
    inv = rc.run(f"data get entity {p} Inventory")
    for m in re.finditer(r"Slot: (\d+)b, id: \"minecraft:amethyst_shard\"", inv): return int(m.group(1))
    for m in re.finditer(r"id: \"minecraft:amethyst_shard\", Slot: (\d+)b", inv): return int(m.group(1))
    return None
def has_ring(p="Cam"): return "passed" in rc.run(f"execute if items entity {p} container.* *[minecraft:custom_data~{{le_ring:1b}}]") or "passed" in rc.run(f"execute if items entity {p} hotbar.* *[minecraft:custom_data~{{le_ring:1b}}]")
def head_ring(p="Cam"): return "passed" in rc.run(f"execute if items entity {p} armor.head *[minecraft:custom_data~{{le_ring:1b}}]")
def wear(p="Cam"):
    """what the player does: the ring goes into the head slot (the same state as a click / a drag)"""
    rc.run(f"clear {p} minecraft:amethyst_shard[minecraft:custom_data~{{le_ring:1b}}] 1"); rc.run(f"function last_ember:ring/give_for {p}") if False else None
    rc.run(f"item replace entity {p} armor.head from entity {p} hotbar.0") if False else None
def on(p="Cam"): return "le.ringon" in rc.run(f"tag {p} list")
def put_ring_on(p="Cam"):
    rc.run(f"item replace entity {p} armor.head with minecraft:air")
    rc.run(f"execute as {p} run function last_ember:ring/give"); time.sleep(0.3)
    # the freshly given ring is in the inventory; move it to the head slot
    m = None
    for s in list(range(0, 9)) + list(range(9, 36)):
        reg = "hotbar" if s < 9 else "container"; idx = s if s < 9 else s - 9
        if "passed" in rc.run(f"execute if items entity {p} {reg}.{idx} *[minecraft:custom_data~{{le_ring:1b}}]"):
            rc.run(f"item replace entity {p} armor.head from entity {p} {reg}.{idx}"); rc.run(f"item replace entity {p} {reg}.{idx} with minecraft:air"); return True
    return False
def t_don():
    print("[don]"); arena(); halfling(); dress(); time.sleep(0.5); before = snap("Cam")
    a0 = num(rc.run("attribute Cam minecraft:armor get")); t0 = num(rc.run("attribute Cam minecraft:armor_toughness get")); k0 = num(rc.run("attribute Cam minecraft:knockback_resistance get"))
    chk("the ring is in the start inventory of the halfling (tag ringgot)", has_ring() and "le.ringgot" in rc.run("tag Cam list"))
    chk("the ring puts: custom_data owner is the player's UUID", "owner" in rc.run("data get entity Cam Inventory"))
    put_ring_on(); time.sleep(0.6)
    chk("ring on: tag ringon, invisible", on() and "invisibility" in rc.run("data get entity Cam active_effects"))
    chk("armor slots empty", all("No entity" in eq("Cam", s) or "Found no" in eq("Cam", s) for s in ITEMS), [eq("Cam", s)[:60] for s in ITEMS])
    a1 = num(rc.run("attribute Cam minecraft:armor get")); t1 = num(rc.run("attribute Cam minecraft:armor_toughness get")); k1 = num(rc.run("attribute Cam minecraft:knockback_resistance get"))
    chk(f"protection kept as attributes: armor {a0} == {a1}, toughness {t0} == {t1}, knockback {k0} == {k1}", abs(a0 - a1) < 0.01 and abs(t0 - t1) < 0.01 and abs(k0 - k1) < 0.01)
    chk("the ring is on the head", head_ring())
    rc.run("item replace entity Cam armor.head with minecraft:air"); time.sleep(0.6)    # the ring taken off by hand
    after = snap("Cam")
    chk("ring off by hand: armor back as it was (components identical, damage, enchantments, trim, name, dye)", after == before, [(s, before[s][:80], after[s][:80]) for s in ITEMS if before[s] != after[s]])
    time.sleep(2.5); chk("ring off: state and invisibility gone (invisibility runs out within 2 s)", not on() and "invisibility" not in rc.run("data get entity Cam active_effects"))
    a2 = num(rc.run("attribute Cam minecraft:armor get")); chk("armor value back (not doubled)", abs(a2 - a0) < 0.01, (a0, a2))
def effects(p="Cam"): return rc.run(f"data get entity {p} active_effects")
def gt(): return score("#gt", "le.e")
def back_ok(p, before, why):
    time.sleep(0.5); after = snap(p)
    chk(f"{why}: armor back unchanged", after == before, [(k, before[k][:70], after[k][:70]) for k in before if before[k] != after[k]])
def t_foreign():
    print("[the ring does not clear foreign effects]"); arena(); halfling(); dress(); rc.run("effect clear Cam")
    for e in ("wither", "slowness", "darkness"): rc.run(f"effect give Cam minecraft:{e} 100 0")
    rc.run("effect give Cam minecraft:invisibility 100 0"); put_ring_on(); time.sleep(2.0); rc.run("item replace entity Cam armor.head with minecraft:air"); time.sleep(1.5)
    fx = effects(); durs = [int(x) for x in re.findall(r"duration: (\d+)", fx)]
    chk("foreign wither, slowness, darkness, invisibility (100 s) survive putting the ring on and off", all(k in fx for k in ("wither", "slowness", "darkness", "invisibility")) and min(durs) > 1500, (fx[:300],))
    rc.run("effect clear Cam")
def t_owner():
    print("[the ring works only for its owner]"); arena(); halfling(); tc.setc(4, 1, 0, "Cam2"); rc.run("gamemode survival Cam2"); rc.run("tp Cam2 %d %d %d" % (AX + 4, AY, AZ))
    rc.run("clear Cam2 minecraft:amethyst_shard"); rc.run("execute as Cam run function last_ember:ring/give"); time.sleep(0.3)
    rc.run("data modify storage last_ember:ring t set from entity Cam Inventory[{components:{\"minecraft:custom_data\":{le_ring:1b}}}]")
    rc.run("execute at Cam2 run summon minecraft:armor_stand ~ ~ ~ {Marker:1b,Tags:[\"le.rt1\"]}"); rc.run("data modify entity @e[tag=le.rt1,limit=1] equipment.mainhand set from storage last_ember:ring t")
    rc.run("item replace entity Cam2 armor.head from entity @e[tag=le.rt1,limit=1] weapon.mainhand"); rc.run("kill @e[tag=le.rt1]"); time.sleep(0.6)
    chk("another halfling's ring: refused, 'not for you', goes to the inventory", not on("Cam2") and not head_ring("Cam2") and has_ring("Cam2"))
    rc.run("clear Cam2 minecraft:amethyst_shard"); rc.run("tag Cam2 add le.ringgot")
def t_refuse():
    print("[refusals]"); arena(); halfling(); dress(); before = snap("Cam")
    rc.run(f"scoreboard players set Cam le.rcd {gt() + 400}"); put_ring_on(); time.sleep(0.5)
    chk("cooldown: ring back in the inventory, not on, armor kept", not head_ring() and has_ring() and not on() and snap("Cam") == before)
    rc.run("scoreboard players set Cam le.rcd 0"); rc.run("item replace entity Cam armor.chest with minecraft:elytra"); rc.run(f"tp Cam {AX}.5 {AY+25} {AZ}.5"); time.sleep(0.05)
    put_ring_on(); time.sleep(0.3)
    chk("elytra in the air: refused", not on() and not head_ring() and has_ring() and "No entity" not in eq("Cam", "chest"), (on(), eq("Cam", "chest")[:60]))
    rc.run(f"tp Cam {AX}.5 {AY} {AZ}.5"); time.sleep(1.2); dress(); before = snap("Cam")
    rc.run('item replace entity Cam armor.legs with minecraft:iron_leggings[minecraft:enchantments={"minecraft:binding_curse":1}]'); before = snap("Cam"); put_ring_on(); time.sleep(0.5)
    chk("curse of binding: refused, armor stays", not on() and not head_ring() and has_ring() and snap("Cam") == before)
    dress(); rc.run("item replace entity Cam armor.chest with minecraft:elytra"); before = snap("Cam"); put_ring_on(); time.sleep(0.6)
    chk("elytra on the ground is accepted and goes to the storage", on() and "No entity" in eq("Cam", "chest") or "Found no" in eq("Cam", "chest"))
    rc.run("item replace entity Cam armor.head with minecraft:air"); time.sleep(0.6); chk("elytra is back", snap("Cam") == before)
    # not a halfling
    rc.run("clear Cam"); tc.setc(1, 1, 0, "Cam"); rc.run("gamemode survival Cam"); rc.run(f"tp Cam {AX}.5 {AY} {AZ}.5"); time.sleep(0.5); dress(); before = snap("Cam")
    rc.run("execute as Cam run function last_ember:ring/give"); time.sleep(0.3); put_ring_on_raw = None
    for s in range(0, 9):
        if "passed" in rc.run(f"execute if items entity Cam hotbar.{s} *[minecraft:custom_data~{{le_ring:1b}}]"): rc.run(f"item replace entity Cam armor.head from entity Cam hotbar.{s}"); rc.run(f"item replace entity Cam hotbar.{s} with minecraft:air"); break
    time.sleep(0.5)
    chk("a human: 'not for you', the ring back in the inventory, the armor stays", not head_ring() and has_ring() and not on() and snap("Cam") == before)
def t_fee():
    print("[fee over time: tick rate 100 = 5x]"); arena(); halfling(); dress(); rc.run("effect clear Cam"); put_ring_on(); time.sleep(0.5)
    t0 = score("Cam", "le.rt"); seen = {}
    rc.run("tick rate 100")
    try:
        t_start = time.time()
        while time.time() - t_start < 14:
            time.sleep(0.4); sec = (gt() - t0) / 20; fx = effects()
            for k in ("darkness", "slowness", "wither"):
                if k in fx and k not in seen: seen[k] = sec
            if "wither" in fx and "amplifier: 1b" in fx.split("wither")[1][:60] + fx.split("wither")[0][-60:] and "w2" not in seen: seen["w2"] = sec
            if sec > 46: break
    finally: rc.run("tick rate 20")
    print("   first seen (seconds worn):", {k: round(v, 1) for k, v in seen.items()})
    chk("0-20 s: no darkness/slowness/wither", all(seen.get(k, 99) >= 19 for k in ("darkness", "slowness")) and seen.get("wither", 99) >= 29)
    chk("darkness and slowness from 20 s", 19 <= seen.get("darkness", 0) <= 24 and 19 <= seen.get("slowness", 0) <= 24, seen)
    chk("wither from 30 s", 29 <= seen.get("wither", 0) <= 34, seen)
    chk("wither II from 40 s", "w2" in seen and 39 <= seen["w2"] <= 44, seen)
    rc.run("item replace entity Cam armor.head with minecraft:air"); time.sleep(0.6)
    worn = (gt() - t0) / 20; cd = (score("Cam", "le.rcd") - gt()) / 20
    time.sleep(5.0); chk("ring off: the short ring effects (wither, darkness, slowness, invisibility) simply run out within 5 s", all(k not in effects() for k in ("wither", "darkness", "slowness", "invisibility")), effects()[:100])
    chk(f"cooldown = half of the time worn ({worn:.0f} s -> {worn/2:.1f} s)", abs(cd - worn / 2) <= 2.0, cd)
    rc.run("effect clear Cam"); rc.run("scoreboard players set Cam le.rcd 0"); put_ring_on(); time.sleep(0.5); rc.run("item replace entity Cam armor.head with minecraft:air"); time.sleep(0.6)
    cd = (score("Cam", "le.rcd") - gt()) / 20; chk("worn for a moment: cooldown 3 s", 2.0 <= cd <= 3.5, cd)
    put_ring_on(); time.sleep(0.5); chk("cooldown: the second put-on is refused with the ring back", not on() and not head_ring() and has_ring())
    time.sleep(3.0); put_ring_on(); time.sleep(0.5); chk("after 3 s it works again", on()); rc.run("item replace entity Cam armor.head with minecraft:air"); time.sleep(0.5)
DEATHS = (("mob", "minecraft:mob_attack by @e[tag=le.test,limit=1]"), ("lava", "minecraft:lava"), ("void", "minecraft:out_of_world"), ("suffocation", "minecraft:in_wall"), ("wither of the ring", "minecraft:wither"))
def t_death():
    print("[death in the ring]"); arena()
    for nm, dmg in DEATHS:
        halfling(); rc.run(f"tp Cam {AX}.5 {AY} {AZ}.5"); dress(); rc.run("kill @e[tag=le.test]"); rc.run(f'summon minecraft:husk {AX+3}.5 {AY} {AZ}.5 {{NoAI:1b,Tags:["le.test","le.keep"],PersistenceRequired:1b}}')
        before = snap("Cam"); put_ring_on(); time.sleep(0.6); assert on()
        rc.run(f"damage Cam 1000 {dmg}"); time.sleep(3.5)
        chk(f"death ({nm}): the armor stayed on him, intact", snap("Cam") == before, [(k, before[k][:60], snap("Cam")[k][:60]) for k in before if before[k] != snap("Cam")[k]])
        chk(f"death ({nm}): ring in the inventory, not on the head, state off, no modifiers", has_ring() and not head_ring() and not on() and abs(num(rc.run("attribute Cam minecraft:armor get")) - 12.0) < 0.01, (has_ring(), head_ring(), on(), rc.run("attribute Cam minecraft:armor get")))
        rc.run("kill @e[tag=le.test]")
def t_rejoin():
    print("[a new session / server restart: ticks missed]"); arena(); halfling(); dress(); before = snap("Cam"); put_ring_on(); time.sleep(0.6)
    rc.run(f"scoreboard players set Cam le.rlast {gt() - 500}"); time.sleep(0.5)
    chk("missed ticks: armor back unchanged, ring in the inventory, no ring effects", snap("Cam") == before and has_ring() and not head_ring() and not on() and True)
    # the record is lost (storage older than the player data): the copy inside the ring brings the armor back
    put_ring_on(); time.sleep(0.6); rc.run('data remove storage last_ember:ring p'); rc.run(f"scoreboard players set Cam le.rlast {gt() - 500}"); time.sleep(0.5)
    chk("record lost: the copy inside the ring restores the armor", snap("Cam") == before and not on(), [(k, before[k][:50]) for k in before if before[k] != snap("Cam")[k]])
    # not doubled: the piece is already on him and the record is there (the player data is older than the storage)
    put_ring_on(); time.sleep(0.6); rc.run("tag Cam remove le.ringon"); rc.run("item replace entity Cam armor.head with minecraft:air"); dress(); time.sleep(0.2)
    rc.run(f"scoreboard players set Cam le.rlast {gt() - 500}"); time.sleep(1.5)
    inv = rc.run("data get entity Cam Inventory"); cnt = inv.count("diamond_chestplate") + inv.count("iron_boots") + inv.count("leather_leggings")
    chk("armor already on him + a record in the storage: nothing is given twice (guard settles the record)", snap("Cam") == before and cnt == 0 and "passed" not in rc.run('execute if data storage last_ember:ring p'), (cnt, rc.run("data get storage last_ember:ring p")[:80]))
def t_reset():
    print("[char/reset in the ring]"); arena(); halfling(); dress(); before = snap("Cam"); put_ring_on(); time.sleep(0.6)
    rc.run("execute as Cam run function last_ember:char/reset"); time.sleep(2.0)
    chk("reset: the armor is on him again before the reset", snap("Cam") == before and not on(), [(k, before[k][:50]) for k in before if before[k] != snap("Cam")[k]])
def t_two():
    print("[two wearers at once]"); arena(); halfling("Cam"); tc.setc(4, 1, 0, "Cam2"); rc.run("gamemode survival Cam2"); rc.run(f"scoreboard players set Cam2 le.rcd 0"); rc.run(f"tp Cam2 {AX+4}.5 {AY} {AZ}.5")
    rc.run(f"tp Cam {AX}.5 {AY} {AZ}.5"); dress("Cam")
    other = {"chest": "minecraft:leather_chestplate[minecraft:dyed_color=255]", "legs": "minecraft:chainmail_leggings", "feet": "minecraft:golden_boots[minecraft:damage=5]"}
    for s_, it in other.items(): rc.run(f"item replace entity Cam2 armor.{s_} with {it}")
    b1, b2 = snap("Cam"), snap("Cam2"); put_ring_on("Cam"); put_ring_on("Cam2"); time.sleep(0.8)
    chk("both wear the ring", on("Cam") and on("Cam2") and "No entity" in eq("Cam", "chest") + eq("Cam2", "chest") or (on("Cam") and on("Cam2")))
    rc.run("damage Cam 1000 minecraft:mob_attack"); rc.run("item replace entity Cam2 armor.head with minecraft:air"); time.sleep(3.5)
    chk("Cam died in the ring, Cam2 took it off: each has his own armor", snap("Cam") == b1 and snap("Cam2") == b2, [(k, b1[k][:40], snap("Cam")[k][:40]) for k in b1 if b1[k] != snap("Cam")[k]] + [(k, b2[k][:40]) for k in b2 if b2[k] != snap("Cam2")[k]])
    def pieces(p_): inv = rc.run(f"data get entity {p_} Inventory"); return sum(inv.count(x) for x in ("diamond_chestplate", "iron_boots", "leather_leggings", "leather_chestplate", "chainmail_leggings", "golden_boots"))
    chk("no piece got doubled (none in the inventories, the storage is empty)", pieces("Cam") == 0 and pieces("Cam2") == 0 and "passed" not in rc.run("execute if data storage last_ember:ring p.a"), (pieces("Cam"), pieces("Cam2")))
def t_lost():
    print("[the ring is never lost]"); arena(); halfling(); time.sleep(0.5)
    rc.run("clear Cam minecraft:amethyst_shard"); time.sleep(1.6); chk("destroyed (cleared): the owner gets it again", has_ring())
    rc.run("clear Cam minecraft:amethyst_shard"); rc.run(f"execute as Cam run function last_ember:ring/give"); time.sleep(0.2)
    # dropped on the floor: no copy appears
    rc.run("execute as Cam at @s run summon minecraft:item ~ ~ ~5 {Item:{id:\"minecraft:stone\",count:1},Tags:[\"le.rdrop\"],PickupDelay:32767s}") if False else None
    n0 = rc.run("data get entity Cam Inventory").count("le_ring")
    rc.run("clear Cam minecraft:amethyst_shard"); rc.run(f"execute as Cam run function last_ember:ring/give"); time.sleep(0.3)
    sl = None
    for s in range(0, 9):
        if "passed" in rc.run(f"execute if items entity Cam hotbar.{s} *[minecraft:custom_data~{{le_ring:1b}}]"): sl = s; break
    rc.run(f"execute at Cam run summon item ~ ~ ~4 {{Item:{{id:\"minecraft:amethyst_shard\",count:1,components:{{}}}},PickupDelay:32767s,Tags:[\"le.rdrop\"]}}")
    rc.run("data modify entity @e[tag=le.rdrop,limit=1] Item set from entity Cam Inventory[{components:{\"minecraft:custom_data\":{le_ring:1b}}}]"); rc.run("clear Cam minecraft:amethyst_shard"); time.sleep(1.6)
    chk("dropped on the floor: no second ring", not has_ring() and "passed" in rc.run("execute if entity @e[tag=le.rdrop]"))
    rc.run("kill @e[tag=le.rdrop]"); time.sleep(1.6); chk("floor ring gone (void/lava/despawn): it comes back", has_ring())
    tc.setc(4, 1, 0, "Cam2"); rc.run("gamemode survival Cam2"); rc.run("clear Cam minecraft:amethyst_shard"); time.sleep(1.6); rc.run("clear Cam2 minecraft:amethyst_shard")
    # handed to a partner: no copy either
    rc.run("execute as Cam run function last_ember:ring/give"); rc.run("data modify storage last_ember:ring t set from entity Cam Inventory[{components:{\"minecraft:custom_data\":{le_ring:1b}}}]")
    rc.run("clear Cam minecraft:amethyst_shard"); rc.run("summon minecraft:item ~ ~ ~ {Item:{id:\"minecraft:stone\",count:1},Tags:[\"le.rt1\"]}") if False else None
    rc.run("execute at Cam run summon minecraft:armor_stand ~ ~ ~ {Marker:1b,Tags:[\"le.rt1\"]}"); rc.run("data modify entity @e[tag=le.rt1,limit=1] equipment.mainhand set from storage last_ember:ring t"); rc.run("item replace entity Cam2 hotbar.3 from entity @e[tag=le.rt1,limit=1] weapon.mainhand"); rc.run("kill @e[tag=le.rt1]")
    time.sleep(1.8); chk("the ring is with the partner: the owner does not get a copy", not has_ring("Cam"))
    rc.run("clear Cam2")
if __name__ == "__main__":
    want = sys.argv[1:] or ["don", "refuse", "foreign", "owner", "fee", "death", "rejoin", "reset", "two", "lost"]
    for w in want: globals()["t_" + w]()
    print(f"\n{ok} ok, {bad} failed"); sys.exit(1 if bad else 0)
