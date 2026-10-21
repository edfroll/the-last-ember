# as a player: Гномы -- modifiers (idempotent)
function last_ember:char/gen/race_strip
attribute @s minecraft:scale modifier add last_ember:race_scale -0.2 add_value
attribute @s minecraft:max_health modifier add last_ember:race_max_health 4 add_value
attribute @s minecraft:attack_damage modifier add last_ember:race_attack_damage 1 add_value
attribute @s minecraft:block_break_speed modifier add last_ember:race_block_break_speed 0.3 add_multiplied_base
attribute @s minecraft:knockback_resistance modifier add last_ember:race_knockback_resistance 0.5 add_value
attribute @s minecraft:movement_speed modifier add last_ember:race_movement_speed -0.1 add_multiplied_base
attribute @s minecraft:jump_strength modifier add last_ember:race_jump_strength -0.08 add_multiplied_base
attribute @s minecraft:block_interaction_range modifier add last_ember:race_block_interaction_range -0.5 add_value
attribute @s minecraft:entity_interaction_range modifier add last_ember:race_entity_interaction_range -0.5 add_value
