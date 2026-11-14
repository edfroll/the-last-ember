# T-022: back to the point where the chorus fruit was eaten
execute store result storage last_ember:gates ch.x double 0.1 run scoreboard players get @s le.chx
execute store result storage last_ember:gates ch.y double 0.1 run scoreboard players get @s le.chy
execute store result storage last_ember:gates ch.z double 0.1 run scoreboard players get @s le.chz
function last_ember:gate/chorus_tp with storage last_ember:gates ch
execute at @s run playsound minecraft:item.chorus_fruit.teleport player @a ~ ~ ~ 1 0.6
execute at @s run particle minecraft:reverse_portal ~ ~1 ~ 0.3 0.6 0.3 0.05 30
tag @s remove le.chorus
