# generated: as/at a player the tick after eating a chorus fruit (gate/chorus_check): every border, then the hold boxes of closed gates
function last_ember:gate/gen/chorus_west_ridge
function last_ember:gate/gen/chorus_watch_ridge
function last_ember:gate/gen/chorus_north_wall
function last_ember:gate/gen/chorus_rift
function last_ember:gate/gen/chorus_east_ridge
function last_ember:gate/gen/chorus_edge_w
function last_ember:gate/gen/chorus_edge_e
function last_ember:gate/gen/chorus_edge_n
function last_ember:gate/gen/chorus_edge_s
execute if score #gate_west_pass le.gate matches 0 if entity @s[x=-664,y=-64,z=-195,dx=15,dy=500,dz=10] unless score @s le.chx matches -6649..-6481 run return run function last_ember:gate/chorus_back
execute if score #gate_west_pass le.gate matches 0 if entity @s[x=-664,y=-64,z=-195,dx=15,dy=500,dz=10] unless score @s le.chz matches -1959..-1841 run return run function last_ember:gate/chorus_back
