# at the chosen free block (centre), as the dead player
execute store result score #id le.e run data get storage last_ember:ash next
execute store result storage last_ember:ash next int 1 run scoreboard players add #id le.e 1
scoreboard players remove #id le.e 1
execute store result storage last_ember:dt rec.id int 1 run scoreboard players get #id le.e
summon minecraft:marker ~ ~ ~ {Tags:["le.pos"]}
execute store result storage last_ember:dt rec.x int 1 run data get entity @e[type=minecraft:marker,tag=le.pos,limit=1] Pos[0]
execute store result storage last_ember:dt rec.y int 1 run data get entity @e[type=minecraft:marker,tag=le.pos,limit=1] Pos[1]
execute store result storage last_ember:dt rec.z int 1 run data get entity @e[type=minecraft:marker,tag=le.pos,limit=1] Pos[2]
kill @e[type=minecraft:marker,tag=le.pos]
summon minecraft:interaction ~ ~ ~ {width:0.9f,height:0.7f,response:1b,Tags:["le.ash","le.ashclick","le.ashnew"]}
summon minecraft:item_display ~ ~0.3 ~ {Tags:["le.ash","le.ash_disp","le.ashnew"],brightness:{sky:15,block:15},billboard:"vertical",item:{id:"minecraft:trial_key",count:1,components:{"minecraft:item_model":"last_ember:ash_pile"}},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.9f,0.9f,0.9f]}}
execute as @e[tag=le.ashnew,distance=..2] run scoreboard players operation @s le.tid = #id le.e
tag @e[tag=le.ashnew,distance=..2] remove le.ashnew
execute if block ~ ~ ~ minecraft:air run setblock ~ ~ ~ minecraft:light[level=10]
function last_ember:ash/store with storage last_ember:dt rec
scoreboard players operation @s le.ash = #id le.e
scoreboard players set #done le.e 1
particle minecraft:large_smoke ~ ~0.3 ~ 0.2 0.2 0.2 0.01 15
