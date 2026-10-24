# the claws are open for a bite: they snap shut after 4 ticks
scoreboard players remove @s le.lan 1
execute if score @s le.lan matches 0 run function last_ember:lab/gen/cent_claw_snap
