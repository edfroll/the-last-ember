# generated: statue 22 at -181 -465 (cell 1,1 v2), exit E, nearest movable cell 5
scoreboard players set #n22 le.mz 1
execute at @s anchored eyes facing -180.5 114.5 -464.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l22
