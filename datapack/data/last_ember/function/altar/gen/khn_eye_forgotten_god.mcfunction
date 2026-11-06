# generated: a new holder of the key eye_forgotten_god: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_eye_forgotten_god] remove le.kh_eye_forgotten_god
tag @s add le.kh_eye_forgotten_god
data modify storage last_ember:keys k.eye_forgotten_god.h set from entity @s UUID
