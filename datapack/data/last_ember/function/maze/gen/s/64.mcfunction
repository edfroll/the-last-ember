# generated: statue 64 at -133 -460 (cell 3,1 v3), exit E, nearest movable cell 1
scoreboard players set #n64 le.mz 1
execute at @s anchored eyes facing -132.5 114.5 -459.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l64
