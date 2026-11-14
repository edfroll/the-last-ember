# generated from death/regions.txt: #rg le.el = the region of this mob (0..6, 7 = Nether, -1 = none); the first matching line wins
scoreboard players set #rg le.el -1
execute if score #rg le.el matches -1 if dimension minecraft:overworld if entity @s[x=-665,y=-64,z=600,dx=1330,dy=384,dz=50] run scoreboard players set #rg le.el 1
execute if score #rg le.el matches -1 if dimension minecraft:overworld if entity @s[x=-665,y=-64,z=-870,dx=1330,dy=84,dz=1520] run scoreboard players set #rg le.el 5
execute if score #rg le.el matches -1 if dimension minecraft:overworld if entity @s[x=-200,y=21,z=-200,dx=400,dy=299,dz=400] run scoreboard players set #rg le.el 0
execute if score #rg le.el matches -1 if dimension minecraft:overworld if entity @s[x=-665,y=-64,z=-870,dx=1330,dy=384,dz=1520] run scoreboard players set #rg le.el 1
execute if score #rg le.el matches -1 if dimension minecraft:overworld if entity @s[x=-1500,y=-64,z=-830,dx=835,dy=384,dz=210] run scoreboard players set #rg le.el 1
execute if score #rg le.el matches -1 if dimension minecraft:overworld if entity @s[x=-1500,y=-64,z=-620,dx=835,dy=384,dz=1270] run scoreboard players set #rg le.el 2
execute if score #rg le.el matches -1 if dimension minecraft:overworld if entity @s[x=-1500,y=-64,z=-1500,dx=3000,dy=384,dz=629] run scoreboard players set #rg le.el 3
execute if score #rg le.el matches -1 if dimension minecraft:overworld if entity @s[x=-1500,y=-64,z=651,dx=3000,dy=384,dz=849] run scoreboard players set #rg le.el 4
execute if score #rg le.el matches -1 if dimension minecraft:overworld if entity @s[x=666,y=-64,z=-870,dx=834,dy=384,dz=1520] run scoreboard players set #rg le.el 6
execute if score #rg le.el matches -1 if dimension minecraft:the_nether if entity @s[x=-30000000,y=-64,z=-30000000,dx=60000000,dy=384,dz=60000000] run scoreboard players set #rg le.el 7
