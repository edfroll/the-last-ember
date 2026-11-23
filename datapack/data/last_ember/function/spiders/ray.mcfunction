# T-032: a step of the Mistress's line of sight (0.5 block, 40 steps): 1 = the target reached, 0 = blocked
scoreboard players add #rs le.sp 1
execute if score #rs le.sp matches 80.. run return 0
execute positioned ~ ~-1.62 ~ if entity @a[tag=le.spwt,distance=..1] run return 1
execute unless block ~ ~ ~ #last_ember:spiders_ray run return 0
execute positioned ^ ^ ^0.5 run return run function last_ember:spiders/ray
