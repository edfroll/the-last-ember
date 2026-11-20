# T-027: the knight spirits of a wave, one by one (recursive), positioned at the grave
execute unless score #nk le.cem matches 1.. run return 0
scoreboard players remove #nk le.cem 1
function last_ember:cemetery/gen/count_spirits
execute if score #sp le.cem matches 8.. run return 0
data modify storage last_ember:cemetery sp.kind set value "knight"
function last_ember:cemetery/place
function last_ember:cemetery/wave_k
