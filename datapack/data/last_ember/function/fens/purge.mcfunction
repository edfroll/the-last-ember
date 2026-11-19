# T-026: after the choice: the quest items of the two other witches are gone from everybody in the game (a player who was away loses
# them when he comes back: this runs every second) and from the ground; the vial also from the ambush chest
execute unless score #choice le.fn matches 1 run clear @a *[minecraft:custom_data~{le_citem:"fens_vial"}]
execute unless score #choice le.fn matches 1 as @e[type=minecraft:item] if items entity @s contents *[minecraft:custom_data~{le_citem:"fens_vial"}] run kill @s
execute unless score #choice le.fn matches 1 unless score #vs le.fn matches 3 run function last_ember:fens/vial_void
execute unless score #choice le.fn matches 2 run clear @a *[minecraft:custom_data~{le_citem:"fens_sedge"}]
execute unless score #choice le.fn matches 2 as @e[type=minecraft:item] if items entity @s contents *[minecraft:custom_data~{le_citem:"fens_sedge"}] run kill @s
execute unless score #choice le.fn matches 3 run clear @a *[minecraft:custom_data~{le_citem:"fens_skull"}]
execute unless score #choice le.fn matches 3 as @e[type=minecraft:item] if items entity @s contents *[minecraft:custom_data~{le_citem:"fens_skull"}] run kill @s
execute unless score #choice le.fn matches 3 if score #sk le.fn matches 0..1 run scoreboard players set #sk le.fn 2
execute unless score #choice le.fn matches 3 if score #ms le.fn matches 2 run scoreboard players set #ms le.fn 0
