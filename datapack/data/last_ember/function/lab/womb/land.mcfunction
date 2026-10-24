scoreboard players set @s le.lair 0
scoreboard players set @s le.lsq 2
scoreboard players set @s le.llook 3
function last_ember:lab/womb/shape {s:"squash",d:2}
function last_ember:lab/s/womb_land
execute if score #r le.l matches 0 run function last_ember:lab/s/womb_land2
particle minecraft:block{block_state:"minecraft:mud"} ~ ~0.1 ~ 0.6 0.05 0.6 0 8
