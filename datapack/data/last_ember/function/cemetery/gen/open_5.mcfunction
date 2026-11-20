# grave 5 (right): first opening
scoreboard players set #g5 le.cem 1
execute store result score #dlast le.cem run time query gametime
scoreboard players add #dist le.cem 1
loot spawn 226.5 101.2 467.5 loot last_ember:cemetery/grave_5
execute positioned 226.5 101 467.5 as @e[type=minecraft:item,distance=..2] run data merge entity @s {Age:-32768s}
playsound minecraft:block.wooden_trapdoor.open block @a[distance=..16] 226 102 467 1 0.6
function last_ember:cemetery/save
function last_ember:cemetery/wave {x:226,y:104,z:467}
