# generated: as/at a player in a border strip (tag le.zf.border), every 5 ticks: the side of each border axis is remembered
# (le.bside = 2*border+side); crossing an axis outside a gap high above the world is undone
execute if entity @s[x=-705,y=-64,z=-620,dx=80,dy=400,dz=1270] run function last_ember:gate/gen/sky_west_ridge
execute if entity @s[x=-1500,y=-64,z=-660,dx=835,dy=400,dz=80] run function last_ember:gate/gen/sky_watch_ridge
execute if entity @s[x=-1500,y=-64,z=-910,dx=3000,dy=400,dz=80] run function last_ember:gate/gen/sky_north_wall
execute if entity @s[x=-1500,y=-64,z=610,dx=3000,dy=400,dz=80] run function last_ember:gate/gen/sky_rift
execute if entity @s[x=625,y=-64,z=-870,dx=80,dy=400,dz=1520] run function last_ember:gate/gen/sky_east_ridge
execute if entity @s[x=-1540,y=-64,z=-1500,dx=80,dy=400,dz=3000] run function last_ember:gate/gen/sky_edge_w
execute if entity @s[x=1460,y=-64,z=-1500,dx=80,dy=400,dz=3000] run function last_ember:gate/gen/sky_edge_e
execute if entity @s[x=-1500,y=-64,z=-1540,dx=3000,dy=400,dz=80] run function last_ember:gate/gen/sky_edge_n
execute if entity @s[x=-1500,y=-64,z=1460,dx=3000,dy=400,dz=80] run function last_ember:gate/gen/sky_edge_s
