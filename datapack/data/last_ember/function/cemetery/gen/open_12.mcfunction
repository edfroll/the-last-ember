# grave 12 (wrong): first opening
scoreboard players set #g12 le.cem 1
execute store result score #dlast le.cem run time query gametime
scoreboard players add #dist le.cem 3
loot spawn 198.5 92.2 488.5 loot last_ember:cemetery/bones
execute positioned 198.5 92 488.5 as @e[type=minecraft:item,distance=..2] run data merge entity @s {Age:-32768s}
playsound minecraft:block.wooden_trapdoor.open block @a[distance=..16] 198 93 488 1 0.6
function last_ember:cemetery/save
function last_ember:cemetery/wave {x:198,y:95,z:488}
