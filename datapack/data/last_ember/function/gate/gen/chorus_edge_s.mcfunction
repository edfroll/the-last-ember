# generated: chorus guard of the border edge_s (z=1500): as the player the tick after eating a chorus fruit
execute unless score @s le.chx matches -15009..15009 run return 0
execute if score @s le.chz matches ..14999 if score @s le.cnz matches 15010..15410 run return run function last_ember:gate/chorus_back
execute if score @s le.chz matches 15010.. if score @s le.cnz matches 14600..14999 run return run function last_ember:gate/chorus_back
