# generated: a new holder of the key shard_ice_crown: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_shard_ice_crown] remove le.kh_shard_ice_crown
tag @s add le.kh_shard_ice_crown
data modify storage last_ember:keys k.shard_ice_crown.h set from entity @s UUID
