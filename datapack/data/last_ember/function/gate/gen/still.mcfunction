# generated: as a player in transfer (le.scw = code): left the trigger -> cancelled
execute if score @s le.scw matches 2 in minecraft:overworld positioned 28.8 103 -27.8 unless entity @s[distance=..2.5] run return 0
execute if score @s le.scw matches 3 in minecraft:overworld unless entity @s[x=-387,y=111,z=-198,dx=2,dy=2,dz=4] run return 0
return 1
