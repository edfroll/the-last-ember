# every 2 seconds: a rare particle round the elites that have a player within 24 blocks
execute as @e[tag=le.elite] at @s if entity @a[distance=..24] run particle minecraft:soul_fire_flame ~ ~0.9 ~ 0.3 0.5 0.3 0.01 3
schedule function last_ember:elite/loop 40t replace
