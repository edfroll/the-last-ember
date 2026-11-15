# generated: statue 43 at -165 -393 (cell 1,4), exit S, nearest movable cell 3
scoreboard players set #n43 le.mz 1
execute at @s anchored eyes facing -164.5 114.5 -392.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l43
