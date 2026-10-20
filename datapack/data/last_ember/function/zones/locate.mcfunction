# @s -> storage last_ember:zt a {d: o|n|e, x: cellX, z: cellZ} (64-block cells, coordinates offset by 8192 to stay positive)
execute store result score #x le.z run data get entity @s Pos[0]
execute store result score #zz le.z run data get entity @s Pos[2]
scoreboard players add #x le.z 8192
scoreboard players add #zz le.z 8192
scoreboard players operation #x le.z /= #64 le.z
scoreboard players operation #zz le.z /= #64 le.z
execute store result storage last_ember:zt a.x int 1 run scoreboard players get #x le.z
execute store result storage last_ember:zt a.z int 1 run scoreboard players get #zz le.z
data modify storage last_ember:zt a.d set value "o"
execute if dimension minecraft:the_nether run data modify storage last_ember:zt a.d set value "n"
execute if dimension minecraft:the_end run data modify storage last_ember:zt a.d set value "e"
