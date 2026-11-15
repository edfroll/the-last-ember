# generated: statue 63 at -117 -450 (cell 3,1 v2), exit S, nearest movable cell 6
scoreboard players set #n63 le.mz 1
execute at @s anchored eyes facing -116.5 114.5 -449.5 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.35] run function last_ember:maze/gen/s/l63
