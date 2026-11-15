# generated: statue 36 at -164 -417 (cell 1,3 v2), exit W, nearest movable cell 5
scoreboard players set #n36 le.mz 1
execute at @s anchored eyes facing -163.5 114.5 -416.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l36
