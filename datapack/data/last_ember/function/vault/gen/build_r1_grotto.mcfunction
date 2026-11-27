# the container of the treasury r1_grotto with its loot table (the loot is made when a player opens it)
execute in minecraft:overworld run setblock -373 136 213 minecraft:chest[facing=south]{LootTable:"last_ember:vault/r1_grotto"} replace
scoreboard players set #b.r1_grotto le.vt 1
