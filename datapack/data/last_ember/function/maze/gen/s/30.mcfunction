# generated: statue 30 at -185 -411 (cell 1,3 v1), exit N, nearest movable cell 5
scoreboard players set #n30 le.mz 1
execute at @s anchored eyes facing -184.5 114.5 -410.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l30
