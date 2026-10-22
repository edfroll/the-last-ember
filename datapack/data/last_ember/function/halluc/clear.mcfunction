# as a player who has slept: the timers and the shadow are forgotten (our effects were short pulses and run out by themselves)
scoreboard players reset @s le.hw
scoreboard players reset @s le.hsh
scoreboard players reset @s le.hfm
scoreboard players reset @s le.hpu
scoreboard players reset @s le.hk
scoreboard players set @s le.hst 0
execute if score @s le.hid matches 1.. run function last_ember:halluc/shadow_end
