# generated: statue 80 at -93 -444 (cell 4,1), exit N, nearest movable cell 6
scoreboard players set #n80 le.mz 1
execute at @s anchored eyes facing -92.5 114.5 -443.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l80
