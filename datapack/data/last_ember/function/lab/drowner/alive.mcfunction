# the roar of the swing when it reaches somebody (the blow itself is the vanilla one: arms, the hit, the wound by the advancement lab/hit_drowner)
execute if score @s le.lcd matches ..0 if entity @a[distance=..2.6,gamemode=!spectator,gamemode=!creative] run function last_ember:lab/drowner/swing
execute if score @s le.lst matches 80.. run function last_ember:lab/drowner/step
