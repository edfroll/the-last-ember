execute in minecraft:overworld run fill 273 96 489 273 96 490 minecraft:soul_soil replace minecraft:air
scoreboard players set #cem_pit_16_st le.tr 0
scoreboard players set #cem_pit_16_t le.tr 0
execute in minecraft:overworld positioned 273 96 489 run playsound minecraft:block.stone.place block @a[distance=..16] ~ ~ ~ 1 0.8
