# generated: cem_pit_16 fired by a link or by the admin (any context)
execute unless score #cem_pit_16_st le.tr matches 0 run return 0
scoreboard players set #cem_pit_16_st le.tr 1
scoreboard players set #cem_pit_16_t le.tr 0
execute positioned 273 96 489 run function last_ember:trap/shield_near
