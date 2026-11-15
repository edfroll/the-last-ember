# generated: statue 57 at -125 -455 (cell 3,1 v1), exit W, nearest movable cell 6
scoreboard players set #n57 le.mz 1
execute at @s anchored eyes facing -124.5 114.5 -454.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l57
