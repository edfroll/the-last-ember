# a blow from the front: only a quarter of it counts (#h gets back 3/4 of the loss #d)
scoreboard players operation #d le.ct *= #3 le.ct
scoreboard players operation #d le.ct /= #4 le.ct
scoreboard players operation #h le.ct += #d le.ct
playsound minecraft:block.wood.hit hostile @a ~ ~1.5 ~ 1.4 0.6
particle minecraft:block{block_state:"minecraft:oak_log"} ~ ~1.6 ~ 0.4 0.4 0.4 0 10
title @a[tag=le.catk] actionbar {"text":"Кора держит удар","color":"gray"}
