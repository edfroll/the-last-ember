scoreboard players set #dx le.alt -390
scoreboard players set #dz le.alt 340
scoreboard players operation #dx le.alt -= #px le.alt
scoreboard players operation #dz le.alt -= #pz le.alt
scoreboard players operation #dx le.alt *= #dx le.alt
scoreboard players operation #dz le.alt *= #dz le.alt
scoreboard players operation #dx le.alt += #dz le.alt
execute if score #dx le.alt < #best le.alt run function last_ember:altar/gen/take_crown_witches
