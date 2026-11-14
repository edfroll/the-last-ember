# generated: chorus guard of the border edge_w (x=-1500): as the player the tick after eating a chorus fruit
execute unless score @s le.chz matches -15009..15009 run return 0
execute if score @s le.chx matches ..-15001 if score @s le.cnx matches -14990..-14590 run return run function last_ember:gate/chorus_back
execute if score @s le.chx matches -14990.. if score @s le.cnx matches -15400..-15001 run return run function last_ember:gate/chorus_back
