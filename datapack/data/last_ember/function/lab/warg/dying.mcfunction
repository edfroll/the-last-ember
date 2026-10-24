# the death: a yelp, it rears and the maw gapes, it falls on its side, lies, sinks into the ground
function last_ember:lab/turn
execute if score @s le.lt matches 1 run playsound last_ember:creature.wild_dog.death hostile @a ~ ~ ~ 1.8 1
execute if score @s le.lt matches 1 run function last_ember:lab/rig_pose {r:"warg",p:"die0",d:5}
execute if score @s le.lt matches 7 run function last_ember:lab/rig_pose {r:"warg",p:"die1",d:8}
execute if score @s le.lt matches 15 run playsound last_ember:creature.wild_dog.bodyfall.grass_long_grass_short_leaves hostile @a ~ ~ ~ 1.2 1
execute if score @s le.lt matches 15 run particle minecraft:block{block_state:"minecraft:redstone_block"} ~ ~0.4 ~ 0.6 0.2 0.6 0 16
execute if score @s le.lt matches 40..79 run tp @s ~ ~-0.02 ~
execute if score @s le.lt matches 40..79 run particle minecraft:block{block_state:"minecraft:coarse_dirt"} ~ ~0.2 ~ 0.8 0.05 0.8 0 2
execute if score @s le.lt matches 80.. run function last_ember:lab/remove
