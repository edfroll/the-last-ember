# generated: the sky guard of the border north_wall (z=-870): side 6 (low) / 7 (high)
scoreboard players set #side le.gate 0
execute if entity @s[x=-1500,y=-64,z=-911,dx=3000,dy=400,dz=40] unless entity @s[x=-1500,y=-64,z=-869,dx=3000,dy=400,dz=40] run scoreboard players set #side le.gate 6
execute if entity @s[x=-1500,y=-64,z=-869,dx=3000,dy=400,dz=40] unless entity @s[x=-1500,y=-64,z=-911,dx=3000,dy=400,dz=40] run scoreboard players set #side le.gate 7
execute if score #side le.gate matches 0 run return 0
execute if score @s le.bside matches 6 if score #side le.gate matches 7 if entity @s[y=300,dy=1000] unless entity @s[x=-563,dx=6,y=-64,dy=400] run return run tp @s ~ ~ -871.5
execute if score @s le.bside matches 7 if score #side le.gate matches 6 if entity @s[y=300,dy=1000] unless entity @s[x=-563,dx=6,y=-64,dy=400] run return run tp @s ~ ~ -867.5
scoreboard players operation @s le.bside = #side le.gate
