# generated: traders whose chunk is loaded are put in place once (every second)
execute if score #trader_smith_bl le.tr matches 0 in minecraft:overworld if loaded 58 101 27 run function last_ember:trader/gen/build_smith
execute if score #trader_witch_mother_bl le.tr matches 0 in minecraft:overworld if loaded -401 139 339 run function last_ember:trader/gen/build_witch_mother
execute if score #trader_witch_maiden_bl le.tr matches 0 in minecraft:overworld if loaded -380 139 331 run function last_ember:trader/gen/build_witch_maiden
execute if score #trader_witch_crone_bl le.tr matches 0 in minecraft:overworld if loaded -380 139 348 run function last_ember:trader/gen/build_witch_crone
