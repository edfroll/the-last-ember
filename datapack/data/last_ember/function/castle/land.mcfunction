# T-028: the end of the flight: in the water of the knock zone; 3 s of grace before the colossi may wake for him again
tag @s remove le.cfly
scoreboard players set @s le.cf 0
execute store result score @s le.cg run time query gametime
scoreboard players add @s le.cg 60
execute at @s run particle minecraft:splash ~ ~1 ~ 1 0.5 1 0.2 60 force @a[distance=..64]
execute at @s run playsound minecraft:entity.player.splash.high_speed player @a[distance=..48] ~ ~ ~ 1.5 0.8
