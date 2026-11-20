# grave 2 (right): first opening
scoreboard players set #g2 le.cem 1
execute store result score #dlast le.cem run time query gametime
scoreboard players add #dist le.cem 1
loot spawn 268.5 92.2 478.5 loot last_ember:cemetery/grave_2
execute positioned 268.5 92 478.5 as @e[type=minecraft:item,distance=..2] run data merge entity @s {Age:-32768s}
playsound minecraft:block.wooden_trapdoor.open block @a[distance=..16] 268 93 478 1 0.6
function last_ember:cemetery/save
function last_ember:cemetery/wave {x:268,y:95,z:478}
