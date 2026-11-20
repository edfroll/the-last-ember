# T-026: the Maiden's introduction (once per player); the 5 bundles of sedge go to the first who hears it
tag @s add le.fh2
execute if score #sg le.fn matches 0 run function last_ember:fens/gen/give_fens_sedge {n:5}
execute if score #sg le.fn matches 0 run playsound minecraft:block.grass.break neutral @s ~ ~ ~ 1 0.8
execute if score #sg le.fn matches 0 run scoreboard players set #sg le.fn 1
function last_ember:fens/save
execute unless score #sg le.fn matches 0 if score #sg le.fn matches 1 run function last_ember:fens/sedge_again
dialog show @s last_ember:fens/intro_2
