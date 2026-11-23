# T-032: every 5 ticks: the buttons of Toivo's windows; (players near) the elite spiders wake (a player not in spectator/creative within
# 6), the trip wires, the Mistress (wakes when a player is in the nest; awake: the leash, the empty nest, the brood, the webs); every
# second the rest (spiders/second)
schedule function last_ember:spiders/loop 5t replace
execute as @a[scores={le.sptrig=1..}] at @s run function last_ember:spiders/trig
scoreboard players add #t le.sp 1
execute if score #t le.sp matches 4.. in minecraft:overworld run function last_ember:spiders/second
execute if score #near le.sp matches 0 run return 0
execute store result score #gt le.sp run time query gametime
execute in minecraft:overworld as @e[type=minecraft:spider,tag=le.sprest] at @s if entity @a[gamemode=!spectator,gamemode=!creative,distance=..6] run function last_ember:spiders/wake
execute in minecraft:overworld run function last_ember:spiders/gen/trip_chk
execute if score #boss le.sp matches 1 run return 0
execute in minecraft:overworld run function last_ember:spiders/gen/count_nest
execute if score #bs le.sp matches 0 if score #innest le.sp matches 1.. as @e[type=minecraft:spider,tag=le.sp_boss,limit=1] run function last_ember:spiders/boss_wake
execute if score #bs le.sp matches 1 in minecraft:overworld run function last_ember:spiders/boss_tick
execute in minecraft:overworld as @e[type=minecraft:marker,tag=le.spweb] if score @s le.spwt <= #gt le.sp at @s run function last_ember:spiders/web_clear
