scoreboard players remove @s le.wbu 1
execute if block ~ ~ ~ minecraft:water run return run function last_ember:wound/burn_stop
execute if block ~ ~1 ~ minecraft:water run return run function last_ember:wound/burn_stop
execute if predicate last_ember:wound/fire_res run return run function last_ember:wound/burn_stop
particle minecraft:flame ~ ~0.9 ~ 0.3 0.5 0.3 0.01 2
scoreboard players operation #b le.l = @s le.wbu
scoreboard players operation #b le.l %= #20 le.l
execute if score #b le.l matches 0 run damage @s 1 minecraft:on_fire
