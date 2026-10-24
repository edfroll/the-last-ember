scoreboard players remove @s le.wrt 1
scoreboard players operation #b le.l = @s le.wrt
scoreboard players operation #b le.l %= #2 le.l
execute if score #b le.l matches 0 run particle minecraft:block{block_state:"minecraft:mangrove_roots"} ~ ~0.15 ~ 0.3 0.05 0.3 0 3
execute if score #b le.l matches 0 run particle minecraft:block{block_state:"minecraft:rooted_dirt"} ~ ~0.1 ~ 0.35 0.02 0.35 0 2
