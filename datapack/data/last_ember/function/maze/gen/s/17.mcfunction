# generated: statue 17 at -175 -459 (cell 1,1 v1), exit N, nearest movable cell 5
scoreboard players set #n17 le.mz 1
execute at @s anchored eyes facing -174.5 114.5 -458.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l17
