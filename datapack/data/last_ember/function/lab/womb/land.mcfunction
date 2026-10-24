scoreboard players set @s le.lair 0
scoreboard players set @s le.lsq 2
scoreboard players set @s le.lfd 3
function last_ember:lab/womb/shape {s:"squash",d:2}
playsound last_ember:creature.toad.mv_land hostile @a ~ ~ ~ 1.0 1
execute if score #r le.l matches 0 run playsound last_ember:creature.water_hag.slime hostile @a ~ ~ ~ 0.9 1
particle minecraft:block{block_state:"minecraft:mud"} ~ ~0.1 ~ 0.6 0.05 0.6 0 8
