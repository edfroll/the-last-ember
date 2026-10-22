# the ticks of this wearer were missed (he was away or the server was down): the same as a restart, but a piece that is already on him is not doubled
scoreboard players set #dd le.e 1
function last_ember:ring/restore_armor
function last_ember:ring/clear_state
scoreboard players set @s le.rcd 0
scoreboard players operation @s le.rcd = #gt le.e
scoreboard players add @s le.rcd 60
execute if items entity @s armor.head *[minecraft:custom_data~{le_ring:1b}] run item replace entity @s armor.head with minecraft:air
function last_ember:ring/give
