# generated: cem_pit_15 back to the start
scoreboard players set #cem_pit_15_st le.tr 0
scoreboard players set #cem_pit_15_t le.tr 0
scoreboard players set #cem_pit_15_cd le.tr 0
execute in minecraft:overworld run fill 263 93 464 263 93 465 minecraft:soul_soil replace minecraft:air
execute in minecraft:overworld run kill @e[type=minecraft:falling_block,tag=le.trap_fb]
