scoreboard players remove @s le.wfr 1
execute if entity @s[tag=le.warm] run function last_ember:wound/frost_stop
scoreboard players operation #b le.l = @s le.wfr
scoreboard players operation #b le.l %= #4 le.l
execute if score #b le.l matches 0 run particle minecraft:snowflake ~ ~1.2 ~ 0.35 0.5 0.35 0.01 3
