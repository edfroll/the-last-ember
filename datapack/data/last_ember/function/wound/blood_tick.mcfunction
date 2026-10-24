scoreboard players remove @s le.wbl 1
execute if predicate last_ember:sneaking run scoreboard players add @s le.wbs 1
execute unless predicate last_ember:sneaking run scoreboard players set @s le.wbs 0
execute if score @s le.wbs matches 60.. run return run function last_ember:wound/blood_stop
scoreboard players operation #b le.l = @s le.wbl
scoreboard players operation #b le.l %= #60 le.l
execute if score #b le.l matches 0 run damage @s 1 minecraft:magic
scoreboard players operation #b le.l = @s le.wbl
scoreboard players operation #b le.l %= #10 le.l
execute if score #b le.l matches 0 run particle minecraft:block{block_state:"minecraft:redstone_block"} ~ ~0.6 ~ 0.15 0.2 0.15 0 3
