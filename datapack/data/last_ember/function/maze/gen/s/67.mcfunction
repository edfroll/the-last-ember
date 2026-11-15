# generated: statue 67 at -132 -435 (cell 3,2), exit N, nearest movable cell 2
scoreboard players set #n67 le.mz 1
execute at @s anchored eyes facing -131.5 114.5 -434.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l67
