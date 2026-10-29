# the womb of the Crooked Bogs (Р1): the lab womb (an invisible slime of size 4 + the blob); splits at half health, weak on dry land
$data modify storage last_ember:contracts sp set value {id:"$(id)",n:$(n),hp:$(hp),max:$(max),hpm:$(hpm),dmg:$(dmg),arm:$(arm)}
function last_ember:contract/k/bog_womb/summon with storage last_ember:contracts sp
execute as @e[tag=le.cnewm] run function last_ember:contract/k/new with storage last_ember:contracts sp
