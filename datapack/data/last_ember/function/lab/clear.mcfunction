# ADMIN: removes every lab sample, part and label
execute as @e[type=#last_ember:lab_bodies,tag=le.lab_body] at @s run function last_ember:lab/remove
kill @e[type=minecraft:item_display,tag=le.lab_part]
kill @e[type=minecraft:text_display,tag=le.lab_label]
kill @e[tag=le.cseg]
kill @e[type=minecraft:interaction,tag=le.cbox]
kill @e[type=minecraft:marker,tag=le.cmark]
kill @e[type=minecraft:area_effect_cloud,tag=le.lab_trail]
