# as an elite slime / magma cube (every scan): the small ones that a dying elite splits into copy its tags and name; they are ordinary mobs
execute store result score #sz le.el run data get entity @s Size
execute if score #sz le.el matches 3.. run return 0
tag @s remove le.elite
attribute @s minecraft:scale modifier remove last_ember:elite_scale
attribute @s minecraft:max_health modifier remove last_ember:elite_hp
attribute @s minecraft:attack_damage modifier remove last_ember:elite_dmg
attribute @s minecraft:movement_speed modifier remove last_ember:elite_spd
attribute @s minecraft:knockback_resistance modifier remove last_ember:elite_kb
attribute @s minecraft:armor modifier remove last_ember:elite_armor
data remove entity @s CustomName
data modify entity @s CustomNameVisible set value 0b
data remove entity @s DeathLootTable
