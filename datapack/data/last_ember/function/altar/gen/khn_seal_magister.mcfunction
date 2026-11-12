# generated: a new holder of the key seal_magister: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_seal_magister] remove le.kh_seal_magister
tag @s add le.kh_seal_magister
data modify storage last_ember:keys k.seal_magister.h set from entity @s UUID
