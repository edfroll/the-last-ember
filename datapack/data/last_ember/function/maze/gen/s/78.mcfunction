# generated: statue 78 at -98 -469 (cell 4,0), exit E, nearest movable cell 2
scoreboard players set #n78 le.mz 1
execute at @s anchored eyes facing -97.5 114.5 -468.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l78
