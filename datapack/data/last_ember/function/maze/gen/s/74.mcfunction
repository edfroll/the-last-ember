# generated: statue 74 at -117 -411 (cell 3,3 v3), exit N, nearest movable cell 6
scoreboard players set #n74 le.mz 1
execute at @s anchored eyes facing -116.5 114.5 -410.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l74
