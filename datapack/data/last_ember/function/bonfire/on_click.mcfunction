# as/at the clicked interaction entity; the player is @a[tag=le.clicker]
data remove entity @s interaction
execute store result storage last_ember:bt i int 1 run scoreboard players get @s le.bidx
function last_ember:bonfire/load_cur with storage last_ember:bt
execute if entity @s[tag=le.hearth] run function last_ember:bonfire/hearth
execute if entity @s[tag=le.stela] run function last_ember:ember/stela
