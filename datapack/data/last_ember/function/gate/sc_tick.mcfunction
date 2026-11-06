# every tick, as/at a player in transfer: still in the trigger? steps; at 0 the teleport
execute unless function last_ember:gate/gen/still run return run function last_ember:gate/sc_cancel
scoreboard players remove @s le.sct 1
execute if score @s le.sct matches 12 run playsound minecraft:block.stone.step player @s ~ ~ ~ 0.5 0.6
execute if score @s le.sct matches 5 run playsound minecraft:block.stone.step player @s ~ ~ ~ 0.4 0.6
execute if score @s le.sct matches ..0 run function last_ember:gate/gen/arrive
