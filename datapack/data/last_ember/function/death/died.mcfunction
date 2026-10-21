# as the player who just died (still on the death screen; keep_inventory kept everything).
# Stays: equipment (armor, off-hand), the selected hotbar slot, the Ember, items with custom_data le_keep / le_key. Everything else and XP -> trail.
scoreboard players set @s le.deaths 0
data modify storage last_ember:dt d set from entity @s LastDeathLocation
data modify storage last_ember:dt dim set from storage last_ember:dt d.dimension
execute store result score #x le.e run data get storage last_ember:dt d.pos[0]
execute store result score #y le.e run data get storage last_ember:dt d.pos[1]
execute store result score #z le.e run data get storage last_ember:dt d.pos[2]
data modify storage last_ember:dt inv set from entity @s Inventory
execute store result storage last_ember:dt sel int 1 run data get entity @s SelectedItemSlot
function last_ember:death/keep_selected with storage last_ember:dt
data remove storage last_ember:dt inv[{components:{"minecraft:custom_data":{le_ember:1b}}}]
data remove storage last_ember:dt inv[{components:{"minecraft:custom_data":{le_keep:1b}}}]
data remove storage last_ember:dt inv[{components:{"minecraft:custom_data":{le_key:1b}}}]
execute store result storage last_ember:dt lv int 1 run xp query @s levels
execute store result storage last_ember:dt pts int 1 run xp query @s points
xp set @s 0 levels
xp set @s 0 points
data modify storage last_ember:dt rm set from storage last_ember:dt inv
function last_ember:death/remove_items
# a trail left from the previous death goes to its urn
execute if score @s le.ash matches 1.. run function last_ember:ash/old_to_urn
execute unless data storage last_ember:dt inv[0] if data storage last_ember:dt {lv:0,pts:0} run return 0
function last_ember:ash/create
