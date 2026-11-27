# T-033: as a resting dead miner or Bran: he wakes (a player within 6, a hit): an ordinary hostile zombie
data modify entity @s NoAI set value 0b
tag @s remove le.mnr
tag @s add le.mna
execute if entity @s[tag=le.mn_bran] run scoreboard players set #bran le.mn 1
execute if entity @s[tag=le.mn_bran] run data modify storage last_ember:mines bran set value 1
execute if entity @s[tag=le.mn_bran] run data modify entity @s CustomNameVisible set value 1b
