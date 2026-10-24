# 2. Warg (second version: a rig of 8 parts on an invisible wolf of scale 1.9, always angry): it crouches in the bushes, its red eyes glow;
# a howl, then it leaps out, gallops, bites with its own jaw
function last_ember:lab/warg/summon with storage last_ember:lab
execute as @e[tag=le.lnew] run function last_ember:lab/new
execute as @e[tag=le.lab_warg,tag=!le.lposed] run function last_ember:lab/warg/first_pose
