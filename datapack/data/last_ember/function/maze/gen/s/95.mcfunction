# generated: statue 95 at -92 -417 (cell 4,3), exit W, nearest movable cell 6
scoreboard players set #n95 le.mz 1
execute at @s anchored eyes facing -91.5 114.5 -416.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l95
