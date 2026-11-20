# grave 4 (right): first opening
scoreboard players set #g4 le.cem 1
execute store result score #dlast le.cem run time query gametime
scoreboard players add #dist le.cem 1
loot spawn 270.5 100.2 514.5 loot last_ember:cemetery/grave_4
execute positioned 270.5 100 514.5 as @e[type=minecraft:item,distance=..2] run data merge entity @s {Age:-32768s}
playsound minecraft:block.wooden_trapdoor.open block @a[distance=..16] 270 101 514 1 0.6
function last_ember:cemetery/save
function last_ember:cemetery/wave {x:270,y:103,z:514}
