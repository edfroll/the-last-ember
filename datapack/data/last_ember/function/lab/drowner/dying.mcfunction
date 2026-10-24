# the death: a cry, it falls on its side, lies, sinks into the ground in a puddle of rot
execute if score @s le.lt matches 1 run playsound last_ember:creature.drowner.vo_death hostile @a ~ ~ ~ 1.8 1
execute if score @s le.lt matches 12 run function last_ember:lab/lie
execute if score @s le.lt matches 12 run playsound last_ember:creature.drowner.mv_bodyfall hostile @a ~ ~ ~ 1.2 1
execute if score @s le.lt matches 12 run particle minecraft:item{item:"minecraft:rotten_flesh"} ~ ~0.3 ~ 0.5 0.1 0.5 0.08 14
execute if score @s le.lt matches 30..69 run tp @s ~ ~-0.025 ~
execute if score @s le.lt matches 30..69 run particle minecraft:block{block_state:"minecraft:mud"} ~ ~0.2 ~ 0.6 0.05 0.6 0 2
execute if score @s le.lt matches 40 run playsound last_ember:creature.drowner.mv_flesh hostile @a ~ ~ ~ 1.0 0.8
execute if score @s le.lt matches 70.. run function last_ember:lab/remove
