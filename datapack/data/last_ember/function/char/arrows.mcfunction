# every tick: fresh arrows of players get their class/people tuning (mobs' and dispensers' arrows are not touched)
execute as @e[type=minecraft:arrow,tag=!le.ar] run function last_ember:char/arrow_new
execute as @e[type=minecraft:spectral_arrow,tag=!le.ar] run function last_ember:char/arrow_new
