# generated: statue 2 at -188 -445 (cell 0,1), exit W, nearest movable cell 1
scoreboard players set #n2 le.mz 1
execute at @s anchored eyes facing -187.5 114.5 -444.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l2
