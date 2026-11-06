# generated: the sky guard of the border watch_ridge (z=-620): side 4 (low) / 5 (high)
scoreboard players set #side le.gate 0
execute if entity @s[x=-1500,y=-64,z=-661,dx=835,dy=400,dz=40] unless entity @s[x=-1500,y=-64,z=-619,dx=835,dy=400,dz=40] run scoreboard players set #side le.gate 4
execute if entity @s[x=-1500,y=-64,z=-619,dx=835,dy=400,dz=40] unless entity @s[x=-1500,y=-64,z=-661,dx=835,dy=400,dz=40] run scoreboard players set #side le.gate 5
execute if score #side le.gate matches 0 run return 0
execute if score @s le.bside matches 4 if score #side le.gate matches 5 if entity @s[y=300,dy=1000] unless entity @s[x=-885,dx=10,y=-64,dy=400] run return run tp @s ~ ~ -621.5
execute if score @s le.bside matches 5 if score #side le.gate matches 4 if entity @s[y=300,dy=1000] unless entity @s[x=-885,dx=10,y=-64,dy=400] run return run tp @s ~ ~ -617.5
scoreboard players operation @s le.bside = #side le.gate
