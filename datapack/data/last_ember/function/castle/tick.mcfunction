# T-028: every tick while somebody is waking the colossi or flying: the warning, the strike, the flight (the next tick appended once;
# castle/loop re-schedules it with replace, so it never runs twice a tick)
execute as @a[tag=le.cwake] at @s run function last_ember:castle/wake_tick
execute as @a[tag=le.cfly] run function last_ember:castle/fly_tick
scoreboard players set #act le.cas 0
execute if entity @a[tag=le.cwake] run scoreboard players set #act le.cas 1
execute if entity @a[tag=le.cfly] run scoreboard players set #act le.cas 1
execute if score #act le.cas matches 1 run schedule function last_ember:castle/tick 1t append
