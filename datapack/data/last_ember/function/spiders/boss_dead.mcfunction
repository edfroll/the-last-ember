# T-032: the Mistress is dead (once a world): storage boss 1, the brood and the webs gone, «Чаща затихла.» to the players within 64;
# the elite spiders killed from now on do not come back; every player of the fight gets 2 Trophies of the Dol (spiders/second: now or
# when he comes back)
execute if score #boss le.sp matches 1 run return 0
scoreboard players set #boss le.sp 1
data modify storage last_ember:spiders boss set value 1
scoreboard players set #bs le.sp 0
execute as @e[type=minecraft:cave_spider,tag=le.sp_brood] run function last_ember:spiders/vanish
execute as @e[type=minecraft:marker,tag=le.spweb] at @s run function last_ember:spiders/web_clear
execute in minecraft:overworld positioned 129 95 -313 run title @a[distance=..64] actionbar {"text":"Чаща затихла.","color":"gray","italic":true}
