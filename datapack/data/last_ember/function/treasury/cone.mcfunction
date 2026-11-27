# T-034: as a player: 1 when the player is within 50 degrees of the Ogre's facing (his blow covers 100 degrees in front)
execute at @e[type=minecraft:zombie,tag=le.tr_ogre,limit=1] run summon minecraft:marker ~ ~ ~ {Tags:["le.tr_aim"]}
execute at @e[type=minecraft:zombie,tag=le.tr_ogre,limit=1] facing entity @s feet run tp @e[type=minecraft:marker,tag=le.tr_aim,limit=1] ~ ~ ~ ~ 0
execute store result score #a le.tr run data get entity @e[type=minecraft:marker,tag=le.tr_aim,limit=1] Rotation[0]
execute store result score #b le.tr run data get entity @e[type=minecraft:zombie,tag=le.tr_ogre,limit=1] Rotation[0]
kill @e[type=minecraft:marker,tag=le.tr_aim]
scoreboard players operation #a le.tr -= #b le.tr
execute if score #a le.tr matches 181.. run scoreboard players remove #a le.tr 360
execute if score #a le.tr matches ..-181 run scoreboard players add #a le.tr 360
execute if score #a le.tr matches -50..50 run return 1
return 0
