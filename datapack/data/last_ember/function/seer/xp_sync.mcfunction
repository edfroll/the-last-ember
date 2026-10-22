# as a player, after the datapack itself gave or took experience (ash trail, urn, death): the new total is the base, nothing is doubled
function last_ember:seer/xp_total
scoreboard players operation @s le.xptot = #xt le.e
