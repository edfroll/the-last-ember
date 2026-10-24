# from the water: a growl and bubbles 1.5 s before, then it slowly rises out of the pool
execute if score @s le.lt matches 1 run playsound last_ember:creature.drowner.dialog_growl hostile @a ~ ~2 ~ 1.8 1
execute if score @s le.lt matches ..30 run particle minecraft:bubble_pop ~ ~2.25 ~ 0.5 0.05 0.5 0 4
execute if score @s le.lt matches ..30 run particle minecraft:bubble_column_up ~ ~1 ~ 0.3 0.6 0.3 0 3
execute if score @s le.lt matches 31 run playsound last_ember:creature.drowner.uw_dive_short hostile @a ~ ~2 ~ 1.8 1
execute if score @s le.lt matches 31..70 run tp @s ~ ~0.055 ~
execute if score @s le.lt matches 31..70 run particle minecraft:splash ~ ~2.2 ~ 0.4 0.1 0.4 0 6
execute if score @s le.lt matches 70 run playsound last_ember:creature.drowner.dialog_taunt hostile @a ~ ~ ~ 1.8 1
execute if score @s le.lt matches 70 run function last_ember:lab/awake
