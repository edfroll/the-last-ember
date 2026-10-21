# as a sated player, every second
execute if score #gt le.e > @s le.sat run return run tag @s remove le.sated
scoreboard players add @s le.satcd 1
execute if score @s le.satcd matches 40.. run function last_ember:knight/sated_food
