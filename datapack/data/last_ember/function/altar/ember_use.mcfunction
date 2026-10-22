# advancement reward of using_item with the Ember (every tick while it is held): Call, on the first tick of a Shift + right click
advancement revoke @s only last_ember:ember/using
scoreboard players operation #d le.alt = #gt le.e
scoreboard players operation #d le.alt -= @s le.eslast
scoreboard players operation @s le.eslast = #gt le.e
execute if score #d le.alt matches ..2 run return 0
execute unless entity @s[tag=le.carrier] run return 0
execute unless predicate last_ember:sneaking run return 0
execute unless score #chapters le.alt matches 3.. run return 0
execute if score #gt le.e < @s le.ecd run return run function last_ember:altar/call_wait
scoreboard players operation @s le.ecd = #gt le.e
scoreboard players add @s le.ecd 1200
function last_ember:altar/call_run
