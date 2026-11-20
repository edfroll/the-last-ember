# T-026: every second while the vial is carried: old copies go; back in the chest -> in the chest again; nobody in the game has it and it
# does not lie on the ground -> lost: a new generation, it goes back into the chest (the quest can start again)
function last_ember:fens/invalid with storage last_ember:fens vial
function last_ember:fens/count with storage last_ember:fens vial
execute if score #c le.fn matches 1.. run return 0
function last_ember:fens/gen/vial_in_chest
execute if score #c le.fn matches 1 run scoreboard players set #vs le.fn 1
execute if score #c le.fn matches 1 run return run function last_ember:fens/save
execute store result score #g le.fn run data get storage last_ember:fens vial.gen
scoreboard players add #g le.fn 1
execute store result storage last_ember:fens vial.gen int 1 run scoreboard players get #g le.fn
scoreboard players set #vs le.fn 0
function last_ember:fens/save
