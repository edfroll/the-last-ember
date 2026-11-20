# T-027: the unrest falls by 1 every 3 minutes while no grave is opened
execute unless score #dist le.cem matches 1.. run return 0
scoreboard players operation #tmp le.cem = #gt le.cem
scoreboard players operation #tmp le.cem -= #dlast le.cem
execute unless score #tmp le.cem matches 3600.. run return 0
scoreboard players remove #dist le.cem 1
scoreboard players operation #dlast le.cem = #gt le.cem
function last_ember:cemetery/save
