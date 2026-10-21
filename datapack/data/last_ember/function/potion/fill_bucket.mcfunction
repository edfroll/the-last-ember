setblock ~ ~ ~ minecraft:water_cauldron[level=3]
item replace entity @s weapon.mainhand with minecraft:bucket
playsound minecraft:item.bucket.empty block @a[distance=..12] ~ ~ ~ 1 1
title @s actionbar {"text":"Котёл полон воды","color":"aqua"}
return 1
