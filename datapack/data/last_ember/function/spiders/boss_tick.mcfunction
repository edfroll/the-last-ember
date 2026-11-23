# T-032: every 5 ticks while the Mistress is awake: the leash (out of the nest's box: back on her lair); nobody alive in the nest 10 s:
# reset (asleep, full health, the brood gone); at half her health the brood (once a fight)
function last_ember:spiders/gen/leash
execute if score #innest le.sp matches 0 run scoreboard players add #empty le.sp 5
execute if score #innest le.sp matches 1.. run scoreboard players set #empty le.sp 0
execute if score #empty le.sp matches 200.. as @e[type=minecraft:spider,tag=le.sp_boss,limit=1] run return run function last_ember:spiders/boss_sleep
execute if score #brood le.sp matches 1 run return 0
execute store result score #bh le.sp run data get entity @e[type=minecraft:spider,tag=le.sp_boss,limit=1] Health
execute if score #bh le.sp matches 1.. if score #bh le.sp <= #bhalf le.sp run function last_ember:spiders/brood
