execute in minecraft:overworld run fill 263 93 464 263 93 465 minecraft:soul_soil replace minecraft:air
scoreboard players set #cem_pit_15_st le.tr 0
scoreboard players set #cem_pit_15_t le.tr 0
execute in minecraft:overworld positioned 263 93 464 run playsound minecraft:block.stone.place block @a[distance=..16] ~ ~ ~ 1 0.8
