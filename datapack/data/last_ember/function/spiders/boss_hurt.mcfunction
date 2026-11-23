# T-032: advancement reward: a player hit the Mistress: asleep - she wakes; the player takes part in this fight (the trophies at her death)
advancement revoke @s only last_ember:spiders/boss_hurt
execute if score #bs le.sp matches 0 as @e[type=minecraft:spider,tag=le.sp_boss,limit=1] run function last_ember:spiders/boss_wake
tag @s add le.sppart
scoreboard players operation @s le.spfight = #fight le.sp
