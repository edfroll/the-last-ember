# it stops dead for 0.8 s; the head jerks three times (a cough or a rattle)
scoreboard players set @s le.lfr 16
execute store result score @s le.lan run random value 90..160
attribute @s minecraft:movement_speed modifier add last_ember:lab_hold -1 add_multiplied_total
execute if score #r le.l matches 0..1 run playsound last_ember:creature.drowner.vo_cough hostile @a ~ ~ ~ 1.8 1
execute if score #r le.l matches 2 run playsound last_ember:creature.drowner.breath_long_q503 hostile @a ~ ~ ~ 1.8 1
