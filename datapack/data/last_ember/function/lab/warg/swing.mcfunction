scoreboard players set @s le.lcd 30
execute if score #r le.l matches 0 run playsound last_ember:creature.wild_dog.attack hostile @a ~ ~ ~ 1.8 1
execute unless score #r le.l matches 0 run playsound last_ember:creature.wild_dog.growl_aggro hostile @a ~ ~ ~ 1.8 1
