# generated: chorus guard of the border rift (z=650): as the player the tick after eating a chorus fruit
execute if score #gate_south_bridge le.gate matches 1 if score @s le.chx matches -20..29 run return 0
execute unless score @s le.chx matches -15009..15009 run return 0
execute if score @s le.chz matches ..6499 if score @s le.cnz matches 6510..6910 run return run function last_ember:gate/chorus_back
execute if score @s le.chz matches 6510.. if score @s le.cnz matches 6100..6499 run return run function last_ember:gate/chorus_back
