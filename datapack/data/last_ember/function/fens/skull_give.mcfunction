# T-026: as the killer of the Master: the skull
function last_ember:fens/gen/give_fens_skull with storage last_ember:fens skull
scoreboard players set #sk le.fn 1
scoreboard players set #ms le.fn 2
playsound minecraft:entity.skeleton.death neutral @s ~ ~ ~ 1 0.6
title @s actionbar {"text":"Череп Хозяина Гати","color":"gold"}
function last_ember:fens/save
