# T-028: the colossi wake for @s (no seal near, or on the rock without the pass): 1 s of warning (castle/wake_tick), then the strike
tag @s add le.cwake
scoreboard players set @s le.cw 20
scoreboard players set #eyes le.cas 1
scoreboard players operation #eyet le.cas = #gt le.cas
scoreboard players add #eyet le.cas 80
execute unless score #eyesv le.cas = #eyes le.cas run function last_ember:castle/gen/eyes_sync
function last_ember:castle/gen/charge_n
function last_ember:castle/gen/charge_s
title @s actionbar {"text":"Колоссы поднимают ладони.","color":"gray","italic":true}
schedule function last_ember:castle/tick 1t replace
