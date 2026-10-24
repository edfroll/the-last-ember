# from the bog: a gurgle and bubbles first, then the blob rises out of the water and jumps
execute if score @s le.lt matches 1 run playsound last_ember:creature.water_hag.vo_gurgle_long hostile @a ~ ~ ~ 1.8 1
execute if score @s le.lt matches ..30 run particle minecraft:bubble_pop ~ ~0.5 ~ 0.7 0.05 0.7 0 5
execute if score @s le.lt matches ..30 run particle minecraft:bubble_column_up ~ ~-1 ~ 0.5 0.5 0.5 0 3
execute if score @s le.lt matches 30 run playsound last_ember:creature.water_hag.emerge hostile @a ~ ~ ~ 1.8 1
execute if score @s le.lt matches 30 on passengers run data merge entity @s {start_interpolation:0,interpolation_duration:12,transformation:{translation:[0.0f,-1.513f,0.0f],scale:[1.36f,2.08f,1.36f]}}
execute if score @s le.lt matches 30..42 run particle minecraft:splash ~ ~0.6 ~ 0.8 0.2 0.8 0 10
execute if score @s le.lt matches 42 run data modify entity @s Motion set value [0.0d,0.5d,0.0d]
execute if score @s le.lt matches 42 run playsound last_ember:creature.toad.mv_jump hostile @a ~ ~ ~ 1.0 1
execute if score @s le.lt matches 42 run function last_ember:lab/awake
