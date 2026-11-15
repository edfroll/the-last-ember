# generated: statue 11 at -200 -412 (cell 0,3), exit E, nearest movable cell 5
scoreboard players set #n11 le.mz 1
execute at @s anchored eyes facing -199.5 114.5 -411.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l11
