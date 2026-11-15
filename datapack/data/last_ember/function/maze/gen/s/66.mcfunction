# generated: statue 66 at -116 -465 (cell 3,1 v3), exit W, nearest movable cell 6
scoreboard players set #n66 le.mz 1
execute at @s anchored eyes facing -115.5 114.5 -464.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l66
