# generated: statue 28 at -180 -429 (cell 1,2), exit N, nearest movable cell 5
scoreboard players set #n28 le.mz 1
execute at @s anchored eyes facing -179.5 114.5 -428.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l28
