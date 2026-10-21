# as a player: picks Рыцарь
scoreboard players set @s le.class 1
function last_ember:char/gen/class_untag
tag @s add le.class.knight
function last_ember:char/gen/class_apply_1
particle minecraft:end_rod -4.5 60.2 52.5 0.3 0.3 0.3 0.05 40
playsound minecraft:block.enchantment_table.use player @s -4.5 55 52.5 1 1
tellraw @s {"text":"Ты — Рыцарь.","color":"gold"}
function last_ember:char/gen/light_stone
function last_ember:char/give_kit
function last_ember:char/effects
function last_ember:char/open_font
function last_ember:char/finish
