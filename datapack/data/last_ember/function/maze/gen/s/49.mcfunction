# generated: statue 49 at -161 -417 (cell 2,3), exit S, nearest movable cell 3
scoreboard players set #n49 le.mz 1
execute at @s anchored eyes facing -160.5 114.5 -416.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l49
