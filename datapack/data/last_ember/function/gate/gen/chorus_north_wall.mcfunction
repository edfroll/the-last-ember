# generated: chorus guard of the border north_wall (z=-870): as the player the tick after eating a chorus fruit
execute if score @s le.chx matches -5630..-5561 run return 0
execute unless score @s le.chx matches -15009..15009 run return 0
execute if score @s le.chz matches ..-8701 if score @s le.cnz matches -8690..-8290 run return run function last_ember:gate/chorus_back
execute if score @s le.chz matches -8690.. if score @s le.cnz matches -9100..-8701 run return run function last_ember:gate/chorus_back
