execute unless data storage last_ember:dt tr[0] run return 0
data modify storage last_ember:dt rec set from storage last_ember:dt tr[0]
function last_ember:ash/give_rec
data remove storage last_ember:dt tr[0]
function last_ember:urn/give_all
