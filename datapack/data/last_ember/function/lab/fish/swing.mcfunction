scoreboard players set @s le.lcd 24
function last_ember:lab/s/fish_swing
execute if entity @s[tag=le.cent] run function last_ember:lab/gen/cent_claw_open
execute if entity @s[tag=le.cent] run scoreboard players set @s le.lan 4
