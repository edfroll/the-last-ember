scoreboard players remove @s le.lfl 1
execute if score @s le.lfl matches 0 on passengers if entity @s[tag=le.lab_part] run data remove entity @s item.components."minecraft:custom_model_data"
