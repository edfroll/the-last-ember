# carrier puts the Ember into this stela's socket
tag @a[tag=le.clicker] remove le.carrier
clear @a[tag=le.clicker] *[minecraft:custom_data~{le_ember:1b}]
execute store result storage last_ember:ember socket int 1 run scoreboard players get @s le.bidx
kill @e[type=minecraft:item_display,tag=le.ember_disp]
summon minecraft:item_display ~ ~2.35 ~ {Tags:["le.ember_disp"],billboard:"vertical",brightness:{sky:15,block:15},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0.6f,0.6f,0.6f]},item:{id:"minecraft:trial_key",count:1,components:{"minecraft:item_model":"last_ember:ember"}}}
particle minecraft:flame ~ ~2.3 ~ 0.1 0.1 0.1 0.02 20
playsound minecraft:block.respawn_anchor.charge block @a[distance=..16] ~ ~ ~ 0.8 1.4
title @a[tag=le.clicker] actionbar {"text":"Уголь в гнезде стелы. Забрать его может любой у этого костра.","color":"gold"}
