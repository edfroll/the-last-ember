# every tick, as a seer: any growth of the total experience is doubled (the second half is added right away and counted in, so it is not doubled again)
function last_ember:seer/xp_total
execute unless score @s le.xptot matches 0.. run return run scoreboard players operation @s le.xptot = #xt le.e
scoreboard players operation #xd le.e = #xt le.e
scoreboard players operation #xd le.e -= @s le.xptot
execute if score #xd le.e matches 1.. run function last_ember:seer/xp_double
scoreboard players operation @s le.xptot = #xt le.e
