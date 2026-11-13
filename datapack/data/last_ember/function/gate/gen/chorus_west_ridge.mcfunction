# generated: chorus guard of the border west_ridge (x=-665): as the player the tick after eating a chorus fruit
execute if score #gate_west_pass le.gate matches 1 if score @s le.chz matches -1940..-1851 run return 0
execute unless score @s le.chz matches -6209..6509 run return 0
execute if score @s le.chx matches ..-6651 if entity @s[x=-664,y=-64,z=-621,dx=40,dy=500,dz=1272] run return run function last_ember:gate/chorus_back
execute if score @s le.chx matches -6640.. if entity @s[x=-706,y=-64,z=-621,dx=40,dy=500,dz=1272] run return run function last_ember:gate/chorus_back
