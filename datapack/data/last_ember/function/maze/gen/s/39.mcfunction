# generated: statue 39 at -185 -417 (cell 1,3 v3), exit S, nearest movable cell 5
scoreboard players set #n39 le.mz 1
execute at @s anchored eyes facing -184.5 114.5 -416.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l39
