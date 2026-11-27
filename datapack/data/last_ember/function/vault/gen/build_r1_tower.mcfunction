# the container of the treasury r1_tower with its loot table (the loot is made when a player opens it)
execute in minecraft:overworld run setblock 477 190 43 minecraft:chest[facing=north]{LootTable:"last_ember:vault/r1_tower"} replace
scoreboard players set #b.r1_tower le.vt 1
