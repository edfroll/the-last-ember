# generated: as a player in the area of castle_arrows (arrows)
execute unless score #castle_arrows_st le.tr matches 0 run return 0
execute if score #gt le.e < #castle_arrows_cd le.tr run return 0
scoreboard players set #castle_arrows_st le.tr 1
scoreboard players set #castle_arrows_t le.tr 0
scoreboard players operation #castle_arrows_cd le.tr = #gt le.e
scoreboard players add #castle_arrows_cd le.tr 200
execute as @a[x=413,y=155,z=73,dx=2,dy=2,dz=4] run scoreboard players set @s le.tbud 0
execute as @a[x=413,y=155,z=73,dx=2,dy=2,dz=4] run function last_ember:trap/shield
execute positioned 414 155 75 run playsound minecraft:block.dispenser.fail block @a[distance=..16] ~ ~ ~ 0.8 1.4
