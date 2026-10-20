# TEST/ADMIN: makes @s the carrier; any other Ember (carried, socketed, lost) becomes invalid
tag @a remove le.carrier
function last_ember:ember/bump_gen
kill @e[type=minecraft:item_display,tag=le.ember_disp]
data modify storage last_ember:ember socket set value -1
function last_ember:ember/give
