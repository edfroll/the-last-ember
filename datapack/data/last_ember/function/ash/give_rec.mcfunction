# as/at the receiving player: items of storage last_ember:dt rec (unchanged components) + XP
data modify storage last_ember:dt give set from storage last_ember:dt rec.items
function last_ember:ash/give_items
function last_ember:ash/give_xp with storage last_ember:dt rec
