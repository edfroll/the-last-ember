# every 2 ticks while some frosted enemy lives: TicksFrozen is held at 100 (the frost view, under the damage threshold of 140), 10 s later it is let go
execute as @e[type=#last_ember:monsters,tag=le.frost] run function last_ember:seer/frost_tick
execute if entity @e[type=#last_ember:monsters,tag=le.frost,limit=1] run schedule function last_ember:seer/frost_loop 2t replace
