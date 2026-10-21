execute if block ~ ~ ~ minecraft:water_cauldron[level=3] run return run title @s actionbar {"text":"Котёл полон","color":"gray"}
execute if block ~ ~ ~ minecraft:water_cauldron[level=2] run setblock ~ ~ ~ minecraft:water_cauldron[level=3]
execute if block ~ ~ ~ minecraft:water_cauldron[level=1] run setblock ~ ~ ~ minecraft:water_cauldron[level=2]
execute if block ~ ~ ~ minecraft:cauldron run setblock ~ ~ ~ minecraft:water_cauldron[level=1]
item replace entity @s weapon.mainhand with minecraft:glass_bottle
playsound minecraft:item.bottle.empty block @a[distance=..12] ~ ~ ~ 1 1
return 1
