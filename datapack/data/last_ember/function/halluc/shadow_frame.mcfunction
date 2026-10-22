# as a player, every 4 ticks while the shadow is there
scoreboard players remove @s le.hst 1
scoreboard players operation #me le.h = @s le.hid
tag @s add le.hme
execute as @e[type=minecraft:marker,tag=le.hmark] if score @s le.hid = #me le.h at @s run function last_ember:halluc/shadow_draw
tag @s remove le.hme
execute if score @s le.hst matches ..0 run function last_ember:halluc/shadow_end
