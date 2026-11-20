# grave 6 (thane): first opening
scoreboard players set #g6 le.cem 1
execute store result score #dlast le.cem run time query gametime
scoreboard players add #dist le.cem 1
execute positioned 248.5 95 464.5 as @e[type=minecraft:item,distance=..2] run data merge entity @s {Age:-32768s}
playsound minecraft:block.wooden_trapdoor.open block @a[distance=..16] 248 96 464 1 0.6
function last_ember:cemetery/save
function last_ember:cemetery/wave {x:248,y:98,z:464}
