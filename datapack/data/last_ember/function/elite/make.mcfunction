# ADMIN/TEST, also the end of the roll: as a mob at itself: makes it an elite without a roll (bigger, stronger, a name, a helmet of the colour of its region, a loot table with the trophy)
tag @s add le.elite
tag @s add le.rolled
function last_ember:elite/gen/region
function last_ember:elite/gen/name
data modify entity @s CustomName set from storage last_ember:elite name
data modify entity @s CustomNameVisible set value 1b
attribute @s minecraft:scale modifier remove last_ember:elite_scale
execute unless entity @s[type=#last_ember:elite_spiders] unless entity @s[type=minecraft:phantom] run attribute @s minecraft:scale modifier add last_ember:elite_scale 0.3 add_multiplied_base
execute if entity @s[type=#last_ember:elite_spiders] run attribute @s minecraft:scale modifier add last_ember:elite_scale 0.2 add_multiplied_base
execute if entity @s[type=minecraft:phantom] run attribute @s minecraft:scale modifier add last_ember:elite_scale 0.5 add_multiplied_base
attribute @s minecraft:max_health modifier remove last_ember:elite_hp
attribute @s minecraft:max_health modifier add last_ember:elite_hp 1.5 add_multiplied_base
attribute @s minecraft:attack_damage modifier remove last_ember:elite_dmg
attribute @s minecraft:attack_damage modifier add last_ember:elite_dmg 0.5 add_multiplied_base
attribute @s minecraft:movement_speed modifier remove last_ember:elite_spd
attribute @s minecraft:movement_speed modifier add last_ember:elite_spd 0.1 add_multiplied_base
attribute @s minecraft:knockback_resistance modifier remove last_ember:elite_kb
attribute @s minecraft:knockback_resistance modifier add last_ember:elite_kb 0.3 add_value
attribute @s minecraft:armor modifier remove last_ember:elite_armor
attribute @s minecraft:armor modifier add last_ember:elite_armor 4 add_value
execute store result storage last_ember:elite hp float 1 run attribute @s minecraft:max_health get
data modify entity @s Health set from storage last_ember:elite hp
function last_ember:elite/gen/helmet
data merge entity @s {drop_chances:{head:0.0f}}
function last_ember:elite/gen/loot
