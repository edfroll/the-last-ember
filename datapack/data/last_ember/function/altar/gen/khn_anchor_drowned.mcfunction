# generated: a new holder of the key anchor_drowned: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_anchor_drowned] remove le.kh_anchor_drowned
tag @s add le.kh_anchor_drowned
data modify storage last_ember:keys k.anchor_drowned.h set from entity @s UUID
