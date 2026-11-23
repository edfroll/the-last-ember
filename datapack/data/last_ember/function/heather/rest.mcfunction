# T-031: as an awake dead villager, nobody within 32: back on his point, full health, resting again (like the statues of T-016)
function last_ember:heather/gen/home
data modify entity @s NoAI set value 1b
data modify entity @s Health set value 20.0f
data modify entity @s Fire set value 0s
scoreboard players set @s le.hoff 0
tag @s remove le.hza
tag @s add le.hzr
