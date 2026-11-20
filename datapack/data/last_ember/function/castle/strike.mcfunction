# T-028: the strike (as/at the player): off a boat, the damage leaves 1 heart (health + absorption - 2, our damage type ignores armour,
# Protection, Resistance, shields), the wind from the palm of the nearer colossus, then the flight to a knock point of its own
tag @s remove le.cwake
ride @s dismount
scoreboard players operation @s le.ck = #kn le.cas
scoreboard players add #kn le.cas 1
scoreboard players operation #kn le.cas %= #3 le.cas
execute if score @s le.ck matches 0 run function last_ember:castle/gen/knock_0
execute if score @s le.ck matches 1 run function last_ember:castle/gen/knock_1
execute if score @s le.ck matches 2 run function last_ember:castle/gen/knock_2
execute store result score @s le.csx run data get entity @s Pos[0] 100
execute store result score @s le.csy run data get entity @s Pos[1] 100
execute store result score @s le.csz run data get entity @s Pos[2] 100
execute store result score #h le.cas run data get entity @s Health 100
execute store result score #a le.cas run data get entity @s AbsorptionAmount 100
scoreboard players operation #h le.cas += #a le.cas
scoreboard players remove #h le.cas 200
execute if score #h le.cas matches 1.. store result storage last_ember:castle hit.d float 0.01 run scoreboard players get #h le.cas
execute if score #h le.cas matches 1.. run function last_ember:castle/hurt with storage last_ember:castle hit
execute if score @s le.csz matches ..-3350 run function last_ember:castle/gen/strike_n
execute if score @s le.csz matches -3349.. run function last_ember:castle/gen/strike_s
particle minecraft:gust_emitter_large ~ ~1 ~ 0 0 0 0 1 force @a[distance=..96]
playsound minecraft:entity.wind_charge.wind_burst player @a[distance=..48] ~ ~ ~ 2 0.7
playsound minecraft:entity.player.hurt_sweet_berry_bush player @s ~ ~ ~ 1 0.5
scoreboard players set #eyes le.cas 1
scoreboard players operation #eyet le.cas = #gt le.cas
scoreboard players add #eyet le.cas 60
tag @s add le.cfly
scoreboard players set @s le.cf 0
