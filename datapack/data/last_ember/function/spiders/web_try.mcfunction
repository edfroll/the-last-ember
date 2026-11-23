# T-032: as the Mistress at her: a player in the nest farther than 6 whose line to her eyes is free gets web at his feet (5 s)
tag @a remove le.spwt
tag @a[tag=le.spin,distance=6..,sort=random,limit=1] add le.spwt
execute unless entity @a[tag=le.spwt] run return 0
scoreboard players set #rs le.sp 0
execute store result score #los le.sp anchored eyes positioned ^ ^ ^ facing entity @a[tag=le.spwt,limit=1] eyes run function last_ember:spiders/ray
execute unless score #los le.sp matches 1 run return run tag @a remove le.spwt
playsound minecraft:entity.llama.spit hostile @a[distance=..32] ~ ~2 ~ 1.5 0.5
execute as @a[tag=le.spwt,limit=1] at @s if block ~ ~ ~ minecraft:air run function last_ember:spiders/web_put
tag @a remove le.spwt
