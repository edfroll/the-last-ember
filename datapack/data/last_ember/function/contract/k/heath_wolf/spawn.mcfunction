# the heath wolf (Р1): the warg rig with its own look (heath_*), an invisible wolf of scale 1.9 (macro: the contract args)
$data modify storage last_ember:contracts sp set value {id:"$(id)",n:$(n),hp:$(hp),max:$(max),hpm:$(hpm),dmg:$(dmg),arm:$(arm)}
data modify storage last_ember:contracts sp.parts set from storage last_ember:lab heath_parts
function last_ember:contract/k/heath_wolf/summon with storage last_ember:contracts sp
execute as @e[tag=le.cnewm] run function last_ember:contract/k/new with storage last_ember:contracts sp
execute as @e[tag=le.lab_warg,tag=le.contract,tag=!le.lposed] run function last_ember:lab/warg/first_pose
