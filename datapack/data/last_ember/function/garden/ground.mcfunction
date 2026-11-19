# T-025: as the candidate marker, positioned from 6 above down to 10 below: the first spot with 2 free blocks over solid ground (not
# leaves, water or lava) -> the marker goes there, #gok 1
scoreboard players add #gs le.gd 1
execute if score #gs le.gd matches 17.. run return 0
execute if block ~ ~ ~ #last_ember:garden_air if block ~ ~1 ~ #last_ember:garden_air unless block ~ ~-1 ~ #last_ember:garden_air unless block ~ ~-1 ~ #minecraft:leaves unless block ~ ~-1 ~ minecraft:water unless block ~ ~-1 ~ minecraft:lava run return run function last_ember:garden/ground_ok
execute positioned ~ ~-1 ~ run function last_ember:garden/ground
