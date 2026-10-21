# as a player: onto a free bed of the Cell (the first one nobody lies on), respawn point there, darkness and a quiet sound
execute unless entity @a[x=-3,y=57,z=-9,dx=0,dy=3,dz=1] run return run function last_ember:char/to_bed_0
execute unless entity @a[x=0,y=57,z=-9,dx=0,dy=3,dz=1] run return run function last_ember:char/to_bed_1
function last_ember:char/to_bed_2
