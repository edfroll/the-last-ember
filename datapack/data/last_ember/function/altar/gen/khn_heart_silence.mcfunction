# generated: a new holder of the key heart_silence: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_heart_silence] remove le.kh_heart_silence
tag @s add le.kh_heart_silence
data modify storage last_ember:keys k.heart_silence.h set from entity @s UUID
