# generated: the sky guard of the border edge_e (x=1500): side 14 (low) / 15 (high)
scoreboard players set #side le.gate 0
execute if entity @s[x=1459,y=-64,z=-1500,dx=40,dy=400,dz=3000] unless entity @s[x=1501,y=-64,z=-1500,dx=40,dy=400,dz=3000] run scoreboard players set #side le.gate 14
execute if entity @s[x=1501,y=-64,z=-1500,dx=40,dy=400,dz=3000] unless entity @s[x=1459,y=-64,z=-1500,dx=40,dy=400,dz=3000] run scoreboard players set #side le.gate 15
execute if score #side le.gate matches 0 run return 0
execute if score @s le.bside matches 14 if score #side le.gate matches 15 if entity @s[y=300,dy=1000] run return run tp @s 1498.5 ~ ~
execute if score @s le.bside matches 15 if score #side le.gate matches 14 if entity @s[y=300,dy=1000] run return run tp @s 1502.5 ~ ~
scoreboard players operation @s le.bside = #side le.gate
