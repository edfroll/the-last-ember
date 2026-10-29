# full health again (the real health + 500)
execute store result entity @s Health float 1 run attribute @s minecraft:max_health get
execute store result score @s le.chp run attribute @s minecraft:max_health get 10
effect clear @s
