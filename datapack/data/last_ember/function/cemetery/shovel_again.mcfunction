# T-027: the shovel was lost (nobody in the game has it, it does not lie on the ground; cemetery/lost raised its generation): the keeper
# gives another
function last_ember:cemetery/give {key:"cem_shovel"}
scoreboard players set #sh le.cem 1
tellraw @s [{"text":"Смотритель: ","color":"gray"},{"text":"Лопату потеряли? Держите другую. Последняя.","color":"white"}]
function last_ember:cemetery/save
