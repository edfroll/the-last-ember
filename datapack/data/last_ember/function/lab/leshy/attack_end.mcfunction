function last_ember:lab/leshy/pose {p:"idle0",d:8}
attribute @s minecraft:movement_speed modifier remove last_ember:lab_hold
scoreboard players set @s le.lan 0
scoreboard players set @s le.lfd 8
scoreboard players set @s le.lfr 1
scoreboard players set @s le.lcd 40
# the next blow with the other arm
scoreboard players add @s le.lair 1
execute if score @s le.lair matches 2.. run scoreboard players set @s le.lair 0
