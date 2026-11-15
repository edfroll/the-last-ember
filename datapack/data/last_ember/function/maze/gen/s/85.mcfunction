# generated: statue 85 at -113 -420 (cell 4,2 v2), exit N, nearest movable cell 4
scoreboard players set #n85 le.mz 1
execute at @s anchored eyes facing -112.5 114.5 -419.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l85
