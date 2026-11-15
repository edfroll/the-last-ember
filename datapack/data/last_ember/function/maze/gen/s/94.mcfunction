# generated: statue 94 at -113 -417 (cell 4,3), exit S, nearest movable cell 4
scoreboard players set #n94 le.mz 1
execute at @s anchored eyes facing -112.5 114.5 -416.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l94
