function last_ember:lab/turn
execute if entity @s[tag=le.cent] run function last_ember:lab/cent/tick
execute if score @s le.lcd matches ..0 if entity @a[distance=..2.8,gamemode=!spectator,gamemode=!creative] run function last_ember:lab/fish/swing
execute if score @s le.lst matches 60.. run function last_ember:lab/fish/step
# every 8-13 s, when its prey is 6-24 blocks away, it burrows and comes up under it
scoreboard players remove @s le.lfd 1
execute if score @s le.lfd matches ..0 run function last_ember:lab/fish/burrow_try
