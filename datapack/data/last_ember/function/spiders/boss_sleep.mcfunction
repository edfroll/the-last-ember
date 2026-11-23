# T-032: as the Mistress: nobody alive in the nest 10 s - the fight resets: on her lair, full health, asleep; the brood and the webs gone
function last_ember:spiders/gen/boss_home
data modify entity @s NoAI set value 1b
execute store result entity @s Health float 1 run attribute @s minecraft:max_health get
scoreboard players set #bs le.sp 0
scoreboard players set #empty le.sp 0
execute as @e[type=minecraft:cave_spider,tag=le.sp_brood] run function last_ember:spiders/vanish
execute as @e[type=minecraft:marker,tag=le.spweb] at @s run function last_ember:spiders/web_clear
