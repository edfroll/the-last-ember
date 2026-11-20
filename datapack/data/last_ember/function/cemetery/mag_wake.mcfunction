# T-027: the door is open: a player within 10 of the sarcophagus wakes the Magister (on the peaceful difficulty he counts as laid to rest)
function last_ember:cemetery/gen/near_sarc
execute if score #c le.cem matches 0 run return 0
execute store result score #d le.cem run difficulty
execute if score #d le.cem matches 0 run return run function last_ember:cemetery/mag_rest
scoreboard players set #mg le.cem 3
scoreboard players set #mt le.cem 0
