# grave 3 (right): first opening
scoreboard players set #g3 le.cem 1
execute store result score #dlast le.cem run time query gametime
scoreboard players add #dist le.cem 1
loot spawn 172.5 97.2 510.5 loot last_ember:cemetery/grave_3
execute positioned 172.5 97 510.5 as @e[type=minecraft:item,distance=..2] run data merge entity @s {Age:-32768s}
playsound minecraft:block.wooden_trapdoor.open block @a[distance=..16] 172 98 510 1 0.6
function last_ember:cemetery/save
function last_ember:cemetery/wave {x:172,y:100,z:510}
