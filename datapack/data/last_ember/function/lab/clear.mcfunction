# ADMIN: removes every lab sample, part and label
execute as @e[type=#last_ember:lab_bodies,tag=le.lab_body] at @s run function last_ember:lab/remove
kill @e[type=minecraft:item_display,tag=le.lab_part]
kill @e[type=minecraft:text_display,tag=le.lab_label]
