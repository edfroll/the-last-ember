# generated: statue 4 at -209 -429 (cell 0,2 v2), exit N, nearest movable cell 3
scoreboard players set #n4 le.mz 1
execute at @s anchored eyes facing -208.5 114.5 -428.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l4
