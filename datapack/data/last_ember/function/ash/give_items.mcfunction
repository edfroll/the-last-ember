# each item as an item entity on the player with no pickup delay: picked up at once, what does not fit stays on the ground
execute unless data storage last_ember:dt give[0] run return 0
data remove storage last_ember:dt give[0].Slot
summon minecraft:item ~ ~ ~ {Item:{id:"minecraft:stone",count:1},PickupDelay:0,Tags:["le.give","le.out"]}
data modify entity @e[type=minecraft:item,tag=le.give,limit=1,sort=nearest] Item set from storage last_ember:dt give[0]
tag @e[type=minecraft:item,tag=le.give] remove le.give
data remove storage last_ember:dt give[0]
function last_ember:ash/give_items
