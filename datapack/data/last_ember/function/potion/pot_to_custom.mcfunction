# storage last_ember:pt it: a vanilla potion becomes a custom-effects potion with the same name and colour (no boost)
data modify storage last_ember:pt pid set string storage last_ember:pt it.components."minecraft:potion_contents".potion 10
data modify storage last_ember:pt ty set string storage last_ember:pt it.id 10
data remove storage last_ember:pt pc
data modify storage last_ember:pt m set value "b"
function last_ember:potion/boost_mac with storage last_ember:pt
execute unless data storage last_ember:pt pc run return 0
data modify storage last_ember:pt it.components."minecraft:potion_contents" set from storage last_ember:pt pc
function last_ember:potion/boost_name with storage last_ember:pt
