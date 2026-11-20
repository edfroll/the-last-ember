# grave 11 (wrong): first opening
scoreboard players set #g11 le.cem 1
execute store result score #dlast le.cem run time query gametime
scoreboard players add #dist le.cem 3
loot spawn 158.5 92.2 502.5 loot last_ember:cemetery/bones
execute positioned 158.5 92 502.5 as @e[type=minecraft:item,distance=..2] run data merge entity @s {Age:-32768s}
playsound minecraft:block.wooden_trapdoor.open block @a[distance=..16] 158 93 502 1 0.6
function last_ember:cemetery/save
function last_ember:cemetery/wave {x:158,y:95,z:502}
