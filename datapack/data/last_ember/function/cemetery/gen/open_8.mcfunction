# grave 8 (wrong): first opening
scoreboard players set #g8 le.cem 1
execute store result score #dlast le.cem run time query gametime
scoreboard players add #dist le.cem 3
loot spawn 235.5 102.2 468.5 loot last_ember:cemetery/bones
execute positioned 235.5 102 468.5 as @e[type=minecraft:item,distance=..2] run data merge entity @s {Age:-32768s}
playsound minecraft:block.wooden_trapdoor.open block @a[distance=..16] 235 103 468 1 0.6
function last_ember:cemetery/save
function last_ember:cemetery/wave {x:235,y:105,z:468}
