# T-032: as the Mistress asleep: a player entered the nest or hit her: she wakes; health 120 + 40 per player in the nest (1 at least)
tag @a remove le.spin
function last_ember:spiders/gen/count_nest
execute if score #innest le.sp matches ..1 run function last_ember:spiders/gen/boss_hp_1
execute if score #innest le.sp matches 2 run function last_ember:spiders/gen/boss_hp_2
execute if score #innest le.sp matches 3 run function last_ember:spiders/gen/boss_hp_3
execute if score #innest le.sp matches 4.. run function last_ember:spiders/gen/boss_hp_4
data modify entity @s NoAI set value 0b
scoreboard players set #bs le.sp 1
scoreboard players add #fight le.sp 1
scoreboard players set #empty le.sp 0
scoreboard players set #web le.sp 8
scoreboard players set #brood le.sp 0
execute at @s run playsound minecraft:entity.spider.ambient hostile @a[distance=..48] ~ ~2 ~ 3 0.45
execute at @s run playsound minecraft:entity.ravager.roar hostile @a[distance=..48] ~ ~2 ~ 1.2 1.6
