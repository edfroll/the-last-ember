# as a player: the armor from the storage (else from the copy inside the ring) back into the slots. #dd = 1: a piece that is already on him (compared by components) is not given again.
function last_ember:ring/key
data modify storage last_ember:ring cur set value {}
function last_ember:ring/load_m with storage last_ember:ring u
execute unless data storage last_ember:ring cur.chest unless data storage last_ember:ring cur.legs unless data storage last_ember:ring cur.feet run data modify storage last_ember:ring cur set from entity @s equipment.head.components."minecraft:custom_data".stash
execute unless data storage last_ember:ring cur.chest unless data storage last_ember:ring cur.legs unless data storage last_ember:ring cur.feet run data modify storage last_ember:ring cur set from entity @s Inventory[{components:{"minecraft:custom_data":{le_ring:1b}}}].components."minecraft:custom_data".stash
summon minecraft:armor_stand ~ ~ ~ {Marker:1b,Invisible:1b,NoGravity:1b,Silent:1b,Tags:["le.ringstand"]}
function last_ember:ring/back {slot:"chest"}
function last_ember:ring/back {slot:"legs"}
function last_ember:ring/back {slot:"feet"}
kill @e[type=minecraft:armor_stand,tag=le.ringstand]
function last_ember:ring/forget_m with storage last_ember:ring u
