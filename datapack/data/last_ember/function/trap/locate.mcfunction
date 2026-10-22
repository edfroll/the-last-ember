# @s at itself: the cell of the index (64-block cells, coordinates offset by 8192) -> the traps whose area reaches it check this player
execute store result score #x le.tr run data get entity @s Pos[0]
execute store result score #zz le.tr run data get entity @s Pos[2]
scoreboard players add #x le.tr 8192
scoreboard players add #zz le.tr 8192
scoreboard players operation #x le.tr /= #64 le.tr
scoreboard players operation #zz le.tr /= #64 le.tr
execute store result storage last_ember:traps a.x int 1 run scoreboard players get #x le.tr
execute store result storage last_ember:traps a.z int 1 run scoreboard players get #zz le.tr
data modify storage last_ember:traps a.d set value "o"
execute if dimension minecraft:the_nether run data modify storage last_ember:traps a.d set value "n"
execute if dimension minecraft:the_end run data modify storage last_ember:traps a.d set value "e"
function last_ember:trap/cell with storage last_ember:traps a
