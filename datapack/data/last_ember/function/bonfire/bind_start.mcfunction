execute store result storage last_ember:bt i int 1 run scoreboard players get #start le.e
function last_ember:bonfire/load_cur with storage last_ember:bt
execute if data storage last_ember:bt cur.rx run function last_ember:bonfire/bind
