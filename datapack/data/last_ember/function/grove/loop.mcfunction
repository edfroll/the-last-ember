# T-030: every 5 ticks: the buttons of the Advisor's windows; every second the rest (grove/second)
schedule function last_ember:grove/loop 5t replace
execute as @a[scores={le.atrig=1..}] at @s run function last_ember:grove/trig
scoreboard players add #t le.grv 1
execute if score #t le.grv matches 4.. in minecraft:overworld run function last_ember:grove/second
