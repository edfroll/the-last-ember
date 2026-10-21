# ranger: speed x1.5 (range x~2.0 with the air drag, measured in the report); the damage is divided back so that only the range changes
execute store result entity @s Motion[0] double 0.0001 run data get entity @s Motion[0] 15000
execute store result entity @s Motion[1] double 0.0001 run data get entity @s Motion[1] 15000
execute store result entity @s Motion[2] double 0.0001 run data get entity @s Motion[2] 15000
execute store result entity @s damage double 0.0001 run data get entity @s damage 6667
