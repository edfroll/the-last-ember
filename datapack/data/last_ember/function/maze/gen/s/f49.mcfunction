# generated: one second of the look at statue 49: the nearest movable cell (3) rebuilds, cooldowns 20 s here and 5 s for the maze
scoreboard players set @s le.mzg 0
execute if score #gt le.mz < #cd49 le.mz run return 0
execute if score #gt le.mz < #gcd le.mz run return 0
execute unless function last_ember:maze/gen/try_3 run return 0
scoreboard players operation #cd49 le.mz = #gt le.mz
scoreboard players add #cd49 le.mz 400
scoreboard players operation #gcd le.mz = #gt le.mz
scoreboard players add #gcd le.mz 100
scoreboard players add #looks le.mz 1
