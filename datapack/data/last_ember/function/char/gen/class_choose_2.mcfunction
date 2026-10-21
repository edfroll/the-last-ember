# as a player: picks Следопыт
scoreboard players set @s le.class 2
function last_ember:char/gen/class_untag
tag @s add le.class.ranger
function last_ember:char/gen/class_apply_2
particle minecraft:end_rod 5.5 60.2 52.5 0.3 0.3 0.3 0.05 40
playsound minecraft:block.enchantment_table.use player @s 5.5 55 52.5 1 1
tellraw @s {"text":"Ты — Следопыт.","color":"gold"}
function last_ember:char/gen/light_stone
function last_ember:char/give_kit
function last_ember:char/effects
function last_ember:char/open_font
function last_ember:char/finish
