# T-033: every 5 ticks: (players near) the cave-ins (an active sensor with a player within 10 -> the warning, 2 s, the fall), the resting
# dead miners and Bran wake (a player not in spectator/creative within 6); every second the rest (mines/second)
schedule function last_ember:mines/loop 5t replace
scoreboard players add #t le.mn 1
execute if score #t le.mn matches 4.. in minecraft:overworld run function last_ember:mines/second
execute if score #near le.mn matches 0 run return 0
execute in minecraft:overworld run function last_ember:mines/gen/caves
execute in minecraft:overworld as @e[type=minecraft:zombie,tag=le.mnr] at @s if entity @e[type=minecraft:player,gamemode=!spectator,gamemode=!creative,distance=..6] run function last_ember:mines/wake
