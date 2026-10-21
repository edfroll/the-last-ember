execute unless data storage last_ember:dt rm[0] run return 0
execute store result storage last_ember:dt s int 1 run data get storage last_ember:dt rm[0].Slot
function last_ember:death/remove_slot with storage last_ember:dt
data remove storage last_ember:dt rm[0]
function last_ember:death/remove_items
