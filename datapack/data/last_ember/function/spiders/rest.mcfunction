# T-032: as an awake elite spider, nobody within 40: back on her point, full health, resting again (like the villagers of T-031)
function last_ember:spiders/gen/home
data modify entity @s NoAI set value 1b
execute store result entity @s Health float 1 run attribute @s minecraft:max_health get
data modify entity @s Fire set value 0s
tag @s remove le.spawk
tag @s add le.sprest
