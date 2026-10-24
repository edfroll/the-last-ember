scoreboard players remove @s le.lfl 1
execute if score @s le.lfl matches 0 if entity @s[tag=le.lab_drowner] run data remove entity @s equipment.head.components."minecraft:custom_model_data"
execute if score @s le.lfl matches 0 on passengers if entity @s[tag=le.lab_part] run data remove entity @s item.components."minecraft:custom_model_data"
