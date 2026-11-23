# T-032: the Mistress at half her health: her brood out of the walls (3 cave spiders, once a fight)
scoreboard players set #brood le.sp 1
function last_ember:spiders/gen/brood_put
execute as @e[type=minecraft:spider,tag=le.sp_boss,limit=1] at @s run playsound minecraft:entity.spider.death hostile @a[distance=..48] ~ ~2 ~ 2 0.6
