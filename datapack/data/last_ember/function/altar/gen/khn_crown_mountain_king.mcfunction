# generated: a new holder of the key crown_mountain_king: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_crown_mountain_king] remove le.kh_crown_mountain_king
tag @s add le.kh_crown_mountain_king
data modify storage last_ember:keys k.crown_mountain_king.h set from entity @s UUID
