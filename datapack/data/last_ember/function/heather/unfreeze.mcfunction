tag @s remove le.hfrz
execute if entity @s[tag=le.hza] run data modify entity @s NoAI set value 0b
execute if entity @s[tag=le.hfv] run data modify entity @s NoAI set value 0b
tag @s remove le.hfv
execute if entity @s[tag=le.hzr] run function last_ember:heather/gen/home
execute if entity @s[tag=le.hzr] run scoreboard players set @s le.hoff 0
