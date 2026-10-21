execute in minecraft:overworld run tp @s 0.5 58.5 -8.5 0 5
execute in minecraft:overworld run spawnpoint @s 0 59 -8
effect give @s minecraft:blindness 4 0 true
title @s actionbar {"text":"Ты просыпаешься…","color":"gray"}
playsound minecraft:ambient.cave ambient @s ~ ~ ~ 0.5 0.8
schedule function last_ember:char/open_cell 100t
