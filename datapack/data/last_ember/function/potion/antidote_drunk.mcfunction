advancement revoke @s only last_ember:potion/antidote
effect clear @s minecraft:poison
effect clear @s minecraft:wither
scoreboard players operation @s le.immune = #gt le.e
scoreboard players add @s le.immune 1200
tag @s add le.immune
title @s actionbar {"text":"Противоядие: 60 секунд","color":"green"}
