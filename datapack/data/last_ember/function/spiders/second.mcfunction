# T-032: every second (in the overworld, players near the place): the difficulty, the day time, the old generations, the points of the
# elite spiders (alive / killed / back at dawn while the Mistress lives), the awake ones home when nobody is within 40, the resting ones
# hiss now and then; the Mistress (present, peaceful, the reward of the fight), the wires set again, the fire round the players, the
# props, Toivo (his point, home)
scoreboard players set #t le.sp 0
scoreboard players add #sec le.sp 1
scoreboard players enable @a le.sptrig
execute as @a[tag=le.sppart] if score #boss le.sp matches 1 if score @s le.spfight = #fight le.sp run function last_ember:spiders/pay
function last_ember:spiders/gen/toivo_check
function last_ember:spiders/gen/near
execute if score #near le.sp matches 0 run return 0
execute store result score #df le.sp run difficulty
execute store result score #ck le.sp run time query time
scoreboard players operation #day le.sp = #ck le.sp
scoreboard players operation #day le.sp /= #24000 le.sp
scoreboard players operation #dt le.sp = #ck le.sp
scoreboard players operation #dt le.sp %= #24000 le.sp
execute if score #df le.sp matches 0 run function last_ember:spiders/gen/forget
execute if score #df le.sp matches 0 if score #boss le.sp matches 0 run function last_ember:spiders/boss_peace
execute as @e[type=minecraft:spider,tag=le.sp_el] run function last_ember:spiders/gen/genchk
execute as @e[type=minecraft:spider,tag=le.sp_boss] unless score @s le.spbg = #bgen le.sp run function last_ember:spiders/vanish
execute as @e[tag=le.spt] unless score @s le.sptg = #tgen le.sp run kill @s
function last_ember:spiders/gen/points
execute as @e[type=minecraft:spider,tag=le.spawk] at @s unless entity @a[gamemode=!spectator,distance=..40] run function last_ember:spiders/rest
execute as @e[type=minecraft:cave_spider,tag=le.sp_brood] at @s if score #bs le.sp matches 0 unless entity @a[gamemode=!spectator,distance=..40] run function last_ember:spiders/vanish
execute as @e[type=minecraft:spider,tag=le.sprest] if predicate last_ember:spiders/sound at @s run playsound minecraft:entity.spider.ambient hostile @a ~ ~ ~ 0.7 0.75
execute if score #boss le.sp matches 0 if score #df le.sp matches 1.. run function last_ember:spiders/gen/boss_check
execute if score #bs le.sp matches 1 run function last_ember:spiders/boss_second
function last_ember:spiders/gen/trip_fixes
function last_ember:spiders/gen/fire_near
function last_ember:spiders/gen/props_check
function last_ember:spiders/gen/toivo_go
