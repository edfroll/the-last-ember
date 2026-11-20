# T-027: every second of the fight: the half (once: 2 knight spirits out of the niches, his speed x1.2); the leash (every player out of
# the hall or dead for 10 s -> back into the sarcophagus at full health, the spirits gone); gone without a kill (2 s) -> laid to rest
execute unless entity @e[type=minecraft:skeleton,tag=le.cmag] run scoreboard players add #mx le.cem 1
execute if entity @e[type=minecraft:skeleton,tag=le.cmag] run scoreboard players set #mx le.cem 0
execute if score #mx le.cem matches 2.. run return run function last_ember:cemetery/mag_rest
execute as @e[type=minecraft:skeleton,tag=le.cmag,limit=1] store result score #mhp le.cem run data get entity @s Health
execute if score #mh le.cem matches 0 if score #mhp le.cem matches ..50 run function last_ember:cemetery/mag_half
function last_ember:cemetery/gen/in_hall
execute if score #c le.cem matches 0 run scoreboard players add #ml le.cem 1
execute if score #c le.cem matches 1.. run scoreboard players set #ml le.cem 0
execute if score #ml le.cem matches 10.. run function last_ember:cemetery/mag_leash
