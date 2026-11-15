# generated: statue 47 at -155 -445 (cell 2,1), exit W, nearest movable cell 1
scoreboard players set #n47 le.mz 1
execute at @s anchored eyes facing -154.5 114.5 -444.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l47
