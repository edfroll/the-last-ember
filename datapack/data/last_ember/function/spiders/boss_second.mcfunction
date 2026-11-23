# T-032: every second while the Mistress is awake: the web (every 8 s) at a player farther than 6 with a free line to her
scoreboard players remove #web le.sp 1
execute if score #web le.sp matches 1.. run return 0
scoreboard players set #web le.sp 8
execute as @e[type=minecraft:spider,tag=le.sp_boss,limit=1] at @s run function last_ember:spiders/web_try
