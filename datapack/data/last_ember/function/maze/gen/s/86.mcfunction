# generated: statue 86 at -109 -421 (cell 4,2 v2), exit E, nearest movable cell 4
scoreboard players set #n86 le.mz 1
execute at @s anchored eyes facing -108.5 114.5 -420.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l86
