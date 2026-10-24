# the bite: the head goes back and the maw opens wide (4 ticks), then it snaps forward (the damage itself is the vanilla bite of the wolf)
scoreboard players set @s le.lan 2
scoreboard players set @s le.lfr 0
scoreboard players set @s le.lfd 0
execute if score #r le.l matches 0 run playsound last_ember:creature.wild_dog.attack hostile @a ~ ~ ~ 1.8 1
execute unless score #r le.l matches 0 run playsound last_ember:creature.wild_dog.growl_aggro hostile @a ~ ~ ~ 1.8 1
