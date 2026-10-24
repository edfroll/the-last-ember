# a sudden dash at the prey: a short hop and 0.6 s of triple speed along its own path (a thrown Motion made it skip the nodes
# of its path, and the zombie then walked back to them, away from the player - Edward saw it turn round after every leap)
execute store result score @s le.lfd run random value 100..160
execute if score #r le.l matches 0..1 run playsound last_ember:creature.alghoul.agressive_snarl hostile @a ~ ~ ~ 1.8 1
execute if score #r le.l matches 2 run playsound last_ember:creature.drowner.vo_attack hostile @a ~ ~ ~ 1.8 1
playsound last_ember:creature.drowner.swoosh hostile @a ~ ~1 ~ 1.0 0.8
particle minecraft:splash ~ ~0.8 ~ 0.3 0.4 0.3 0 12
data modify entity @s Motion[1] set value 0.34d
attribute @s minecraft:movement_speed modifier remove last_ember:lab_dash
attribute @s minecraft:movement_speed modifier add last_ember:lab_dash 2.0 add_multiplied_total
scoreboard players set @s le.llook 12
