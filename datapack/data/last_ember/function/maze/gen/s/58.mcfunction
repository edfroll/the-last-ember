# generated: statue 58 at -122 -445 (cell 3,1 v1), exit E, nearest movable cell 6
scoreboard players set #n58 le.mz 1
execute at @s anchored eyes facing -121.5 114.5 -444.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l58
