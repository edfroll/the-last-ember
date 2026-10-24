execute facing entity @p[gamemode=!spectator,gamemode=!creative] feet positioned 0.0 0.0 0.0 rotated ~ 0 positioned ^ ^ ^-0.18 run summon minecraft:marker ~ ~ ~ {Tags:["le.lvec"]}
execute store result score #mx le.l run data get entity @e[type=minecraft:marker,tag=le.lvec,limit=1] Pos[0] 1000
execute store result score #mz le.l run data get entity @e[type=minecraft:marker,tag=le.lvec,limit=1] Pos[2] 1000
execute store result entity @s Motion[0] double 0.001 run scoreboard players get #mx le.l
execute store result entity @s Motion[2] double 0.001 run scoreboard players get #mz le.l
kill @e[type=minecraft:marker,tag=le.lvec]
