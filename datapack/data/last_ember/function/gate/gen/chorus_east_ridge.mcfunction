# generated: chorus guard of the border east_ridge (x=665): as the player the tick after eating a chorus fruit
execute unless score @s le.chz matches -8709..6509 run return 0
execute if score @s le.chx matches ..6649 if entity @s[x=666,y=-64,z=-871,dx=40,dy=500,dz=1522] run return run function last_ember:gate/chorus_back
execute if score @s le.chx matches 6660.. if entity @s[x=624,y=-64,z=-871,dx=40,dy=500,dz=1522] run return run function last_ember:gate/chorus_back
