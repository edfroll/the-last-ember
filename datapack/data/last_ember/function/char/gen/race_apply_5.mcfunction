# as a player: Пеплорождённые -- modifiers (idempotent)
function last_ember:char/gen/race_strip
attribute @s minecraft:scale modifier add last_ember:race_scale 0.0 add_value
attribute @s minecraft:max_health modifier add last_ember:race_max_health 2 add_value
attribute @s minecraft:burning_time modifier add last_ember:race_burning_time -0.8 add_multiplied_base
