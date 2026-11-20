# grave 10 (wrong): first opening
scoreboard players set #g10 le.cem 1
execute store result score #dlast le.cem run time query gametime
scoreboard players add #dist le.cem 3
loot spawn 182.5 93.2 496.5 loot last_ember:cemetery/bones
execute positioned 182.5 93 496.5 as @e[type=minecraft:item,distance=..2] run data merge entity @s {Age:-32768s}
playsound minecraft:block.wooden_trapdoor.open block @a[distance=..16] 182 94 496 1 0.6
function last_ember:cemetery/save
function last_ember:cemetery/wave {x:182,y:96,z:496}
