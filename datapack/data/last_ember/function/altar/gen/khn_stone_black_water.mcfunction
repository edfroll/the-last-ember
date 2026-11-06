# generated: a new holder of the key stone_black_water: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_stone_black_water] remove le.kh_stone_black_water
tag @s add le.kh_stone_black_water
data modify storage last_ember:keys k.stone_black_water.h set from entity @s UUID
