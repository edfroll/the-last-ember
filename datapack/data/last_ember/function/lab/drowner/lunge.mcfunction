# a leap at the nearest player that lands about a block in front of him (the force by the distance: it must not fly past him,
# or the zombie walks on along its old path, away from him); then for a second it keeps pressing toward him
execute store result score @s le.lfd run random value 100..160
execute if score #r le.l matches 0..1 run playsound last_ember:creature.alghoul.agressive_snarl hostile @a ~ ~ ~ 1.8 1
execute if score #r le.l matches 2 run playsound last_ember:creature.drowner.vo_attack hostile @a ~ ~ ~ 1.8 1
playsound last_ember:creature.drowner.swoosh hostile @a ~ ~1 ~ 1.0 0.8
particle minecraft:splash ~ ~0.8 ~ 0.3 0.4 0.3 0 12
scoreboard players set @s le.llook 20
execute if entity @a[distance=..4.5,gamemode=!spectator,gamemode=!creative] run return run function last_ember:lab/drowner/push {f:0.36,y:0.36}
execute if entity @a[distance=..5.5,gamemode=!spectator,gamemode=!creative] run return run function last_ember:lab/drowner/push {f:0.5,y:0.38}
execute if entity @a[distance=..6.5,gamemode=!spectator,gamemode=!creative] run return run function last_ember:lab/drowner/push {f:0.65,y:0.4}
function last_ember:lab/drowner/push {f:0.8,y:0.42}
