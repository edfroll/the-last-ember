# as the dead player: record of the trail, then either a trail on the ground or straight to the urn
function last_ember:death/gen/region
data modify storage last_ember:dt rec set value {}
data modify storage last_ember:dt rec.items set from storage last_ember:dt inv
data modify storage last_ember:dt rec.lv set from storage last_ember:dt lv
data modify storage last_ember:dt rec.pts set from storage last_ember:dt pts
data modify storage last_ember:dt rec.urn set from storage last_ember:dt urn
data modify storage last_ember:dt rec.dim set from storage last_ember:dt dim
data modify storage last_ember:dt rec.owner set from entity @s UUID
function last_ember:ash/owner_name
function last_ember:death/gen/is_void
execute store result storage last_ember:dt p.x int 1 run scoreboard players get #x le.e
execute store result storage last_ember:dt p.y int 1 run scoreboard players get #y le.e
execute store result storage last_ember:dt p.z int 1 run scoreboard players get #z le.e
data modify storage last_ember:dt p.dim set from storage last_ember:dt dim
execute if score #void le.e matches 0 run function last_ember:ash/place with storage last_ember:dt p
execute if score #void le.e matches 1 run function last_ember:ash/rec_to_urn
