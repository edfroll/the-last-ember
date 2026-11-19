# T-026: as a player at the Maiden's mirror (the bundles were given once): the lost bundles again - as many as there are pools still
# open, less the bundles the players in the game hold
execute unless score #sg le.fn matches 1 run return 0
function last_ember:fens/gen/open_pools
execute store result score #h le.fn run clear @a *[minecraft:custom_data~{le_citem:"fens_sedge"}] 0
scoreboard players operation #c le.fn -= #h le.fn
execute if score #c le.fn matches ..0 run return 0
execute store result storage last_ember:fens n int 1 run scoreboard players get #c le.fn
function last_ember:fens/sedge_give with storage last_ember:fens
playsound minecraft:block.grass.break neutral @s ~ ~ ~ 1 0.8
