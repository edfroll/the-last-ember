# under the ground: it sinks 1.5 blocks, then moves 0.5 block every 2 ticks toward the nearest player, 1.5 below his feet; a trail of earth and a rumble on the surface; near him (or after 6 s) it emerges
scoreboard players add @s le.lt 1
execute if entity @s[tag=le.cent] run function last_ember:lab/cent/tick
execute if score @s le.lt matches ..12 run tp @s ~ ~-0.125 ~
execute if score @s le.lt matches ..12 run particle minecraft:block{block_state:"minecraft:coarse_dirt"} ~ ~0.3 ~ 0.6 0.1 0.6 0 6
execute if score @s le.lt matches ..12 run return 0
execute unless entity @a[distance=..40,gamemode=!spectator,gamemode=!creative] run return run function last_ember:lab/fish/emerge
scoreboard players operation #t2 le.l = @s le.lt
scoreboard players operation #t2 le.l %= #2 le.l
execute if score #t2 le.l matches 0 facing entity @p[gamemode=!spectator,gamemode=!creative] feet rotated ~ 0 run tp @s ^ ^ ^0.5 ~ 0
execute store result score #ty le.l run data get entity @p[gamemode=!spectator,gamemode=!creative] Pos[1] 100
execute store result entity @s Pos[1] double 0.01 run scoreboard players remove #ty le.l 150
particle minecraft:block{block_state:"minecraft:coarse_dirt"} ~ ~1.6 ~ 0.4 0.05 0.4 0 3
scoreboard players operation #t8 le.l = @s le.lt
scoreboard players operation #t8 le.l %= #8 le.l
execute if score #t8 le.l matches 0 run function last_ember:lab/s/fish_rumble
execute if entity @a[distance=..2.5,gamemode=!spectator,gamemode=!creative] run return run function last_ember:lab/fish/emerge
execute if score @s le.lt matches 120.. run function last_ember:lab/fish/emerge
