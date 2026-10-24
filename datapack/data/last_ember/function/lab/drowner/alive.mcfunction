# not a zombie: water drips off it; now and then it stops dead and its head jerks, then it throws itself at the prey; the roar of the swing when it reaches somebody (the blow itself is vanilla: the wound by the advancement lab/hit_drowner)
scoreboard players operation #t4 le.l = #gt le.l
scoreboard players operation #t4 le.l %= #4 le.l
execute if score #t4 le.l matches 0 run particle minecraft:dripping_water ~ ~1.3 ~ 0.25 0.45 0.25 0 2
execute if score #t4 le.l matches 2 run particle minecraft:falling_water ~ ~0.9 ~ 0.25 0.3 0.25 0 1
scoreboard players remove @s le.lfd 1
execute if score @s le.lfr matches 1.. run return run function last_ember:lab/drowner/twitch
scoreboard players remove @s le.lan 1
execute if score @s le.lan matches ..0 if entity @a[distance=3.5..14,gamemode=!spectator,gamemode=!creative] run return run function last_ember:lab/drowner/twitch_start
execute if score @s le.lfd matches ..0 if entity @s[nbt={OnGround:1b}] if entity @a[distance=3.5..8,gamemode=!spectator,gamemode=!creative] unless entity @a[distance=..3.5,gamemode=!spectator,gamemode=!creative] run function last_ember:lab/drowner/lunge
execute if score @s le.lcd matches ..0 if entity @a[distance=..2.6,gamemode=!spectator,gamemode=!creative] run function last_ember:lab/drowner/swing
execute if score @s le.lst matches 80.. run function last_ember:lab/drowner/step
