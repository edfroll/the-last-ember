# generated: the sky guard of the border edge_n (z=-1500): side 16 (low) / 17 (high)
scoreboard players set #side le.gate 0
execute if entity @s[x=-1500,y=-64,z=-1541,dx=3000,dy=400,dz=40] unless entity @s[x=-1500,y=-64,z=-1499,dx=3000,dy=400,dz=40] run scoreboard players set #side le.gate 16
execute if entity @s[x=-1500,y=-64,z=-1499,dx=3000,dy=400,dz=40] unless entity @s[x=-1500,y=-64,z=-1541,dx=3000,dy=400,dz=40] run scoreboard players set #side le.gate 17
execute if score #side le.gate matches 0 run return 0
execute if score @s le.bside matches 16 if score #side le.gate matches 17 if entity @s[y=300,dy=1000] run return run tp @s ~ ~ -1501.5
execute if score @s le.bside matches 17 if score #side le.gate matches 16 if entity @s[y=300,dy=1000] run return run tp @s ~ ~ -1497.5
scoreboard players operation @s le.bside = #side le.gate
