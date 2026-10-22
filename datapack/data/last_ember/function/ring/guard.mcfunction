# every second, as a halfling: the ring is granted once, a lost one comes back, a record in the storage without a wearer (the player data is older than the storage after a crash) is settled without doubling
execute unless entity @s[tag=le.ringgot] run return run function last_ember:ring/first
function last_ember:ring/key
execute if entity @s[tag=le.ringon] run return 0
function last_ember:ring/stale_m with storage last_ember:ring u
scoreboard players set #rx le.e 0
function last_ember:ring/exists_m with storage last_ember:ring u
execute if score #rx le.e matches 0 run function last_ember:ring/give
