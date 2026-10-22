# as a player: his shadow is removed
scoreboard players operation #me le.h = @s le.hid
execute as @e[type=minecraft:marker,tag=le.hmark] if score @s le.hid = #me le.h run kill @s
scoreboard players set @s le.hst 0
