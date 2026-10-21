# as the protected partner
effect give @s minecraft:resistance 2 2 true
effect give @s minecraft:absorption 10 0 true
particle minecraft:totem_of_undying ~ ~1 ~ 0.4 0.6 0.4 0.2 20
playsound minecraft:item.totem.use player @a[distance=..16] ~ ~ ~ 0.5 1.4
title @s actionbar {"text":"Оберег знахаря","color":"green"}
