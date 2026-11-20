# generated: as a player in the area of cem_plate_2 (plate)
execute if entity @s[tag=le.race.halfling] run return 0
execute positioned 241 89 440 run playsound minecraft:block.stone_pressure_plate.click_on block @a[distance=..14] ~ ~ ~ 0.8 0.9
execute if score #cem_arrows_st le.tr matches 0 run function last_ember:trap/gen/fire_cem_arrows
