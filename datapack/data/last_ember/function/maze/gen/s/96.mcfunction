# generated: statue 96 at -113 -372 (cell 4,4), exit N, nearest movable cell 4
scoreboard players set #n96 le.mz 1
execute at @s anchored eyes facing -112.5 114.5 -371.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l96
