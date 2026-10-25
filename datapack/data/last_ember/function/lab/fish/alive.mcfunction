# rearing: the carrier is frozen (no AI: it must not turn, or the lifted head and the risen body part ways)
execute if score @s le.lfr matches 1.. run return run function last_ember:lab/cent/tick
function last_ember:lab/turn
execute if entity @s[tag=le.cent] run function last_ember:lab/cent/tick
# now and then, when its prey is 3-5 blocks away, it rears up and strikes with its whole body
scoreboard players remove @s le.llook 1
execute if entity @s[tag=le.cent] if score @s le.llook matches ..0 if entity @s[nbt={OnGround:1b}] if entity @a[distance=3..5,gamemode=!spectator,gamemode=!creative] run return run function last_ember:lab/cent/rear_start
execute if score @s le.lcd matches ..0 if entity @a[distance=..2.8,gamemode=!spectator,gamemode=!creative] run function last_ember:lab/fish/swing
execute if score @s le.lst matches 60.. run function last_ember:lab/fish/step
# every 8-13 s, when its prey is 6-24 blocks away, it burrows and comes up under it
scoreboard players remove @s le.lfd 1
execute if score @s le.lfd matches ..0 run function last_ember:lab/fish/burrow_try
