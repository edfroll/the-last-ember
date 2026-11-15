# generated: statue 83 at -98 -421 (cell 4,2 v1), exit E, nearest movable cell 4
scoreboard players set #n83 le.mz 1
execute at @s anchored eyes facing -97.5 114.5 -420.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l83
