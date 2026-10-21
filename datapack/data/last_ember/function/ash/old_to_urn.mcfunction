# as a player who dies again with an unclaimed trail: that trail goes to its urn
execute store result storage last_ember:dt o.id int 1 run scoreboard players get @s le.ash
scoreboard players set @s le.ash 0
function last_ember:ash/old_to_urn_m with storage last_ember:dt o
