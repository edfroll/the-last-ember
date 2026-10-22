# as a player: the kit of the class by tag (once: tag le.kit)
execute if entity @s[tag=le.kit] run return 0
tag @s add le.kit
function last_ember:char/gen/kit_all
execute if entity @s[tag=le.class.knight] run function last_ember:char/gen/kit_knight
execute if entity @s[tag=le.class.ranger] run function last_ember:char/gen/kit_ranger
execute if entity @s[tag=le.class.seer] run function last_ember:char/gen/kit_seer
execute if entity @s[tag=le.class.healer] run function last_ember:char/gen/kit_healer
execute if entity @s[tag=le.race.halfling] run function last_ember:ring/first
