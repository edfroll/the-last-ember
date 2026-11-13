# generated: chorus guard of the border watch_ridge (z=-620): as the player the tick after eating a chorus fruit
execute if score @s le.chx matches -8850..-8741 run return 0
execute unless score @s le.chx matches -15009..-6641 run return 0
execute if score @s le.chz matches ..-6201 if entity @s[x=-1501,y=-64,z=-619,dx=837,dy=500,dz=40] run return run function last_ember:gate/chorus_back
execute if score @s le.chz matches -6190.. if entity @s[x=-1501,y=-64,z=-661,dx=837,dy=500,dz=40] run return run function last_ember:gate/chorus_back
