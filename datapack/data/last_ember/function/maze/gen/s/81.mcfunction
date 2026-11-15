# generated: statue 81 at -108 -429 (cell 4,2 v1), exit N, nearest movable cell 4
scoreboard players set #n81 le.mz 1
execute at @s anchored eyes facing -107.5 114.5 -428.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l81
