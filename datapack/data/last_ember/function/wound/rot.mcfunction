# MODULE (as a player): Rotten wound — poison I for 6 s; another hit adds 6 s (at most 20 s); the antidote of the healer or milk takes it off
tag @s add le.wound
execute unless predicate last_ember:lab/poisoned run scoreboard players set @s le.wrot 0
scoreboard players add @s le.wrot 120
execute if score @s le.wrot matches 401.. run scoreboard players set @s le.wrot 400
execute store result storage last_ember:lab w.s int 0.05 run scoreboard players get @s le.wrot
function last_ember:wound/rot_give with storage last_ember:lab w
title @s actionbar {"text":"Гнилая рана — нужно противоядие или молоко","color":"dark_green"}
