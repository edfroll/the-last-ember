# @s at itself: the cell of the index (64-block cells, coordinates offset by 8192) -> the contracts whose clues, bait, circle or twins reach it
execute store result score #x le.ct run data get entity @s Pos[0]
execute store result score #zz le.ct run data get entity @s Pos[2]
scoreboard players add #x le.ct 8192
scoreboard players add #zz le.ct 8192
scoreboard players operation #x le.ct /= #64 le.ct
scoreboard players operation #zz le.ct /= #64 le.ct
execute store result storage last_ember:contracts a.x int 1 run scoreboard players get #x le.ct
execute store result storage last_ember:contracts a.z int 1 run scoreboard players get #zz le.ct
data modify storage last_ember:contracts a.d set value "o"
execute if dimension minecraft:the_nether run data modify storage last_ember:contracts a.d set value "n"
execute if dimension minecraft:the_end run data modify storage last_ember:contracts a.d set value "e"
function last_ember:contract/cell with storage last_ember:contracts a
