# every 10 ticks: trails smoulder (only near players), lit urns spark; orphan trail entities (record gone) are cleaned up
execute as @e[type=minecraft:item_display,tag=le.ash_disp] at @s if entity @a[distance=..64] run particle minecraft:smoke ~ ~0.3 ~ 0.08 0.15 0.08 0.01 2
execute as @e[type=minecraft:item_display,tag=le.ash_disp] at @s if entity @a[distance=..64] if predicate last_ember:chance_30 run particle minecraft:small_flame ~ ~0.25 ~ 0.1 0.05 0.1 0.005 1
execute as @e[type=minecraft:text_display,tag=le.urn_lit] at @s if entity @a[distance=..48] run particle minecraft:white_ash ~ ~4 ~ 0.6 0.4 0.6 0.01 6
execute as @e[type=minecraft:text_display,tag=le.urn_lit] at @s if entity @a[distance=..48] run particle minecraft:flame ~ ~4 ~ 0.4 0.2 0.4 0.01 1
execute as @e[type=minecraft:interaction,tag=le.ashclick] run function last_ember:ash/orphan_check
function last_ember:urn/gen/register
schedule function last_ember:ash/slow_loop 10t replace
