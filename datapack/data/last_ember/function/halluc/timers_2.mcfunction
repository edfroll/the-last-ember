execute unless score @s le.hsh matches -2147483648..2147483647 run function last_ember:halluc/roll_sh
execute store success score #fire le.h if score @s le.hsh matches ..0
execute if score #fire le.h matches 1 run function last_ember:halluc/shadow
execute if score #fire le.h matches 1 run function last_ember:halluc/roll_sh
scoreboard players remove @s le.hsh 20
execute unless score @s le.hfm matches -2147483648..2147483647 run function last_ember:halluc/roll_fm
execute store success score #fire le.h if score @s le.hfm matches ..0
execute if score #fire le.h matches 1 run function last_ember:halluc/fake_mob
execute if score #fire le.h matches 1 run function last_ember:halluc/roll_fm
scoreboard players remove @s le.hfm 20
