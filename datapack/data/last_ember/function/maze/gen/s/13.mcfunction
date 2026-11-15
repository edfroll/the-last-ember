# generated: statue 13 at -188 -393 (cell 0,4), exit W, nearest movable cell 3
scoreboard players set #n13 le.mz 1
execute at @s anchored eyes facing -187.5 114.5 -392.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l13
