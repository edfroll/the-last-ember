# generated: one second of the look at statue 53: the nearest movable cell (4) rebuilds, cooldowns 20 s here and 5 s for the maze
scoreboard players set @s le.mzg 0
execute if score #gt le.mz < #cd53 le.mz run return 0
execute if score #gt le.mz < #gcd le.mz run return 0
execute unless function last_ember:maze/gen/try_4 run return 0
scoreboard players operation #cd53 le.mz = #gt le.mz
scoreboard players add #cd53 le.mz 400
scoreboard players operation #gcd le.mz = #gt le.mz
scoreboard players add #gcd le.mz 100
scoreboard players add #looks le.mz 1
