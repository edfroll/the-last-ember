# generated: a new holder of the key tear_titan: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_tear_titan] remove le.kh_tear_titan
tag @s add le.kh_tear_titan
data modify storage last_ember:keys k.tear_titan.h set from entity @s UUID
