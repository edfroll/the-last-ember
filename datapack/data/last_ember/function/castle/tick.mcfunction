# T-028: every tick while somebody is waking the colossi or flying: the warning, the strike, the flight
execute as @a[tag=le.cwake] at @s run function last_ember:castle/wake_tick
execute as @a[tag=le.cfly] run function last_ember:castle/fly_tick
execute if entity @a[tag=le.cwake] run schedule function last_ember:castle/tick 1t replace
execute if entity @a[tag=le.cfly] run schedule function last_ember:castle/tick 1t replace
