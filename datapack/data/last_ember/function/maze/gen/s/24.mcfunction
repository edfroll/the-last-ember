# generated: statue 24 at -165 -444 (cell 1,1 v2), exit N, nearest movable cell 5
scoreboard players set #n24 le.mz 1
execute at @s anchored eyes facing -164.5 114.5 -443.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l24
