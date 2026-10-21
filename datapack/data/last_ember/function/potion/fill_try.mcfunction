# as a player at a cauldron interaction: a healer pours water in (water bucket: full, water bottle: +1 level); returns 1 when handled
execute unless entity @s[tag=le.class.healer] run return 0
execute if items entity @s weapon.mainhand minecraft:water_bucket run return run function last_ember:potion/fill_bucket
execute if items entity @s weapon.mainhand minecraft:potion[minecraft:potion_contents={potion:"minecraft:water"}] run return run function last_ember:potion/fill_bottle
return 0
