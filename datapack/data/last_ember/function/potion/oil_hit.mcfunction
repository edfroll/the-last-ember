# as a player who has hurt an entity: an oiled weapon poisons / sets fire and loses one hit
advancement revoke @s only last_ember:potion/oil_hit
execute unless items entity @s weapon.mainhand *[minecraft:custom_data~{le_oil:{type:"poison"}}] unless items entity @s weapon.mainhand *[minecraft:custom_data~{le_oil:{type:"fire"}}] run return 0
tag @s add le.oiler
scoreboard players set #oilhit le.e 0
scoreboard players set #oilp le.e 0
execute if items entity @s weapon.mainhand *[minecraft:custom_data~{le_oil:{type:"poison"}}] run scoreboard players set #oilp le.e 1
# a blow on a centipede segment (lab/cent/hurt): the victim is its carrier, wherever it is
execute as @e[tag=le.chitv,limit=1] at @s run function last_ember:potion/oil_victim
execute if score #oilhit le.e matches 0 as @e[type=#last_ember:monsters,distance=..6,sort=nearest,limit=1] at @s run function last_ember:potion/oil_victim
tag @s remove le.oiler
execute if score #oilhit le.e matches 0 run return 0
data modify storage last_ember:pt n set from entity @s SelectedItem.components."minecraft:custom_data".le_oil.n
execute store result score #n le.e run data get storage last_ember:pt n
scoreboard players remove #n le.e 1
execute store result storage last_ember:pt n int 1 run scoreboard players get #n le.e
execute if score #n le.e matches 0 run function last_ember:potion/oil_clear
execute if score #n le.e matches 0 run title @s actionbar {"text":"Масло кончилось","color":"gray"}
execute if score #n le.e matches 1.. if items entity @s weapon.mainhand *[minecraft:custom_data~{le_oil:{type:"poison"}}] run data modify storage last_ember:pt oil set value "poison"
execute if score #n le.e matches 1.. if items entity @s weapon.mainhand *[minecraft:custom_data~{le_oil:{type:"fire"}}] run data modify storage last_ember:pt oil set value "fire"
data modify storage last_ember:pt sfx set value "_r"
execute if score #n le.e matches 1.. run function last_ember:potion/oil_mod with storage last_ember:pt
