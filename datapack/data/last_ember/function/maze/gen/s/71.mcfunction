# generated: statue 71 at -125 -412 (cell 3,3 v2), exit W, nearest movable cell 6
scoreboard players set #n71 le.mz 1
execute at @s anchored eyes facing -124.5 114.5 -411.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l71
