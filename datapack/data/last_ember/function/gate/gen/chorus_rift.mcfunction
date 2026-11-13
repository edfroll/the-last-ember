# generated: chorus guard of the border rift (z=650): as the player the tick after eating a chorus fruit
execute if score #gate_south_bridge le.gate matches 1 if score @s le.chx matches -20..29 run return 0
execute unless score @s le.chx matches -15009..15009 run return 0
execute if score @s le.chz matches ..6499 if entity @s[x=-1501,y=-64,z=651,dx=3002,dy=500,dz=40] run return run function last_ember:gate/chorus_back
execute if score @s le.chz matches 6510.. if entity @s[x=-1501,y=-64,z=609,dx=3002,dy=500,dz=40] run return run function last_ember:gate/chorus_back
