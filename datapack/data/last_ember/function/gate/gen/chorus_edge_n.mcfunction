# generated: chorus guard of the border edge_n (z=-1500): as the player the tick after eating a chorus fruit
execute unless score @s le.chx matches -15009..15009 run return 0
execute if score @s le.chz matches ..-15001 if entity @s[x=-1501,y=-64,z=-1499,dx=3002,dy=500,dz=40] run return run function last_ember:gate/chorus_back
execute if score @s le.chz matches -14990.. if entity @s[x=-1501,y=-64,z=-1541,dx=3002,dy=500,dz=40] run return run function last_ember:gate/chorus_back
