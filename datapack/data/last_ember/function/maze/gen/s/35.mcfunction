# generated: statue 35 at -170 -412 (cell 1,3 v2), exit E, nearest movable cell 5
scoreboard players set #n35 le.mz 1
execute at @s anchored eyes facing -169.5 114.5 -411.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l35
