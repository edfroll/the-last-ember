# generated: as a player in the area of cem_pit_16 (collapse)
execute if entity @s[tag=le.race.halfling] run return 0
execute unless score #cem_pit_16_st le.tr matches 0 run return 0
scoreboard players set #cem_pit_16_st le.tr 1
scoreboard players set #cem_pit_16_t le.tr 0
function last_ember:trap/shield
