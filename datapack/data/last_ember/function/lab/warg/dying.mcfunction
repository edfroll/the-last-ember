# the death: a yelp, it falls on its side, it sinks into the ground
execute if score @s le.lt matches 1 run playsound last_ember:creature.wild_dog.death hostile @a ~ ~ ~ 1.8 1
execute if score @s le.lt matches 8 run function last_ember:lab/lie
execute if score @s le.lt matches 8 run playsound last_ember:creature.wild_dog.bodyfall.grass_long_grass_short_leaves hostile @a ~ ~ ~ 1.2 1
execute if score @s le.lt matches 8 run particle minecraft:block{block_state:"minecraft:redstone_block"} ~ ~0.4 ~ 0.5 0.2 0.5 0 20
execute if score @s le.lt matches 40..79 run tp @s ~ ~-0.02 ~
execute if score @s le.lt matches 40..79 run particle minecraft:block{block_state:"minecraft:coarse_dirt"} ~ ~0.2 ~ 0.6 0.05 0.6 0 2
execute if score @s le.lt matches 80.. run function last_ember:lab/remove
