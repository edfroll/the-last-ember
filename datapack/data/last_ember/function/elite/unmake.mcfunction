# as a mob: the stats of an elite are taken off (the small ones of a split elite slime, a statue that goes back to stone)
tag @s remove le.elite
attribute @s minecraft:scale modifier remove last_ember:elite_scale
attribute @s minecraft:max_health modifier remove last_ember:elite_hp
attribute @s minecraft:attack_damage modifier remove last_ember:elite_dmg
attribute @s minecraft:movement_speed modifier remove last_ember:elite_spd
attribute @s minecraft:knockback_resistance modifier remove last_ember:elite_kb
attribute @s minecraft:armor modifier remove last_ember:elite_armor
data remove entity @s DeathLootTable
