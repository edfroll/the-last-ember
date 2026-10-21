# recipe strength
data modify storage last_ember:pt it set value {id:"minecraft:potion",count:1,components:{"minecraft:potion_contents":{potion:"minecraft:strength"}}}
data modify storage last_ember:pt pid set value "strength"
data modify storage last_ember:pt ty set value "potion"
function last_ember:potion/boost_it
