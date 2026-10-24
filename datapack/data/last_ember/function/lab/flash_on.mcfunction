# hurt: the display parts flash red for a moment and the eyes flash black or white (whichever stands out on that monster);
# the drowner's eyes are in its head item (the zombie flashes red by itself)
scoreboard players set @s le.lfl 7
execute if entity @s[tag=le.lab_drowner] run return run data modify entity @s equipment.head.components."minecraft:custom_model_data" set value {colors:[-1,0]}
data modify storage last_ember:lab fc set value {colors:[16738890,16777215]}
execute if entity @s[tag=le.lab_womb] run data modify storage last_ember:lab fc set value {colors:[16738890,0]}
execute on passengers if entity @s[tag=le.lab_part] run data modify entity @s item.components."minecraft:custom_model_data" set from storage last_ember:lab fc
