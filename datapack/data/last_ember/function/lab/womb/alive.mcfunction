function last_ember:lab/turn
# squash and stretch from the vertical speed: stretched going up, squashed on landing, then back, then slowly gathering for the next jump
execute store result score #vy le.l run data get entity @s Motion[1] 100
execute store result score #og le.l run data get entity @s OnGround
execute if score #og le.l matches 0 if score @s le.lair matches 0 if score #vy le.l matches 5.. run function last_ember:lab/womb/takeoff
execute if score #og le.l matches 0 run scoreboard players set @s le.lair 1
execute if score #og le.l matches 1 if score @s le.lair matches 1 run function last_ember:lab/womb/land
execute if score #og le.l matches 1 run function last_ember:lab/womb/ground
execute if score @s le.lcd matches ..0 if entity @a[distance=..3,gamemode=!spectator,gamemode=!creative] run function last_ember:lab/womb/swing
