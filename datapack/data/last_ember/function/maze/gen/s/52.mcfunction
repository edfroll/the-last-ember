# generated: statue 52 at -161 -373 (cell 2,4), exit E, nearest movable cell 3
scoreboard players set #n52 le.mz 1
execute at @s anchored eyes facing -160.5 114.5 -372.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l52
