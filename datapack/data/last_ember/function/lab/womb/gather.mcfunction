scoreboard players remove @s le.lfr 1
execute if score @s le.lfr matches 1.. run return run particle minecraft:item_slime ~ ~0.3 ~ 0.6 0.1 0.6 0 2
scoreboard players set @s le.lan 0
scoreboard players set @s le.lcd 40
function last_ember:lab/womb/push {f:0.7,y:0.52}
