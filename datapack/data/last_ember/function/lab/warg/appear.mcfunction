function last_ember:lab/warg/turn
execute if score @s le.lt matches 1 run playsound last_ember:creature.wild_dog.howl hostile @a ~ ~ ~ 2.2 1
execute if score @s le.lt matches 1..40 run particle minecraft:block{block_state:"minecraft:oak_leaves"} ~ ~0.6 ~ 0.8 0.3 0.8 0 1
execute if score @s le.lt matches 30 run playsound last_ember:creature.wild_dog.growl_aggro hostile @a ~ ~ ~ 1.8 1
execute if score @s le.lt matches 45 run function last_ember:lab/warg/leap
