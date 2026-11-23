# T-031: every 5 ticks: the buttons of the ringer's windows; the dead villagers wake (a player not in spectator/creative within 5);
# every second the rest (heather/second)
schedule function last_ember:heather/loop 5t replace
execute as @a[scores={le.htrig=1..}] at @s run function last_ember:heather/trig
execute if score #near le.hv matches 1.. as @e[type=minecraft:zombie_villager,tag=le.hzr,tag=!le.hfrz] at @s if entity @a[gamemode=!spectator,gamemode=!creative,distance=..5] run function last_ember:heather/wake
scoreboard players add #t le.hv 1
execute if score #t le.hv matches 4.. in minecraft:overworld run function last_ember:heather/second
