# generated: one tick of castle_arrows
scoreboard players add #castle_arrows_t le.tr 1
execute if score #castle_arrows_t le.tr matches 10 in minecraft:overworld positioned 412.5 156.5 74.5 if entity @p[x=413,y=155,z=73,dx=2,dy=2,dz=4] facing entity @p[x=413,y=155,z=73,dx=2,dy=2,dz=4] eyes run function last_ember:trap/arrow_fire
execute if score #castle_arrows_t le.tr matches 10 in minecraft:overworld positioned 412.5 156.5 79.5 if entity @p[x=413,y=155,z=73,dx=2,dy=2,dz=4] facing entity @p[x=413,y=155,z=73,dx=2,dy=2,dz=4] eyes run function last_ember:trap/arrow_fire
execute if score #castle_arrows_t le.tr matches 20 in minecraft:overworld positioned 412.5 156.5 74.5 if entity @p[x=413,y=155,z=73,dx=2,dy=2,dz=4] facing entity @p[x=413,y=155,z=73,dx=2,dy=2,dz=4] eyes run function last_ember:trap/arrow_fire
execute if score #castle_arrows_t le.tr matches 20 in minecraft:overworld positioned 412.5 156.5 79.5 if entity @p[x=413,y=155,z=73,dx=2,dy=2,dz=4] facing entity @p[x=413,y=155,z=73,dx=2,dy=2,dz=4] eyes run function last_ember:trap/arrow_fire
execute if score #castle_arrows_t le.tr matches 30 in minecraft:overworld positioned 412.5 156.5 74.5 if entity @p[x=413,y=155,z=73,dx=2,dy=2,dz=4] facing entity @p[x=413,y=155,z=73,dx=2,dy=2,dz=4] eyes run function last_ember:trap/arrow_fire
execute if score #castle_arrows_t le.tr matches 30 in minecraft:overworld positioned 412.5 156.5 79.5 if entity @p[x=413,y=155,z=73,dx=2,dy=2,dz=4] facing entity @p[x=413,y=155,z=73,dx=2,dy=2,dz=4] eyes run function last_ember:trap/arrow_fire
execute if score #castle_arrows_t le.tr matches 38.. run scoreboard players set #castle_arrows_st le.tr 0
