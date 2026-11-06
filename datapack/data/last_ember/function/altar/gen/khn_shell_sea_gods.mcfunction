# generated: a new holder of the key shell_sea_gods: his UUID is stored (reading the player's data only when the holder changes)
tag @a[tag=le.kh_shell_sea_gods] remove le.kh_shell_sea_gods
tag @s add le.kh_shell_sea_gods
data modify storage last_ember:keys k.shell_sea_gods.h set from entity @s UUID
