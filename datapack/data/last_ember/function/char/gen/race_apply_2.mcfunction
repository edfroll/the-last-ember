# as a player: Эльфы -- modifiers (idempotent)
function last_ember:char/gen/race_strip
attribute @s minecraft:scale modifier add last_ember:race_scale 0.1 add_value
attribute @s minecraft:max_health modifier add last_ember:race_max_health -4 add_value
attribute @s minecraft:movement_speed modifier add last_ember:race_movement_speed 0.1 add_multiplied_base
attribute @s minecraft:jump_strength modifier add last_ember:race_jump_strength 0.15 add_multiplied_base
attribute @s minecraft:safe_fall_distance modifier add last_ember:race_safe_fall_distance 3 add_value
attribute @s minecraft:attack_damage modifier add last_ember:race_attack_damage -1 add_value
