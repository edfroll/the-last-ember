execute unless score @s le.hpu matches -2147483648..2147483647 run function last_ember:halluc/roll_pu
execute store success score #fire le.h if score @s le.hpu matches ..0
execute if score #fire le.h matches 1 run function last_ember:halluc/pulse
execute if score #fire le.h matches 1 run function last_ember:halluc/roll_pu
scoreboard players remove @s le.hpu 20
