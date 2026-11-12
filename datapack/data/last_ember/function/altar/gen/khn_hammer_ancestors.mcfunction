# generated: a new holder of the key hammer_ancestors: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_hammer_ancestors] remove le.kh_hammer_ancestors
tag @s add le.kh_hammer_ancestors
data modify storage last_ember:keys k.hammer_ancestors.h set from entity @s UUID
