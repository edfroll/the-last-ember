# T-026: every 5 ticks while the Master is up: on his leash (12 from the gap); every player further than 48 -> back into the gap
# (gone, full health the next time); gone without a player's blow (lava, the void...) -> in the gap again
execute store result score #ok le.fn run function last_ember:fens/gen/master_loaded
execute if score #ok le.fn matches 0 run return 0
# (the entities of a chunk load after its blocks: gone for 2 s on end, not just this moment)
execute if entity @e[type=minecraft:drowned,tag=le.fmaster] run scoreboard players set #mabs le.fn 0
execute unless entity @e[type=minecraft:drowned,tag=le.fmaster] run scoreboard players add #mabs le.fn 5
execute if score #mabs le.fn matches 40.. run scoreboard players set #ms le.fn 0
execute if score #mabs le.fn matches 40.. run scoreboard players set #mabs le.fn 0
execute unless entity @e[type=minecraft:drowned,tag=le.fmaster] run return run function last_ember:fens/save
execute store result score #c le.fn if entity @e[type=minecraft:drowned,tag=le.fmaster]
execute if score #c le.fn matches 2.. as @e[type=minecraft:drowned,tag=le.fmaster,limit=1] run tag @s add le.fone
execute if score #c le.fn matches 2.. as @e[type=minecraft:drowned,tag=le.fmaster,tag=!le.fone] at @s run tp @s ~ ~-300 ~
execute if score #c le.fn matches 2.. run kill @e[type=minecraft:drowned,tag=le.fmaster,tag=!le.fone]
tag @e[type=minecraft:drowned,tag=le.fone] remove le.fone
execute as @e[type=minecraft:drowned,tag=le.fmaster] run function last_ember:fens/gen/master_leash
execute store result score #ok le.fn run function last_ember:fens/gen/master_far
execute if score #ok le.fn matches 1 run function last_ember:fens/master_gone
