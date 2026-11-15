# generated: statue 53 at -145 -393 (cell 2,4), exit S, nearest movable cell 4
scoreboard players set #n53 le.mz 1
execute at @s anchored eyes facing -144.5 114.5 -392.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l53
