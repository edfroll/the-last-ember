# T-026: the give button of a witch's window (trigger le.fgive = the witch): only before the choice, next to her, with the thing
scoreboard players operation #k le.fn = @s le.fgive
scoreboard players set @s le.fgive 0
execute unless score #choice le.fn matches 0 run return 0
execute store result score #ok le.fn run function last_ember:fens/gen/near_witch
execute if score #ok le.fn matches 0 run return 0
execute if score #k le.fn matches 1 store result score #h le.fn run clear @s *[minecraft:custom_data~{le_citem:"fens_vial"}] 0
execute if score #k le.fn matches 2 run function last_ember:fens/gen/count
execute if score #k le.fn matches 2 store result score #h le.fn run scoreboard players get #closed le.fn
execute if score #k le.fn matches 2 if score #h le.fn matches ..4 run return 0
execute if score #k le.fn matches 3 store result score #h le.fn run clear @s *[minecraft:custom_data~{le_citem:"fens_skull"}] 0
execute if score #h le.fn matches ..0 run return 0
function last_ember:fens/choose
