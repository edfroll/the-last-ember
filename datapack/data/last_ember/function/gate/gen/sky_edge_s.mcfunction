# generated: the sky guard of the border edge_s (z=1500): side 18 (low) / 19 (high)
scoreboard players set #side le.gate 0
execute if entity @s[x=-1500,y=-64,z=1459,dx=3000,dy=400,dz=40] unless entity @s[x=-1500,y=-64,z=1501,dx=3000,dy=400,dz=40] run scoreboard players set #side le.gate 18
execute if entity @s[x=-1500,y=-64,z=1501,dx=3000,dy=400,dz=40] unless entity @s[x=-1500,y=-64,z=1459,dx=3000,dy=400,dz=40] run scoreboard players set #side le.gate 19
execute if score #side le.gate matches 0 run return 0
execute if score @s le.bside matches 18 if score #side le.gate matches 19 if entity @s[y=300,dy=1000] run return run tp @s ~ ~ 1498.5
execute if score @s le.bside matches 19 if score #side le.gate matches 18 if entity @s[y=300,dy=1000] run return run tp @s ~ ~ 1502.5
scoreboard players operation @s le.bside = #side le.gate
