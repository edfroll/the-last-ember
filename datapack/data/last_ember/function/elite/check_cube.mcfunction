# as an elite slime / magma cube (every scan): the small ones that a dying elite splits into copy its tags and name; they are ordinary mobs
execute store result score #sz le.el run data get entity @s Size
execute if score #sz le.el matches 3.. run return 0
function last_ember:elite/unmake
data remove entity @s CustomName
data modify entity @s CustomNameVisible set value 0b
