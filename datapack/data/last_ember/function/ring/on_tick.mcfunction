# every tick, as a wearer at himself: the modifiers, still in the world? the ring still on? the armor slots empty? the fee
execute if score @s le.rpend matches 2.. run return run scoreboard players remove @s le.rpend 1
execute if score @s le.rpend matches 1 run function last_ember:ring/finish_mods
scoreboard players operation #d le.e = #gt le.e
scoreboard players operation #d le.e -= @s le.rlast
execute unless score #d le.e matches 0..5 run return run function last_ember:ring/off_rejoin
scoreboard players operation @s le.rlast = #gt le.e
execute unless items entity @s armor.head *[minecraft:custom_data~{le_ring:1b}] run return run function last_ember:ring/off
execute if data entity @s equipment.chest run function last_ember:ring/eject {slot:"chest"}
execute if data entity @s equipment.legs run function last_ember:ring/eject {slot:"legs"}
execute if data entity @s equipment.feet run function last_ember:ring/eject {slot:"feet"}
scoreboard players operation #m le.e = #gt le.e
scoreboard players operation #m le.e -= @s le.rt
scoreboard players operation #m le.e %= #20 le.e
execute if score #m le.e matches 0 run function last_ember:ring/pay
execute if score #m le.e matches 0 run effect give @s minecraft:invisibility 2 0 true
