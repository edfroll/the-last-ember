# generated: statue 29 at -165 -420 (cell 1,2), exit N, nearest movable cell 3
scoreboard players set #n29 le.mz 1
execute at @s anchored eyes facing -164.5 114.5 -419.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l29
