# T-001b: every 10 ticks, newly seen geared mobs get metal-gear drop chances zeroed (no metal source from mobs).
execute as @e[type=#last_ember:geared,tag=!le.eq_done] run function last_ember:mob_eq/fix
schedule function last_ember:mob_eq/scan 10t replace
