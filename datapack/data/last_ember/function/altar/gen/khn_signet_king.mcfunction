# generated: a new holder of the key signet_king: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_signet_king] remove le.kh_signet_king
tag @s add le.kh_signet_king
data modify storage last_ember:keys k.signet_king.h set from entity @s UUID
