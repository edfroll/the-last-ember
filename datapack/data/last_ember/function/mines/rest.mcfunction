# T-033: as an awake dead miner or Bran, nobody within 32: back on his point, full health, resting again (like the villagers of T-031)
execute if entity @s[tag=le.mn_dead] run function last_ember:mines/gen/home
execute if entity @s[tag=le.mn_bran] run function last_ember:mines/gen/bran_home
data modify entity @s NoAI set value 1b
execute store result entity @s Health float 1 run attribute @s minecraft:max_health get
data modify entity @s Fire set value 0s
tag @s remove le.mna
tag @s add le.mnr
execute if entity @s[tag=le.mn_bran] run scoreboard players set #bran le.mn 0
execute if entity @s[tag=le.mn_bran] run data modify storage last_ember:mines bran set value 0
execute if entity @s[tag=le.mn_bran] run data modify entity @s CustomNameVisible set value 0b
