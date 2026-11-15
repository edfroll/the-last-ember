# generated: statue 45 at -146 -489 (cell 2,0), exit E, nearest movable cell 2
scoreboard players set #n45 le.mz 1
execute at @s anchored eyes facing -145.5 114.5 -488.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l45
