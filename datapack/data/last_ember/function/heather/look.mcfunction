# T-031: as a resting dead villager: a slight turn of the head (+-12 degrees, never more than 24 off his work)
execute store result score #r le.hv run random value 0..1
execute if score #r le.hv matches 0 if score @s le.hoff matches -12.. run return run function last_ember:heather/look_l
execute if score @s le.hoff matches ..12 run return run function last_ember:heather/look_r
function last_ember:heather/look_l
