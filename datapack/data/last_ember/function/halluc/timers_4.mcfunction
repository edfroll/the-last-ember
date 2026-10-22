execute unless score @s le.hk matches -2147483648..2147483647 run function last_ember:halluc/roll_k
execute store success score #fire le.h if score @s le.hk matches ..0
execute if score #fire le.h matches 1 run function last_ember:halluc/knock
execute if score #fire le.h matches 1 run function last_ember:halluc/roll_k
scoreboard players remove @s le.hk 20
