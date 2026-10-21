$execute store result score #d le.e run data get storage last_ember:pt it.components."minecraft:potion_contents".custom_effects[$(i)].duration
execute if score #d le.e matches 2.. run scoreboard players operation #d le.e *= #2 le.e
$execute store result storage last_ember:pt it.components."minecraft:potion_contents".custom_effects[$(i)].duration int 1 run scoreboard players get #d le.e
