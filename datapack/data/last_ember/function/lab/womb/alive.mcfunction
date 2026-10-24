function last_ember:lab/turn
# not the vanilla slime: it does not hop by itself (jump strength and speed 0), it crawls at its prey in surges (a heave every 0.7-1.3 s, sometimes a hop instead),
# gathers itself and leaps at it from close by; it leaves a green stinking trail; the shape follows the motion (squash, stretch, a forward lunge)
execute if entity @a[distance=..24,gamemode=!spectator,gamemode=!creative] run rotate @s facing entity @p[gamemode=!spectator,gamemode=!creative] feet
execute store result score #vy le.l run data get entity @s Motion[1] 100
execute store result score #og le.l run data get entity @s OnGround
# in water (the bog) it heaves itself on as on the ground
execute if score #og le.l matches 0 if block ~ ~0.3 ~ minecraft:water run scoreboard players set #og le.l 1
execute if score #og le.l matches 0 if score @s le.lair matches 0 if score #vy le.l matches 20.. run function last_ember:lab/womb/takeoff
execute if score #og le.l matches 0 run scoreboard players set @s le.lair 1
execute if score #og le.l matches 1 if score @s le.lair matches 1 run function last_ember:lab/womb/land
execute if score #og le.l matches 1 run function last_ember:lab/womb/ground
scoreboard players operation #t5 le.l = #gt le.l
scoreboard players operation #t5 le.l %= #5 le.l
execute if score #t5 le.l matches 0 if score @s le.lsp matches 3.. if score #og le.l matches 1 run function last_ember:lab/womb/trail
execute if score @s le.lan matches 1 run return run function last_ember:lab/womb/gather
scoreboard players remove @s le.lfd 1
execute if score #og le.l matches 1 if score @s le.lcd matches ..0 if entity @a[distance=..4.5,gamemode=!spectator,gamemode=!creative] run return run function last_ember:lab/womb/gather_start
execute if score #og le.l matches 1 if score @s le.lfd matches ..0 if entity @a[distance=2.5..24,gamemode=!spectator,gamemode=!creative] run function last_ember:lab/womb/surge
