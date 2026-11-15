# generated: one second of the look at statue 27: the nearest movable cell (5) rebuilds, cooldowns 20 s here and 5 s for the maze
scoreboard players set @s le.mzg 0
execute if score #gt le.mz < #cd27 le.mz run return 0
execute if score #gt le.mz < #gcd le.mz run return 0
execute unless function last_ember:maze/gen/try_5 run return 0
scoreboard players operation #cd27 le.mz = #gt le.mz
scoreboard players add #cd27 le.mz 400
scoreboard players operation #gcd le.mz = #gt le.mz
scoreboard players add #gcd le.mz 100
scoreboard players add #looks le.mz 1
