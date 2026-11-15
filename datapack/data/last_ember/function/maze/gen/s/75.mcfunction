# generated: statue 75 at -117 -402 (cell 3,3 v3), exit S, nearest movable cell 6
scoreboard players set #n75 le.mz 1
execute at @s anchored eyes facing -116.5 114.5 -401.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l75
