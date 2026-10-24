# a gallop of 4 frames; faster when it runs faster; a footfall at frames 0 and 2
scoreboard players set @s le.lfd 3
execute if score @s le.lsp matches 14.. run scoreboard players set @s le.lfd 2
execute store result storage last_ember:lab anim.d int 1 run scoreboard players get @s le.lfd
execute if score @s le.lfr matches 0 run function last_ember:lab/gen/warg_pose_run0 with storage last_ember:lab anim
execute if score @s le.lfr matches 1 run function last_ember:lab/gen/warg_pose_run1 with storage last_ember:lab anim
execute if score @s le.lfr matches 2 run function last_ember:lab/gen/warg_pose_run2 with storage last_ember:lab anim
execute if score @s le.lfr matches 3 run function last_ember:lab/gen/warg_pose_run3 with storage last_ember:lab anim
execute if score @s le.lfr matches 0 run playsound last_ember:creature.wild_dog.footsteps.grass_long_grass_short_leaves hostile @a ~ ~ ~ 0.8 1
execute if score @s le.lfr matches 2 run playsound last_ember:creature.wild_dog.footsteps.grass_long_grass_short_leaves hostile @a ~ ~ ~ 0.7 0.9
scoreboard players add @s le.lfr 1
execute if score @s le.lfr matches 4.. run scoreboard players set @s le.lfr 0
