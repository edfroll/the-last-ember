# as a visible sample: it falls on its side (the sleeping pose of a living entity without a bed: sleeping_pos one block lower)
data modify storage last_ember:lab p set value [I;0,0,0]
execute store result storage last_ember:lab p[0] int 1 run data get entity @s Pos[0]
execute store result storage last_ember:lab p[1] int 1 run data get entity @s Pos[1]
execute store result storage last_ember:lab p[2] int 1 run data get entity @s Pos[2]
execute store result score #y le.l run data get storage last_ember:lab p[1]
execute store result storage last_ember:lab p[1] int 1 run scoreboard players remove #y le.l 1
data modify entity @s sleeping_pos set from storage last_ember:lab p
