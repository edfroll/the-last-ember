# generated: statue 60 at -131 -465 (cell 3,1 v2), exit W, nearest movable cell 1
scoreboard players set #n60 le.mz 1
execute at @s anchored eyes facing -130.5 114.5 -464.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l60
