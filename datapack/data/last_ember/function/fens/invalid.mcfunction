# T-026: macro key, gen: copies of an older generation go (players in the game, items on the ground)
$clear @a *[minecraft:custom_data~{le_citem:"$(key)"},!minecraft:custom_data~{gen:$(gen)}]
$execute as @e[type=minecraft:item] if items entity @s contents *[minecraft:custom_data~{le_citem:"$(key)"},!minecraft:custom_data~{gen:$(gen)}] run kill @s
