scoreboard players remove @s le.lfr 1
scoreboard players operation #id le.l = @s le.lnk
execute if score @s le.lfr matches 33 run function last_ember:lab/gen/cent_rear_up
execute if score @s le.lfr matches 33 run function last_ember:lab/cent/rear_body_up
execute if score @s le.lfr matches 33 run function last_ember:lab/s/fish_taunt
execute if score @s le.lfr matches 33 run particle minecraft:block{block_state:"minecraft:coarse_dirt"} ~ ~0.3 ~ 0.8 0.2 0.8 0.1 20
execute if score @s le.lfr matches 22 run function last_ember:lab/s/fish_idle2
execute if score @s le.lfr matches 12 run function last_ember:lab/cent/rear_slam
execute if score @s le.lfr matches 4 run function last_ember:lab/gen/cent_rear_back
execute if score @s le.lfr matches 4 as @e[type=minecraft:marker,tag=le.cmark] if score @s le.lnk = #id le.l run function last_ember:lab/cent/replace
execute if score @s le.lfr matches ..0 run attribute @s minecraft:movement_speed modifier remove last_ember:lab_hold
