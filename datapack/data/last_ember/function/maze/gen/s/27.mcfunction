# generated: statue 27 at -164 -445 (cell 1,1 v3), exit W, nearest movable cell 5
scoreboard players set #n27 le.mz 1
execute at @s anchored eyes facing -163.5 114.5 -444.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l27
