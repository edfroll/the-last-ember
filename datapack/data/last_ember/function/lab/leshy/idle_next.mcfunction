scoreboard players set @s le.lfd 16
execute if score @s le.lfr matches 0 run function last_ember:lab/leshy/pose {p:"idle0",d:16}
execute if score @s le.lfr matches 1 run function last_ember:lab/leshy/pose {p:"idle1",d:16}
scoreboard players add @s le.lfr 1
execute if score @s le.lfr matches 2.. run scoreboard players set @s le.lfr 0
