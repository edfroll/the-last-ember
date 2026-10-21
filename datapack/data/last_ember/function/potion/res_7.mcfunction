# recipe water_breathing
data modify storage last_ember:pt it set value {id:"minecraft:potion",count:1,components:{"minecraft:potion_contents":{potion:"minecraft:water_breathing"}}}
data modify storage last_ember:pt pid set value "water_breathing"
data modify storage last_ember:pt ty set value "potion"
function last_ember:potion/boost_it
