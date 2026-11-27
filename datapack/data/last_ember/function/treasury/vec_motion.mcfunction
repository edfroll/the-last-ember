# T-034: as a projectile: its Motion = the marker le.tr_vec minus its position (the marker goes)
execute store result score #a le.tr run data get entity @s Pos[0] 1000
execute store result score #b le.tr run data get entity @e[type=minecraft:marker,tag=le.tr_vec,limit=1] Pos[0] 1000
scoreboard players operation #b le.tr -= #a le.tr
execute store result entity @s Motion[0] double 0.001 run scoreboard players get #b le.tr
execute store result score #a le.tr run data get entity @s Pos[1] 1000
execute store result score #b le.tr run data get entity @e[type=minecraft:marker,tag=le.tr_vec,limit=1] Pos[1] 1000
scoreboard players operation #b le.tr -= #a le.tr
execute store result entity @s Motion[1] double 0.001 run scoreboard players get #b le.tr
execute store result score #a le.tr run data get entity @s Pos[2] 1000
execute store result score #b le.tr run data get entity @e[type=minecraft:marker,tag=le.tr_vec,limit=1] Pos[2] 1000
scoreboard players operation #b le.tr -= #a le.tr
execute store result entity @s Motion[2] double 0.001 run scoreboard players get #b le.tr
kill @e[type=minecraft:marker,tag=le.tr_vec]
