# generated: statue 14 at -164 -489 (cell 1,0), exit W, nearest movable cell 1
scoreboard players set #n14 le.mz 1
execute at @s anchored eyes facing -163.5 114.5 -488.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l14
