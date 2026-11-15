# generated: statue 88 at -93 -429 (cell 4,2 v2), exit N, nearest movable cell 4
scoreboard players set #n88 le.mz 1
execute at @s anchored eyes facing -92.5 114.5 -428.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l88
