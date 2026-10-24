# the swing (the right arm and the left one in turn, le.lair): wind-up (the arm goes up and back, a roar) 10 ticks -> the blow 3 ticks -> the hit is checked -> back to rest
scoreboard players remove @s le.lfd 1
execute if score @s le.lfd matches 1.. run return 0
execute if score @s le.lfr matches 0 if score @s le.lair matches 0 run function last_ember:lab/leshy/pose {p:"windup",d:8}
execute if score @s le.lfr matches 0 if score @s le.lair matches 1 run function last_ember:lab/leshy/pose {p:"windup_l",d:8}
execute if score @s le.lfr matches 0 run playsound last_ember:creature.leshen.vo_attack_short hostile @a ~ ~ ~ 1.8 1
execute if score @s le.lfr matches 0 run playsound last_ember:creature.leshen.mv_wood_stress hostile @a ~ ~ ~ 1.0 1
execute if score @s le.lfr matches 0 run scoreboard players set @s le.lfd 10
execute if score @s le.lfr matches 1 if score @s le.lair matches 0 run function last_ember:lab/leshy/pose {p:"strike",d:3}
execute if score @s le.lfr matches 1 if score @s le.lair matches 1 run function last_ember:lab/leshy/pose {p:"strike_l",d:3}
execute if score @s le.lfr matches 1 run playsound last_ember:creature.leshen.attack_whoosh_medium hostile @a ~ ~2 ~ 1.4 1
execute if score @s le.lfr matches 1 run scoreboard players set @s le.lfd 2
execute if score @s le.lfr matches 2 run function last_ember:lab/leshy/strike
execute if score @s le.lfr matches 2 run scoreboard players set @s le.lfd 10
execute if score @s le.lfr matches 3 run function last_ember:lab/leshy/attack_end
scoreboard players add @s le.lfr 1
