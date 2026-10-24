# the bite is ours (the wolf itself does no harm): from up to 3.8 blocks the head goes back and the maw opens wide (4 ticks), then it snaps forward
scoreboard players set @s le.lan 2
scoreboard players set @s le.lfr 0
scoreboard players set @s le.lfd 0
attribute @s minecraft:movement_speed modifier add last_ember:lab_hold -1 add_multiplied_total
execute if score #r le.l matches 0 run playsound last_ember:creature.wild_dog.attack hostile @a ~ ~ ~ 1.8 1
execute unless score #r le.l matches 0 run playsound last_ember:creature.wild_dog.growl_aggro hostile @a ~ ~ ~ 1.8 1
