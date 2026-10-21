summon minecraft:marker ~ ~ ~ {Tags:["le.pos"]}
execute store result storage last_ember:dt bowl.x double 0.01 run data get entity @e[type=minecraft:marker,tag=le.pos,limit=1] Pos[0] 100
execute store result storage last_ember:dt bowl.y double 0.01 run data get entity @e[type=minecraft:marker,tag=le.pos,limit=1] Pos[1] 100
execute store result storage last_ember:dt bowl.z double 0.01 run data get entity @e[type=minecraft:marker,tag=le.pos,limit=1] Pos[2] 100
kill @e[type=minecraft:marker,tag=le.pos]
