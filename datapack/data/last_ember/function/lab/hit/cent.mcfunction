# a hit by the scolopendra: the claws (its own melee attack) poison — wound/venom; the blow of the body (lab/cent/slam_hit, tag le.noven) does not
advancement revoke @s only last_ember:lab/hit_cent
execute if entity @s[tag=le.noven] run return 0
function last_ember:wound/venom
