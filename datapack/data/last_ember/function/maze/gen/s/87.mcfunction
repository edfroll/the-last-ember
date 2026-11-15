# generated: statue 87 at -104 -431 (cell 4,2 v2), exit E, nearest movable cell 2
scoreboard players set #n87 le.mz 1
execute at @s anchored eyes facing -103.5 114.5 -430.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l87
