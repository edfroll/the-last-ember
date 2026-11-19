# T-025: advancement reward: a player right-clicked the Tear of the Creaker on its pedestal
advancement revoke @s only last_ember:garden/key
execute unless score #key le.gd matches 1 run return 0
function last_ember:garden/key_take
