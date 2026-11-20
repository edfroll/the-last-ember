# T-027: every second while somebody is near: the crypt door, the sarcophagus / chest 2 / the exit after the victory, the seal in the
# sarcophagus, the Magister (0 asleep -> a player within 10 of the sarcophagus at #q 3 -> 3 rising 2 s -> 1 the fight -> 2 laid to rest)
function last_ember:cemetery/gen/door_set
function last_ember:cemetery/gen/crypt_sync
execute if score #ss le.cem matches 1 unless entity @e[type=minecraft:item_display,tag=le.csealdisp] run function last_ember:cemetery/gen/mag_seal
execute if score #mg le.cem matches 0 if score #q le.cem matches 3 run function last_ember:cemetery/mag_wake
execute if score #mg le.cem matches 3 run function last_ember:cemetery/mag_rising
execute if score #mg le.cem matches 1 run function last_ember:cemetery/mag_fight
