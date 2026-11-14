# generated: the sky guard of the border west_ridge (x=-665): side 2 (low) / 3 (high)
scoreboard players set #side le.gate 0
execute if entity @s[x=-706,y=-64,z=-620,dx=40,dy=400,dz=1270] unless entity @s[x=-664,y=-64,z=-620,dx=40,dy=400,dz=1270] run scoreboard players set #side le.gate 2
execute if entity @s[x=-664,y=-64,z=-620,dx=40,dy=400,dz=1270] unless entity @s[x=-706,y=-64,z=-620,dx=40,dy=400,dz=1270] run scoreboard players set #side le.gate 3
execute if score #side le.gate matches 0 run return 0
execute if score @s le.bside matches 2 if score #side le.gate matches 3 if entity @s[y=300,dy=1000] unless entity @s[z=-194,dz=8,y=-64,dy=400] run return run tp @s -666.5 ~ ~
execute if score @s le.bside matches 3 if score #side le.gate matches 2 if entity @s[y=300,dy=1000] unless entity @s[z=-194,dz=8,y=-64,dy=400] run return run tp @s -662.5 ~ ~
scoreboard players operation @s le.bside = #side le.gate
