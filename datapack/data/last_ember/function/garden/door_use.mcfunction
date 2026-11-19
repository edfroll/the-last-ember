# T-025: advancement reward: a player used the door of the gardener's house; while the garden is awake it is locked (shut at once)
advancement revoke @s only last_ember:garden/door
execute if score #asleep le.gd matches 1 run return 0
function last_ember:garden/gen/door_shut
title @s actionbar {"text":"Заперто.","color":"gray","italic":true}
