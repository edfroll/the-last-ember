# generated: statue 19 at -164 -460 (cell 1,1 v1), exit W, nearest movable cell 2
scoreboard players set #n19 le.mz 1
execute at @s anchored eyes facing -163.5 114.5 -459.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l19
