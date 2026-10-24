# the dash lasts 12 ticks, then the speed is back
scoreboard players remove @s le.llook 1
execute if score @s le.llook matches ..0 run attribute @s minecraft:movement_speed modifier remove last_ember:lab_dash
