# T-027: the Magister at half health: he calls 2 knight spirits from the niches, his speed x1.2 (once)
scoreboard players set #mh le.cem 1
function last_ember:cemetery/gen/mag_spirits
execute as @e[type=minecraft:skeleton,tag=le.cmag] run attribute @s minecraft:movement_speed modifier add last_ember:cem_mag_half 0.2 add_multiplied_base
execute as @e[type=minecraft:skeleton,tag=le.cmag] at @s run playsound minecraft:entity.skeleton.converted_to_stray hostile @a[distance=..32] ~ ~ ~ 1.5 0.5
