# grave 14 (wrong): first opening
scoreboard players set #g14 le.cem 1
execute store result score #dlast le.cem run time query gametime
scoreboard players add #dist le.cem 3
loot spawn 190.5 102.2 508.5 loot last_ember:cemetery/bones
execute positioned 190.5 102 508.5 as @e[type=minecraft:item,distance=..2] run data merge entity @s {Age:-32768s}
playsound minecraft:block.wooden_trapdoor.open block @a[distance=..16] 190 103 508 1 0.6
function last_ember:cemetery/save
function last_ember:cemetery/wave {x:190,y:105,z:508}
