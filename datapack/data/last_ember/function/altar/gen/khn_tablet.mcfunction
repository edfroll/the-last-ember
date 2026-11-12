# generated: a new holder of the key tablet: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_tablet] remove le.kh_tablet
tag @s add le.kh_tablet
data modify storage last_ember:keys k.tablet.h set from entity @s UUID
