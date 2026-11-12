# generated: a new holder of the key banner_dawn: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_banner_dawn] remove le.kh_banner_dawn
tag @s add le.kh_banner_dawn
data modify storage last_ember:keys k.banner_dawn.h set from entity @s UUID
