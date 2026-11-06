# generated: the sky guard of the border rift (z=650): side 8 (low) / 9 (high)
scoreboard players set #side le.gate 0
execute if entity @s[x=-1500,y=-64,z=609,dx=3000,dy=400,dz=40] unless entity @s[x=-1500,y=-64,z=651,dx=3000,dy=400,dz=40] run scoreboard players set #side le.gate 8
execute if entity @s[x=-1500,y=-64,z=651,dx=3000,dy=400,dz=40] unless entity @s[x=-1500,y=-64,z=609,dx=3000,dy=400,dz=40] run scoreboard players set #side le.gate 9
execute if score #side le.gate matches 0 run return 0
execute if score @s le.bside matches 8 if score #side le.gate matches 9 if entity @s[y=300,dy=1000] unless entity @s[x=-2,dx=4,y=-64,dy=400] run return run tp @s ~ ~ 648.5
execute if score @s le.bside matches 9 if score #side le.gate matches 8 if entity @s[y=300,dy=1000] unless entity @s[x=-2,dx=4,y=-64,dy=400] run return run tp @s ~ ~ 652.5
scoreboard players operation @s le.bside = #side le.gate
