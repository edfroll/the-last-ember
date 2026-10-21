# as a hearth interaction: is its bonfire lit?
execute store result storage last_ember:bt i int 1 run scoreboard players get @s le.bidx
function last_ember:bonfire/load_cur with storage last_ember:bt
execute if data storage last_ember:bt cur{state:1} run scoreboard players set #lit le.e 1
