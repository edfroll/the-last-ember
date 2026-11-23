# T-032: admin: the Mistress alive and asleep on her lair (storage boss 0), her brood and webs gone, no participants
scoreboard players set #boss le.sp 0
data modify storage last_ember:spiders boss set value 0
tag @a remove le.sppart
execute as @e[type=minecraft:cave_spider,tag=le.sp_brood] run function last_ember:spiders/vanish
execute as @e[type=minecraft:marker,tag=le.spweb] at @s run function last_ember:spiders/web_clear
function last_ember:spiders/gen/boss_put
