# T-026: every second while the skull of the Master is carried: old copies go; nobody in the game has it and it does not lie on the
# ground -> lost: a new generation, the Master is in the dark gap again (he gives the skull again)
execute unless score #sk le.fn matches 1 run return 0
function last_ember:fens/invalid with storage last_ember:fens skull
function last_ember:fens/count with storage last_ember:fens skull
execute if score #c le.fn matches 1.. run return 0
execute store result score #g le.fn run data get storage last_ember:fens skull.gen
scoreboard players add #g le.fn 1
execute store result storage last_ember:fens skull.gen int 1 run scoreboard players get #g le.fn
scoreboard players set #sk le.fn 0
execute if score #ms le.fn matches 2 run scoreboard players set #ms le.fn 0
function last_ember:fens/save
