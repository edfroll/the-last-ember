scoreboard players remove @s le.lfd 1
execute if score @s le.lfd matches 1.. run return 0
execute if score @s le.lfr matches 0 run function last_ember:lab/rig_pose {r:"warg",p:"bite0",d:3}
execute if score @s le.lfr matches 0 run scoreboard players set @s le.lfd 4
execute if score @s le.lfr matches 1 run function last_ember:lab/rig_pose {r:"warg",p:"bite1",d:2}
execute if score @s le.lfr matches 1 run playsound last_ember:creature.wild_dog.bite hostile @a ~ ~1 ~ 1.2 1
execute if score @s le.lfr matches 1 run scoreboard players set @s le.lfd 6
execute if score @s le.lfr matches 2 run function last_ember:lab/warg/mode {m:0,p:"idle0",d:5}
execute if score @s le.lfr matches 2 run return run scoreboard players set @s le.lcd 22
scoreboard players add @s le.lfr 1
