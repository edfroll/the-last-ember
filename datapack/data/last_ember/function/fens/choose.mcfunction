# T-026: as the player who gives the witch #k her thing: the first given thing decides (once a game): she gives the Crown of the Three
# Witches (the key of T-013, its current generation; the Call of the Ember no longer leads to the table: got = 1b), the two others are
# offended (prices x1.5, their quest items gone from everybody)
scoreboard players operation #choice le.fn = #k le.fn
execute store result storage last_ember:choices fens int 1 run scoreboard players get #choice le.fn
execute if score #k le.fn matches 1 run clear @s *[minecraft:custom_data~{le_citem:"fens_vial"}] 1
execute if score #k le.fn matches 1 run scoreboard players set #vs le.fn 3
execute if score #k le.fn matches 3 run clear @s *[minecraft:custom_data~{le_citem:"fens_skull"}] 1
execute if score #k le.fn matches 3 run scoreboard players set #sk le.fn 2
function last_ember:altar/gen/item_crown_witches with storage last_ember:keys k.crown_witches
data modify storage last_ember:keys k.crown_witches.got set value 1b
execute if score #k le.fn matches 1 run dialog show @s last_ember:fens/thanks_1
execute if score #k le.fn matches 2 run dialog show @s last_ember:fens/thanks_2
execute if score #k le.fn matches 3 run dialog show @s last_ember:fens/thanks_3
execute if score #k le.fn matches 1 run title @a actionbar {"text":"Мать Ряска отдала Венец. Сёстры обиделись.","color":"light_purple"}
execute if score #k le.fn matches 2 run title @a actionbar {"text":"Дева Осока отдала Венец. Сёстры обиделись.","color":"light_purple"}
execute if score #k le.fn matches 3 run title @a actionbar {"text":"Старуха Кость отдала Венец. Сёстры обиделись.","color":"light_purple"}
playsound minecraft:entity.witch.celebrate neutral @a[distance=..32] ~ ~ ~ 1 0.8
playsound minecraft:block.enchantment_table.use neutral @a[distance=..32] ~ ~ ~ 1 0.6
function last_ember:fens/purge
function last_ember:fens/gen/prices
function last_ember:fens/save
