scoreboard players set @s le.satcd 0
execute store result score #food le.e run data get entity @s foodLevel
execute if score #food le.e matches ..19 run effect give @s minecraft:saturation 1 0 true
