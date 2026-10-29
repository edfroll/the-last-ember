# MODULE (as a player): Burn (Ожог, T-020) — burns for 3 s: flames and fire damage once a second; fire resistance and water put it out.
# (26.3: the Fire of a player cannot be written by commands, so the burning is our own, without the vanilla flames on the screen)
execute if predicate last_ember:wound/fire_res run return 0
tag @s add le.wound
scoreboard players set @s le.wbu 60
title @s actionbar {"text":"Ожог — в воду!","color":"red"}
playsound minecraft:entity.blaze.shoot player @a ~ ~ ~ 0.8 0.8
