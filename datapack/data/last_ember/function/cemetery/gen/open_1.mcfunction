# grave 1 (right): first opening
scoreboard players set #g1 le.cem 1
execute store result score #dlast le.cem run time query gametime
scoreboard players add #dist le.cem 1
loot spawn 204.5 90.2 468.5 loot last_ember:cemetery/grave_1
execute positioned 204.5 90 468.5 as @e[type=minecraft:item,distance=..2] run data merge entity @s {Age:-32768s}
playsound minecraft:block.wooden_trapdoor.open block @a[distance=..16] 204 91 468 1 0.6
function last_ember:cemetery/save
function last_ember:cemetery/wave {x:204,y:93,z:468}
