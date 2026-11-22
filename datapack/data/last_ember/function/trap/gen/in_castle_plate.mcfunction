# generated: as a player in the area of castle_plate (plate)
execute if entity @s[tag=le.race.halfling] run return 0
execute positioned 414 155 75 run playsound minecraft:block.stone_pressure_plate.click_on block @a[distance=..14] ~ ~ ~ 0.8 0.9
execute if score #castle_arrows_st le.tr matches 0 run function last_ember:trap/gen/fire_castle_arrows
