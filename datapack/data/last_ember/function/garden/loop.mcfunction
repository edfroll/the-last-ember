# T-025: every 5 ticks: the Stillness of the Creaking armour (all its wearers), the sculk sensors of the garden (while somebody is near and
# the garden is awake); every second the rest (hearts, faces, the sensor creakings, the door, the key, the stand) ; once asleep, every 10 ticks the eyeblossoms
# (the task says every 5 s; vanilla reopens ~3 of the 192 a second at night and each wakes its neighbours: every 5 s left ~25 open, every
# second up to ~9 within 40 blocks of the players at a moment)
schedule function last_ember:garden/loop 5t replace
execute store result score #gt le.gd run time query gametime
scoreboard players add #t le.gd 5
execute as @a[gamemode=!spectator] if items entity @s armor.head *[minecraft:custom_data~{le_creak:1b}] if items entity @s armor.chest *[minecraft:custom_data~{le_creak:1b}] if items entity @s armor.legs *[minecraft:custom_data~{le_creak:1b}] if items entity @s armor.feet *[minecraft:custom_data~{le_creak:1b}] at @s run function last_ember:creak/wear
execute in minecraft:overworld run function last_ember:garden/gen/near
execute if score #near le.gd matches 1.. if score #asleep le.gd matches 0 in minecraft:overworld run function last_ember:garden/gen/sensors
scoreboard players operation #t20 le.gd = #t le.gd
scoreboard players operation #t20 le.gd %= #20 le.gd
execute if score #t20 le.gd matches 0 in minecraft:overworld run function last_ember:garden/second
scoreboard players operation #t10 le.gd = #t le.gd
scoreboard players operation #t10 le.gd %= #10 le.gd
execute if score #t10 le.gd matches 0 if score #asleep le.gd matches 1 if score #near le.gd matches 1.. in minecraft:overworld run function last_ember:garden/gen/blooms
