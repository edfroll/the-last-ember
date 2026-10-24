# a heave forward along the ground (3 of 4) or a hop (1 of 4)
execute store result score @s le.lfd run random value 14..26
execute store result score #hop le.l run random value 0..3
execute if score #hop le.l matches 0 run return run function last_ember:lab/womb/push {f:0.4,y:0.5}
# in the bog it heaves itself up over the edge
execute if block ~ ~0.3 ~ minecraft:water run return run function last_ember:lab/womb/push {f:0.55,y:0.48}
function last_ember:lab/womb/push {f:0.8,y:0.06}
function last_ember:lab/s/womb_surge
scoreboard players set @s le.lsq 5
scoreboard players set @s le.llook 5
function last_ember:lab/womb/shape {s:"surge",d:2}
particle minecraft:block{block_state:"minecraft:mud"} ~ ~0.1 ~ 0.7 0.05 0.7 0 10
