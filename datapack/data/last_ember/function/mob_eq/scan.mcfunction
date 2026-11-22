# T-001b: every 10 ticks, newly seen geared mobs get metal-gear drop chances zeroed (no metal source from mobs).
execute as @e[type=#last_ember:geared,tag=!le.eq_done] run function last_ember:mob_eq/fix
# T-014: new mobs that can become elites get their one roll here too
execute as @e[type=#last_ember:elite_types,tag=!le.rolled,limit=40] at @s run function last_ember:elite/roll
execute as @e[type=#last_ember:cube_mobs,tag=le.elite] run function last_ember:elite/check_cube
schedule function last_ember:mob_eq/scan 10t replace
# T-029: at most 20 monsters in castle_halls (new ones beyond are removed)
execute in minecraft:overworld run function last_ember:castle/kg/cap
