# as the carrier, while dying: lt 2 the body rolls over on its side (one segment after another), lt 6-30 the legs kick, lt 35-74 it sinks
scoreboard players operation #id le.l = @s le.lnk
execute if score @s le.lt matches 2 as @e[type=minecraft:item_display,tag=le.cseg] if score @s le.lnk = #id le.l run function last_ember:lab/cent/roll
execute if score @s le.lt matches 2 on passengers run data merge entity @s {start_interpolation:0,interpolation_duration:6,transformation:{left_rotation:[0f,0f,0.5736f,0.8192f]}}
scoreboard players operation #t3 le.l = #gt le.l
scoreboard players operation #t3 le.l %= #3 le.l
execute if score @s le.lt matches 6..30 if score #t3 le.l matches 0 run function last_ember:lab/cent/step
execute if score @s le.lt matches 35..74 as @e[tag=le.cseg] if score @s le.lnk = #id le.l at @s run tp @s ~ ~-0.025 ~
execute if score @s le.lt matches 35..74 as @e[tag=le.cseg] if score @s le.lnk = #id le.l at @s run particle minecraft:block{block_state:"minecraft:coarse_dirt"} ~ ~0.2 ~ 0.5 0.05 0.5 0 1
