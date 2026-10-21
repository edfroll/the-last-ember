# as a player: Рыцарь -- modifiers (idempotent)
function last_ember:char/gen/class_strip
attribute @s minecraft:luck modifier add last_ember:class_mark 0 add_value
attribute @s minecraft:attack_speed modifier add last_ember:class_attack_speed 0.2 add_multiplied_base
attribute @s minecraft:entity_interaction_range modifier add last_ember:class_entity_interaction_range 0.5 add_value
