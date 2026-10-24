# 4. Leshy (a rig of 6 item_display parts on an invisible husk of scale 1.6): it grows out of the ground
function last_ember:lab/leshy/summon with storage last_ember:lab
execute as @e[tag=le.lnew] run function last_ember:lab/new
execute as @e[tag=le.lab_leshy,tag=!le.lposed] run function last_ember:lab/leshy/first_pose
