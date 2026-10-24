# on the ground: back to the neutral shape after a landing squash (3 ticks) or a lunge (5 ticks); a gathering keeps its own shape
scoreboard players remove @s le.llook 1
execute if score @s le.lsq matches 6 run return 0
execute if score @s le.lsq matches 2 if score @s le.llook matches ..0 run function last_ember:lab/womb/to_neutral
execute if score @s le.lsq matches 5 if score @s le.llook matches ..0 run function last_ember:lab/womb/to_neutral
execute if score @s le.lsq matches 0..1 run function last_ember:lab/womb/to_neutral
