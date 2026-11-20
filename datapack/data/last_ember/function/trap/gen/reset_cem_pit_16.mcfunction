# generated: cem_pit_16 back to the start
scoreboard players set #cem_pit_16_st le.tr 0
scoreboard players set #cem_pit_16_t le.tr 0
scoreboard players set #cem_pit_16_cd le.tr 0
execute in minecraft:overworld run fill 273 96 489 273 96 490 minecraft:soul_soil replace minecraft:air
execute in minecraft:overworld run kill @e[type=minecraft:falling_block,tag=le.trap_fb]
