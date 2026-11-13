# generated: chorus guard of the border north_wall (z=-870): as the player the tick after eating a chorus fruit
execute if score @s le.chx matches -5630..-5561 run return 0
execute unless score @s le.chx matches -15009..15009 run return 0
execute if score @s le.chz matches ..-8701 if entity @s[x=-1501,y=-64,z=-869,dx=3002,dy=500,dz=40] run return run function last_ember:gate/chorus_back
execute if score @s le.chz matches -8690.. if entity @s[x=-1501,y=-64,z=-911,dx=3002,dy=500,dz=40] run return run function last_ember:gate/chorus_back
