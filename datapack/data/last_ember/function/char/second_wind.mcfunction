# as a human every tick: health < 6 -> a short regeneration II and strength I, cooldown 3 minutes
execute store result score @s le.hp run data get entity @s Health
execute if score @s le.hp matches 1..5 if score #gt le.e >= @s le.swcd run function last_ember:char/second_wind_go
