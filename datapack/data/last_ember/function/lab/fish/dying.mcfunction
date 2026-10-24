# the death: a long screech, it rolls over on its side, it sinks into the ground
execute if score @s le.lt matches 1 run function last_ember:lab/s/fish_death
execute if score @s le.lt matches 10 run function last_ember:lab/lie
execute if score @s le.lt matches 10 run function last_ember:lab/s/fish_fall
execute if score @s le.lt matches 10 run particle minecraft:block{block_state:"minecraft:coarse_dirt"} ~ ~0.3 ~ 0.8 0.1 0.8 0 20
execute if score @s le.lt matches 35..74 run tp @s ~ ~-0.025 ~
execute if score @s le.lt matches 35..74 run particle minecraft:block{block_state:"minecraft:coarse_dirt"} ~ ~0.2 ~ 0.7 0.05 0.7 0 2
execute if score @s le.lt matches 75.. run function last_ember:lab/remove
