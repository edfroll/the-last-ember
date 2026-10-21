# as a player: Рыцарь -- modifiers (idempotent)
function last_ember:char/gen/class_strip
attribute @s minecraft:luck modifier add last_ember:class_mark 0 add_value
attribute @s minecraft:entity_interaction_range modifier add last_ember:class_entity_interaction_range 0.5 add_value
function last_ember:char/knight_tier
