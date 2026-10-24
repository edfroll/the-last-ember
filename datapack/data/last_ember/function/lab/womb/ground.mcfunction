# on the ground: squash (3 ticks) -> neutral (6 ticks) -> gathering until the jump
scoreboard players remove @s le.lfd 1
execute if score @s le.lsq matches 2 if score @s le.lfd matches ..0 run function last_ember:lab/womb/to_neutral
execute if score @s le.lsq matches 3 if score @s le.lfd matches ..0 run function last_ember:lab/womb/to_charge
execute if score @s le.lsq matches 0..1 run function last_ember:lab/womb/to_neutral
