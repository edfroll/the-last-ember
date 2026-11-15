# generated: statue 50 at -141 -411 (cell 2,3), exit N, nearest movable cell 4
scoreboard players set #n50 le.mz 1
execute at @s anchored eyes facing -140.5 114.5 -410.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l50
