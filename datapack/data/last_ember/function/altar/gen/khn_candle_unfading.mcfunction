# generated: a new holder of the key candle_unfading: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_candle_unfading] remove le.kh_candle_unfading
tag @s add le.kh_candle_unfading
data modify storage last_ember:keys k.candle_unfading.h set from entity @s UUID
