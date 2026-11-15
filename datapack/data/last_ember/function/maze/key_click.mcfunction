# T-024: advancement reward: a player right-clicked the key on its pedestal
advancement revoke @s only last_ember:maze/click
execute unless score #key le.mz matches 1 run return 0
function last_ember:maze/key_take
