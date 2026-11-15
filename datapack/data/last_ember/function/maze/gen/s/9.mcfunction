# generated: statue 9 at -194 -441 (cell 0,2 v3), exit E, nearest movable cell 1
scoreboard players set #n9 le.mz 1
execute at @s anchored eyes facing -193.5 114.5 -440.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l9
