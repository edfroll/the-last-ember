# generated: statue 15 at -165 -474 (cell 1,0), exit S, nearest movable cell 1
scoreboard players set #n15 le.mz 1
execute at @s anchored eyes facing -164.5 114.5 -473.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l15
