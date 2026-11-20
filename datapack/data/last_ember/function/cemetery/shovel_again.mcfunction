# T-027: the shovel was lost (nobody in the game has it, it does not lie on the ground): the keeper gives another (a new generation)
execute store result score #g le.cem run data get storage last_ember:cemetery gen.cem_shovel
scoreboard players add #g le.cem 1
execute store result storage last_ember:cemetery gen.cem_shovel int 1 run scoreboard players get #g le.cem
function last_ember:cemetery/gen/give_cem_shovel with storage last_ember:cemetery gen
scoreboard players set #sh le.cem 1
tellraw @s [{"text":"Смотритель: ","color":"gray"},{"text":"Лопату потеряли? Держите другую. Последняя.","color":"white"}]
function last_ember:cemetery/save
