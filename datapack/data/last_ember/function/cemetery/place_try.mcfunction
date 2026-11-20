# T-027: a try of cemetery/place (recursive while it fails, at most 8)
scoreboard players add #try le.cem 1
execute store result storage last_ember:cemetery sp.yaw int 1 run random value 0..359
execute store result storage last_ember:cemetery sp.d int 1 run random value 6..10
function last_ember:cemetery/place_at with storage last_ember:cemetery sp
execute if score #ok le.cem matches 0 if score #try le.cem matches ..7 run function last_ember:cemetery/place_try
