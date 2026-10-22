# as/at the clicked pedestal interaction; the player is @a[tag=le.clicker]
data remove entity @s interaction
execute store result storage last_ember:altar c.pid int 1 run scoreboard players get @s le.pid
function last_ember:altar/ped_load with storage last_ember:altar c
function last_ember:altar/ped_click2 with storage last_ember:altar ped
