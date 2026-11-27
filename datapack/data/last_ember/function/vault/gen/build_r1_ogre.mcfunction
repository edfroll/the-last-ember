# the container of the treasury r1_ogre with its loot table (the loot is made when a player opens it)
execute in minecraft:overworld run setblock 222 170 149 minecraft:chest[facing=east]{LootTable:"last_ember:vault/r1_ogre"} replace
scoreboard players set #b.r1_ogre le.vt 1
