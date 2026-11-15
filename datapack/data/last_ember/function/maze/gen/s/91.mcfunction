# generated: statue 91 at -107 -436 (cell 4,2 v3), exit W, nearest movable cell 2
scoreboard players set #n91 le.mz 1
execute at @s anchored eyes facing -106.5 114.5 -435.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l91
