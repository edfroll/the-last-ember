# T-032: peaceful difficulty: the Mistress counts as defeated (as the King of T-029), no trophies
scoreboard players set #boss le.sp 1
data modify storage last_ember:spiders boss set value 1
scoreboard players set #bs le.sp 0
tag @a remove le.sppart
execute as @e[type=minecraft:spider,tag=le.sp_boss] run function last_ember:spiders/vanish
execute as @e[type=minecraft:cave_spider,tag=le.sp_brood] run function last_ember:spiders/vanish
