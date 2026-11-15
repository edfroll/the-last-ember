# generated: statue 8 at -197 -425 (cell 0,2 v3), exit W, nearest movable cell 3
scoreboard players set #n8 le.mz 1
execute at @s anchored eyes facing -196.5 114.5 -424.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l8
