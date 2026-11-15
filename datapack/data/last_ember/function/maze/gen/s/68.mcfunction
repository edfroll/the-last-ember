# generated: statue 68 at -117 -420 (cell 3,2), exit N, nearest movable cell 4
scoreboard players set #n68 le.mz 1
execute at @s anchored eyes facing -116.5 114.5 -419.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l68
