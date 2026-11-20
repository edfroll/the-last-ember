# T-027: the evil spirits of a wave (recursive)
execute unless score #nv le.cem matches 1.. run return 0
scoreboard players remove #nv le.cem 1
function last_ember:cemetery/gen/count_spirits
execute if score #sp le.cem matches 8.. run return 0
data modify storage last_ember:cemetery sp.kind set value "vex"
function last_ember:cemetery/place
function last_ember:cemetery/wave_v
