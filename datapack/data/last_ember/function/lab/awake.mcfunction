# the end of the appearance: the vanilla AI takes over
scoreboard players set @s le.ls 2
scoreboard players set @s le.lt 0
data merge entity @s {NoAI:0b,Invulnerable:0b}
execute store result score @s le.lhp run data get entity @s Health
execute store result score @s le.lx run data get entity @s Pos[0] 100
execute store result score @s le.lz run data get entity @s Pos[2] 100
