# generated: statue 42 at -165 -396 (cell 1,3 v3), exit N, nearest movable cell 4
scoreboard players set #n42 le.mz 1
execute at @s anchored eyes facing -164.5 114.5 -395.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l42
