# generated: statue 1 at -197 -489 (cell 0,0), exit W, nearest movable cell 1
scoreboard players set #n1 le.mz 1
execute at @s anchored eyes facing -196.5 114.5 -488.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l1
