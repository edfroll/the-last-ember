# generated: a new holder of the key tear_creaker: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_tear_creaker] remove le.kh_tear_creaker
tag @s add le.kh_tear_creaker
data modify storage last_ember:keys k.tear_creaker.h set from entity @s UUID
