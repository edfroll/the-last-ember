# generated: statue 79 at -109 -455 (cell 4,1), exit E, nearest movable cell 2
scoreboard players set #n79 le.mz 1
execute at @s anchored eyes facing -108.5 114.5 -454.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l79
