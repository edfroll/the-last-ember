# T-032: advancement reward: a player right-clicked the live cocoon: a blade (sword, axe) or shears in the main hand cut it (not more often
# than every 0.5 s, any players); the first cut while the Mistress lives calls her brood; the third opens it and Toivo falls out
advancement revoke @s only last_ember:spiders/cut
execute unless score #toivo le.sp matches 0 run return 0
execute store result score #gt le.sp run time query gametime
scoreboard players set #blade le.sp 0
execute if items entity @s weapon.mainhand #minecraft:swords run scoreboard players set #blade le.sp 1
execute if items entity @s weapon.mainhand #minecraft:axes run scoreboard players set #blade le.sp 1
execute if items entity @s weapon.mainhand minecraft:shears run scoreboard players set #blade le.sp 1
execute if score #blade le.sp matches 0 as @e[type=minecraft:interaction,tag=le.sp_coc,limit=1] at @s run return run playsound minecraft:block.wool.hit block @a[distance=..12] ~ ~2 ~ 0.6 0.8
scoreboard players operation #d le.sp = #gt le.sp
scoreboard players operation #d le.sp -= #cutt le.sp
execute if score #d le.sp matches ..9 run return 0
scoreboard players operation #cutt le.sp = #gt le.sp
scoreboard players add #cuts le.sp 1
execute as @e[type=minecraft:interaction,tag=le.sp_coc,limit=1] at @s run playsound minecraft:entity.sheep.shear block @a[distance=..16] ~ ~2 ~ 1 0.6
execute as @e[type=minecraft:interaction,tag=le.sp_coc,limit=1] at @s run playsound minecraft:block.wool.break block @a[distance=..16] ~ ~2 ~ 1 0.7
execute as @e[type=minecraft:interaction,tag=le.sp_coc,limit=1] at @s run particle minecraft:block{block_state:"minecraft:white_wool"} ~ ~2 ~ 0.6 0.8 0.6 0 30
execute if score #cuts le.sp matches 1 if score #boss le.sp matches 0 if score #cb le.sp matches 0 run function last_ember:spiders/cocoon_brood
execute if score #cuts le.sp matches 3.. run function last_ember:spiders/free
