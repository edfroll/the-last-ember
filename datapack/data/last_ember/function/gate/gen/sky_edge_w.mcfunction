# generated: the sky guard of the border edge_w (x=-1500): side 12 (low) / 13 (high)
scoreboard players set #side le.gate 0
execute if entity @s[x=-1541,y=-64,z=-1500,dx=40,dy=400,dz=3000] unless entity @s[x=-1499,y=-64,z=-1500,dx=40,dy=400,dz=3000] run scoreboard players set #side le.gate 12
execute if entity @s[x=-1499,y=-64,z=-1500,dx=40,dy=400,dz=3000] unless entity @s[x=-1541,y=-64,z=-1500,dx=40,dy=400,dz=3000] run scoreboard players set #side le.gate 13
execute if score #side le.gate matches 0 run return 0
execute if score @s le.bside matches 12 if score #side le.gate matches 13 if entity @s[y=300,dy=1000] run return run tp @s -1501.5 ~ ~
execute if score @s le.bside matches 13 if score #side le.gate matches 12 if entity @s[y=300,dy=1000] run return run tp @s -1497.5 ~ ~
scoreboard players operation @s le.bside = #side le.gate
