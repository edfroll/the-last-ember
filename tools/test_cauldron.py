exec(open('tools/_test_death_helpers.py').read())
act=ns['act']; face=ns['face']; ok=ns['ok']; res=ns['res']
R("gamemode survival Cam"); R("gamemode survival Cam2"); R("clear Cam"); R("clear Cam2"); R("tag Cam remove le.class.healer")
R("execute as Cam run function last_ember:bonfire/give_cauldron"); R("item replace entity Cam weapon.mainhand from entity Cam hotbar.0")
hearth=(200,110,200)
R("setblock 200 111 200 minecraft:air"); R("kill @e[tag=le.pot]"); R("tp Cam 196 110 204")
# 1) a non-healer sneaking click on the hearth = normal click (rest), no cauldron
face("Cam2", 200.5, 110, 202.2, 200.5, 110.4, 200.5); act("Cam2","sneak_on"); act("Cam2","use"); act("Cam2","sneak_off")
ok("non-healer Shift+RMB on the hearth: no cauldron placed (normal rest)", "passed" in R("execute if block 200 111 200 minecraft:air") and "has 1" in R("scoreboard players get Cam2 le.sb"))
# 2) the healer without sneaking: normal click
R("tp Cam2 196 110 196"); face("Cam", 200.5, 110, 202.2, 200.5, 110.4, 200.5); act("Cam","use")
ok("healer RMB without Shift: no cauldron", "passed" in R("execute if block 200 111 200 minecraft:air"))
# 3) healer Shift+RMB with the cauldron: placed over the fire, item gone
act("Cam","sneak_on"); act("Cam","use"); act("Cam","sneak_off")
ok("healer Shift+RMB: cauldron over the fire, item taken from hand", "passed" in R("execute if block 200 111 200 minecraft:cauldron") and "le_cauldron" not in R("data get entity Cam Inventory"))
# 4) another player cannot take it
R("tp Cam 196 110 204"); face("Cam2", 200.5, 110, 202.2, 200.5, 111.5, 200.5); act("Cam2","sneak_on"); act("Cam2","use"); act("Cam2","sneak_off")
ok("non-healer cannot take the cauldron", "passed" in R("execute if block 200 111 200 minecraft:cauldron"))
# 5) the healer takes it back with Shift+RMB
R("tp Cam2 196 110 196"); face("Cam", 200.5, 110, 202.2, 200.5, 111.5, 200.5); act("Cam","sneak_on"); act("Cam","use"); act("Cam","sneak_off")
ok("healer Shift+RMB on the cauldron: taken back into the inventory", "passed" in R("execute if block 200 111 200 minecraft:air") and "le_cauldron" in R("data get entity Cam Inventory"))
print(f"\n{sum(res)}/{len(res)} passed")
