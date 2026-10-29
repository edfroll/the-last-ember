# the Leshy of the Pied Wood (Р1): the leshy rig with a glowing hollow in its back (grove_*), stands as a tree until it is touched
$data modify storage last_ember:contracts sp set value {id:"$(id)",n:$(n),hp:$(hp),max:$(max),hpm:$(hpm),dmg:$(dmg),arm:$(arm)}
data modify storage last_ember:contracts sp.parts set from storage last_ember:lab grove_parts
function last_ember:contract/k/grove_leshy/summon with storage last_ember:contracts sp
execute as @e[tag=le.cnewm] run function last_ember:contract/k/new with storage last_ember:contracts sp
execute as @e[tag=le.lab_leshy,tag=le.contract,tag=!le.lposed] run function last_ember:contract/k/grove_leshy/first_pose
