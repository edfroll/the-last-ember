scoreboard players remove @s le.wmu 1
scoreboard players operation #b le.l = @s le.wmu
scoreboard players operation #b le.l %= #80 le.l
execute if score #b le.l matches 40 run function last_ember:halluc/whisper
execute if score @s le.wmu matches 330 run function last_ember:halluc/shadow
execute if score @s le.wmu matches 130 run function last_ember:halluc/shadow
