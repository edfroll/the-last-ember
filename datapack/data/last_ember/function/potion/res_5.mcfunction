# recipe poison
data modify storage last_ember:pt it set value {id:"minecraft:splash_potion",count:1,components:{"minecraft:potion_contents":{potion:"minecraft:poison"}}}
data modify storage last_ember:pt pid set value "poison"
data modify storage last_ember:pt ty set value "splash_potion"
function last_ember:potion/boost_it
