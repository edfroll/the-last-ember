# as a player: Полурослики -- modifiers (idempotent)
function last_ember:char/gen/race_strip
attribute @s minecraft:scale modifier add last_ember:race_scale -0.35 add_value
attribute @s minecraft:max_health modifier add last_ember:race_max_health -6 add_value
attribute @s minecraft:sneaking_speed modifier add last_ember:race_sneaking_speed 0.5 add_multiplied_base
attribute @s minecraft:fall_damage_multiplier modifier add last_ember:race_fall_damage_multiplier -0.5 add_multiplied_base
attribute @s minecraft:safe_fall_distance modifier add last_ember:race_safe_fall_distance 6 add_value
attribute @s minecraft:luck modifier add last_ember:race_luck 1 add_value
attribute @s minecraft:attack_damage modifier add last_ember:race_attack_damage -1 add_value
attribute @s minecraft:block_interaction_range modifier add last_ember:race_block_interaction_range -0.75 add_value
attribute @s minecraft:entity_interaction_range modifier add last_ember:race_entity_interaction_range -0.75 add_value
