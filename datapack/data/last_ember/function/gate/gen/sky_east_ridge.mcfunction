# generated: the sky guard of the border east_ridge (x=665): side 10 (low) / 11 (high)
scoreboard players set #side le.gate 0
execute if entity @s[x=624,y=-64,z=-870,dx=40,dy=400,dz=1520] unless entity @s[x=666,y=-64,z=-870,dx=40,dy=400,dz=1520] run scoreboard players set #side le.gate 10
execute if entity @s[x=666,y=-64,z=-870,dx=40,dy=400,dz=1520] unless entity @s[x=624,y=-64,z=-870,dx=40,dy=400,dz=1520] run scoreboard players set #side le.gate 11
execute if score #side le.gate matches 0 run return 0
execute if score @s le.bside matches 10 if score #side le.gate matches 11 if entity @s[y=300,dy=1000] run return run tp @s 663.5 ~ ~
execute if score @s le.bside matches 11 if score #side le.gate matches 10 if entity @s[y=300,dy=1000] run return run tp @s 667.5 ~ ~
scoreboard players operation @s le.bside = #side le.gate
