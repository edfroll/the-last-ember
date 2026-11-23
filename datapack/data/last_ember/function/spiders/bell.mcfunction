# T-032: «Звонить и за вас»: the first of 3 far strokes (each player hears it at himself: quiet, low)
execute as @a at @s run playsound minecraft:block.bell.use master @s ~ ~ ~ 0.35 0.6
scoreboard players add #rang le.sp 1
schedule function last_ember:spiders/bell_2 30t replace
