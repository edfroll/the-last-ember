# generated: a new holder of the key crown_witches: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_crown_witches] remove le.kh_crown_witches
tag @s add le.kh_crown_witches
data modify storage last_ember:keys k.crown_witches.h set from entity @s UUID
