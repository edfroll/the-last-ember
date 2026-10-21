$execute store result score #d le.e run data get storage last_ember:pt it.components."minecraft:potion_contents".custom_effects[$(i)].duration
$execute store result score #a le.e run data get storage last_ember:pt it.components."minecraft:potion_contents".custom_effects[$(i)].amplifier
scoreboard players add #a le.e 1
execute if score #d le.e matches 2.. run scoreboard players operation #d le.e /= #2 le.e
$execute store result storage last_ember:pt it.components."minecraft:potion_contents".custom_effects[$(i)].duration int 1 run scoreboard players get #d le.e
$execute store result storage last_ember:pt it.components."minecraft:potion_contents".custom_effects[$(i)].amplifier byte 1 run scoreboard players get #a le.e
