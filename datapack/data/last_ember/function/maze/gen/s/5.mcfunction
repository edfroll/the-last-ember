# generated: statue 5 at -194 -421 (cell 0,2 v2), exit E, nearest movable cell 3
scoreboard players set #n5 le.mz 1
execute at @s anchored eyes facing -193.5 114.5 -420.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l5
