# generated: a new holder of the key drop_source: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_drop_source] remove le.kh_drop_source
tag @s add le.kh_drop_source
data modify storage last_ember:keys k.drop_source.h set from entity @s UUID
