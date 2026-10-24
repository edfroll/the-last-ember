# 4 frames a cycle; a footfall at frames 0 and 2 (the foot touches the ground)
scoreboard players set @s le.lfd 6
execute if score @s le.lsp matches 9.. run scoreboard players set @s le.lfd 5
execute if score @s le.lfd matches 6 run data modify storage last_ember:lab anim.d set value 6
execute if score @s le.lfd matches 5 run data modify storage last_ember:lab anim.d set value 5
execute if score @s le.lfr matches 0 run function last_ember:lab/gen/pose_walk0 with storage last_ember:lab anim
execute if score @s le.lfr matches 1 run function last_ember:lab/gen/pose_walk1 with storage last_ember:lab anim
execute if score @s le.lfr matches 2 run function last_ember:lab/gen/pose_walk2 with storage last_ember:lab anim
execute if score @s le.lfr matches 3 run function last_ember:lab/gen/pose_walk3 with storage last_ember:lab anim
execute if score @s le.lfr matches 0 run playsound last_ember:creature.leshen.footstep_walk_base_custom hostile @a ~ ~ ~ 0.9 1
execute if score @s le.lfr matches 2 run playsound last_ember:creature.leshen.footstep_walk_base_custom hostile @a ~ ~ ~ 0.9 1
scoreboard players add @s le.lfr 1
execute if score @s le.lfr matches 4.. run scoreboard players set @s le.lfr 0
