# grave 7 (wrong): first opening
scoreboard players set #g7 le.cem 1
execute store result score #dlast le.cem run time query gametime
scoreboard players add #dist le.cem 3
loot spawn 214.5 90.2 470.5 loot last_ember:cemetery/bones
execute positioned 214.5 90 470.5 as @e[type=minecraft:item,distance=..2] run data merge entity @s {Age:-32768s}
playsound minecraft:block.wooden_trapdoor.open block @a[distance=..16] 214 91 470 1 0.6
function last_ember:cemetery/save
function last_ember:cemetery/wave {x:214,y:93,z:470}
