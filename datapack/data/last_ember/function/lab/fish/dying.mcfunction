# the death: a long screech; the scolopendra rolls over on its side segment by segment, its legs kick, then it sinks into the ground
execute if score @s le.lt matches 1 run function last_ember:lab/s/fish_death
execute if entity @s[tag=le.cent] run function last_ember:lab/cent/die_body
execute if score @s le.lt matches 10 run function last_ember:lab/s/fish_fall
execute if score @s le.lt matches 10 run particle minecraft:block{block_state:"minecraft:coarse_dirt"} ~ ~0.3 ~ 0.8 0.1 0.8 0 20
execute if score @s le.lt matches 35..74 run tp @s ~ ~-0.025 ~
execute if score @s le.lt matches 75.. if entity @s[tag=le.cent] run function last_ember:lab/cent/kill_body
execute if score @s le.lt matches 75.. run function last_ember:lab/remove
