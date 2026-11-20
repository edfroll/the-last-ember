# generated: as a player in the area of cem_arrows (arrows)
execute unless score #cem_arrows_st le.tr matches 0 run return 0
execute if score #gt le.e < #cem_arrows_cd le.tr run return 0
scoreboard players set #cem_arrows_st le.tr 1
scoreboard players set #cem_arrows_t le.tr 0
scoreboard players operation #cem_arrows_cd le.tr = #gt le.e
scoreboard players add #cem_arrows_cd le.tr 200
execute as @a[x=239,y=88,z=431,dx=2,dy=3,dz=14] run scoreboard players set @s le.tbud 0
execute as @a[x=239,y=88,z=431,dx=2,dy=3,dz=14] run function last_ember:trap/shield
execute positioned 240 88 438 run playsound minecraft:block.dispenser.fail block @a[distance=..16] ~ ~ ~ 0.8 1.4
