scoreboard players set @s le.lfd 18
execute if score @s le.lfr matches 0 run function last_ember:lab/rig_pose {r:"warg",p:"idle0",d:18}
execute if score @s le.lfr matches 1 run function last_ember:lab/rig_pose {r:"warg",p:"idle1",d:18}
scoreboard players add @s le.lfr 1
execute if score @s le.lfr matches 2.. run scoreboard players set @s le.lfr 0
