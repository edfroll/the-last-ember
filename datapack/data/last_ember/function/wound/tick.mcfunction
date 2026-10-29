# as a wounded player (tag le.wound), every tick
execute if score @s le.wrot matches 1.. run function last_ember:wound/rot_tick
execute if score @s le.wbl matches 1.. run function last_ember:wound/blood_tick
execute if score @s le.wmu matches 1.. run function last_ember:wound/murk_tick
execute if score @s le.wrt matches 1.. run function last_ember:wound/roots_tick
execute if score @s le.wqk matches 1.. run function last_ember:wound/quake_tick
execute if score @s le.wven matches 1.. run function last_ember:wound/venom_tick
execute unless score @s le.wrot matches 1.. unless score @s le.wbl matches 1.. unless score @s le.wmu matches 1.. unless score @s le.wrt matches 1.. unless score @s le.wqk matches 1.. unless score @s le.wven matches 1.. run tag @s remove le.wound
