# T-027: macro x, y, z (the grave): the answer of the spirits to an opened grave, by the unrest after it (+1 knight at night), never more
# than 8 spirits at the cemetery; they come up 6..10 blocks from the grave on solid ground with soul fire and a sound from under the earth
scoreboard players set #nk le.cem 0
scoreboard players set #nv le.cem 0
execute if score #dist le.cem matches 1..3 run scoreboard players set #nk le.cem 1
execute if score #dist le.cem matches 4..7 run scoreboard players set #nk le.cem 2
execute if score #dist le.cem matches 8..11 run scoreboard players set #nk le.cem 2
execute if score #dist le.cem matches 8..11 run scoreboard players set #nv le.cem 1
execute if score #dist le.cem matches 12.. run scoreboard players set #nk le.cem 3
execute if score #dist le.cem matches 12.. run scoreboard players set #nv le.cem 2
execute if predicate last_ember:night run scoreboard players add #nk le.cem 1
$execute positioned $(x) $(y) $(z) run particle minecraft:soul ~0.5 ~0.5 ~0.5 3 0.6 3 0.05 60 force
$execute positioned $(x) $(y) $(z) run playsound minecraft:ambient.soul_sand_valley.mood hostile @a[distance=..32] ~ ~ ~ 1.5 0.6
$execute positioned $(x) $(y) $(z) run playsound minecraft:block.soul_soil.break hostile @a[distance=..24] ~ ~ ~ 1.2 0.5
$execute positioned $(x).5 $(y) $(z).5 run function last_ember:cemetery/wave_k
$execute positioned $(x).5 $(y) $(z).5 run function last_ember:cemetery/wave_v
