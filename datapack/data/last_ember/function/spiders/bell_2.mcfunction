# T-032: the second far stroke
execute as @a at @s run playsound minecraft:block.bell.use master @s ~ ~ ~ 0.35 0.6
scoreboard players add #rang le.sp 1
schedule function last_ember:spiders/bell_3 30t replace
