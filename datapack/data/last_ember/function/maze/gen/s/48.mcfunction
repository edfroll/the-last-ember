# generated: statue 48 at -141 -459 (cell 2,1), exit N, nearest movable cell 2
scoreboard players set #n48 le.mz 1
execute at @s anchored eyes facing -140.5 114.5 -458.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l48
