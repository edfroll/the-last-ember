# as/at the clicked trail interaction: everything goes to the clicker (owner or teammate)
data remove entity @s interaction
execute store result storage last_ember:dt o.id int 1 run scoreboard players get @s le.tid
scoreboard players operation #k le.e = @s le.tid
function last_ember:ash/collect_m with storage last_ember:dt o
execute as @a if score @s le.ash = #k le.e run scoreboard players set @s le.ash 0
execute as @e[tag=le.ash] if score @s le.tid = #k le.e at @s run function last_ember:ash/remove_entity
