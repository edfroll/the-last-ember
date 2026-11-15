# generated: statue 56 at -121 -472 (cell 3,0), exit N, nearest movable cell 2
scoreboard players set #n56 le.mz 1
execute at @s anchored eyes facing -120.5 114.5 -471.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l56
