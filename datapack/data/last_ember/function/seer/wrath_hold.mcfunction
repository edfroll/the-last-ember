# every use tick while charging: the charge +1 tick (the full charge at 10 s), the bar, sparks and a rising hum
execute if score @s le.wchg matches 200.. run return 0
scoreboard players add @s le.wchg 1
execute if score @s le.wchg matches 1.. run scoreboard players operation #b le.e = @s le.wchg
scoreboard players operation #b le.e /= #20 le.e
execute store result storage last_ember:seer c.b int 1 run scoreboard players get #b le.e
function last_ember:seer/wrath_bar with storage last_ember:seer c
scoreboard players operation #m le.e = @s le.wchg
scoreboard players operation #m le.e %= #4 le.e
execute if score #m le.e matches 0 run particle minecraft:electric_spark ~ ~2.2 ~ 0.4 0.3 0.4 0.2 3
scoreboard players operation #m le.e = @s le.wchg
scoreboard players operation #m le.e %= #20 le.e
execute if score #m le.e matches 0 run playsound minecraft:block.beacon.ambient player @a[distance=..24] ~ ~ ~ 0.8 1.0
