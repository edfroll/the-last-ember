# T-024: as a player in the maze (every 5 ticks): the cell (#cx #cz 0..4), its dead-end statues (near: the head follows later; looked at
# for 1 s: the nearest movable cell rebuilds)
execute store result score #cx le.mz run data get entity @s Pos[0]
execute store result score #cz le.mz run data get entity @s Pos[2]
scoreboard players add #cx le.mz 450
scoreboard players add #cz le.mz 730
scoreboard players operation #cx le.mz /= #24 le.mz
scoreboard players operation #cz le.mz /= #24 le.mz
scoreboard players remove #cx le.mz 10
scoreboard players remove #cz le.mz 10
tag @s remove le.mzlook
function last_ember:maze/gen/pc
execute unless entity @s[tag=le.mzlook] run scoreboard players set @s le.mzg 0
