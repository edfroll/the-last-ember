# T-025: one creaking behind the player (see wake), retried until a place fits (16 tries per creaking)
scoreboard players add #wt le.gd 1
execute if score #wt le.gd matches 17.. run return 0
summon minecraft:marker ~ ~ ~ {Tags:["le.gcand"]}
execute store result score #yaw le.gd run data get entity @s Rotation[0]
execute store result score #r le.gd run random value 125..235
scoreboard players operation #yaw le.gd += #r le.gd
execute store result entity @e[type=minecraft:marker,tag=le.gcand,limit=1] Rotation[0] float 1 run scoreboard players get #yaw le.gd
execute store result storage last_ember:garden tmp.d int 1 run random value 7..13
execute as @e[type=minecraft:marker,tag=le.gcand,limit=1] at @s run function last_ember:garden/wake_go with storage last_ember:garden tmp
scoreboard players set #gok le.gd 0
scoreboard players set #gs le.gd 0
execute as @e[type=minecraft:marker,tag=le.gcand,limit=1] at @s positioned ~ ~6 ~ run function last_ember:garden/ground
execute if score #gok le.gd matches 1 as @e[type=minecraft:marker,tag=le.gcand,limit=1] at @s unless entity @e[type=minecraft:marker,tag=le.gsn,distance=10..16] run scoreboard players set #gok le.gd 0
execute if score #gok le.gd matches 1 as @e[type=minecraft:marker,tag=le.gcand,limit=1] at @s run function last_ember:garden/spawn
kill @e[type=minecraft:marker,tag=le.gcand]
execute if score #gok le.gd matches 0 run function last_ember:garden/wake_try
