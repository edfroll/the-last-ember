# generated: chorus guard of the border edge_w (x=-1500): as the player the tick after eating a chorus fruit
execute unless score @s le.chz matches -15009..15009 run return 0
execute if score @s le.chx matches ..-15001 if entity @s[x=-1499,y=-64,z=-1501,dx=40,dy=500,dz=3002] run return run function last_ember:gate/chorus_back
execute if score @s le.chx matches -14990.. if entity @s[x=-1541,y=-64,z=-1501,dx=40,dy=500,dz=3002] run return run function last_ember:gate/chorus_back
