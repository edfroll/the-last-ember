# generated: a new holder of the key seal_whirl: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_seal_whirl] remove le.kh_seal_whirl
tag @s add le.kh_seal_whirl
data modify storage last_ember:keys k.seal_whirl.h set from entity @s UUID
