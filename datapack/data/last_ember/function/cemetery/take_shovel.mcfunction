# T-027: «Взять лопату»: the quest is taken (once for the whole team), the Keeper's Shovel to the one who pressed
execute unless score #q le.cem matches 0 run return 0
scoreboard players set #q le.cem 1
scoreboard players set #sh le.cem 1
function last_ember:cemetery/gen/give_cem_shovel with storage last_ember:cemetery gen
playsound minecraft:item.shovel.flatten player @s ~ ~ ~ 0.8 0.7
function last_ember:cemetery/save
