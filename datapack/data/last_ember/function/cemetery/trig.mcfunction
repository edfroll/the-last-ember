# T-027: a button of the keeper's window (trigger le.ctrig: 1 take the shovel, 2 the absolution, 9 the swords): only next to the keeper
scoreboard players operation #k le.cem = @s le.ctrig
scoreboard players set @s le.ctrig 0
scoreboard players enable @s le.ctrig
execute unless entity @e[type=minecraft:villager,tag=le.ckeeper,distance=..8] run return 0
execute if score #k le.cem matches 9 run return run dialog show @s last_ember:cemetery/swords
execute if score #k le.cem matches 1 run return run function last_ember:cemetery/take_shovel
execute if score #k le.cem matches 2 run return run function last_ember:cemetery/absolve
