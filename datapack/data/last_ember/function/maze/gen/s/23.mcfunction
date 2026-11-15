# generated: statue 23 at -170 -465 (cell 1,1 v2), exit E, nearest movable cell 2
scoreboard players set #n23 le.mz 1
execute at @s anchored eyes facing -169.5 114.5 -464.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l23
