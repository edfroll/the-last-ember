# at the mob: #full = 1 when there are too many elites: 8 in the world, 2 within 48 blocks of any player who is within 48 blocks of this mob
scoreboard players set #full le.el 0
execute store result score #wc le.el if entity @e[tag=le.elite]
execute if score #wc le.el >= #elimit_w le.el run scoreboard players set #full le.el 1
execute as @a[distance=..48] at @s run function last_ember:elite/limit_player
