# generated: statue 76 at -128 -388 (cell 3,4), exit E, nearest movable cell 4
scoreboard players set #n76 le.mz 1
execute at @s anchored eyes facing -127.5 114.5 -387.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l76
