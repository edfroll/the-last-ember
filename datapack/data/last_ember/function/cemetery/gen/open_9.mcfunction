# grave 9 (wrong): first opening
scoreboard players set #g9 le.cem 1
execute store result score #dlast le.cem run time query gametime
scoreboard players add #dist le.cem 3
loot spawn 257.5 90.2 471.5 loot last_ember:cemetery/bones
execute positioned 257.5 90 471.5 as @e[type=minecraft:item,distance=..2] run data merge entity @s {Age:-32768s}
playsound minecraft:block.wooden_trapdoor.open block @a[distance=..16] 257 91 471 1 0.6
function last_ember:cemetery/save
function last_ember:cemetery/wave {x:257,y:93,z:471}
