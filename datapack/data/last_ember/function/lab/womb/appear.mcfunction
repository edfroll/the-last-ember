# from the bog: a gurgle and bubbles first, then the blob rises out of the water and jumps
execute if score @s le.lt matches 1 run function last_ember:lab/s/womb_gurgle
execute if score @s le.lt matches ..30 run particle minecraft:bubble_pop ~ ~0.5 ~ 0.7 0.05 0.7 0 5
execute if score @s le.lt matches ..30 run particle minecraft:bubble_column_up ~ ~-1 ~ 0.5 0.5 0.5 0 3
execute if score @s le.lt matches 30 run function last_ember:lab/s/womb_emerge
execute if score @s le.lt matches 30 on passengers run data merge entity @s {start_interpolation:0,interpolation_duration:12,transformation:{translation:[0.0f,-2.017f,0.0f],scale:[1.81f,2.77f,1.81f]}}
execute if score @s le.lt matches 30..42 run particle minecraft:splash ~ ~0.6 ~ 0.8 0.2 0.8 0 10
execute if score @s le.lt matches 42 run data modify entity @s Motion set value [0.0d,0.62d,0.0d]
execute if score @s le.lt matches 42 run function last_ember:lab/s/womb_jump
execute if score @s le.lt matches 42 run function last_ember:lab/awake
