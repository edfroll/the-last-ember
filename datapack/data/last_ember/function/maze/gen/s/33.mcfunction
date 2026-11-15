# generated: statue 33 at -164 -397 (cell 1,3 v1), exit W, nearest movable cell 4
scoreboard players set #n33 le.mz 1
execute at @s anchored eyes facing -163.5 114.5 -396.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l33
