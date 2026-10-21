# as a player who has just used oil (storage last_ember:pt oil): the weapon in the main hand gets le_oil {type, n}, n = 8 (tier 0) .. 16 (tier 6)
execute unless items entity @s weapon.mainhand #minecraft:swords unless items entity @s weapon.mainhand #minecraft:axes unless items entity @s weapon.mainhand minecraft:trident unless items entity @s weapon.mainhand minecraft:mace run return run function last_ember:potion/oil_refund
scoreboard players operation #n le.e = @s le.tier
scoreboard players operation #n le.e *= #8 le.e
scoreboard players operation #n le.e /= #6 le.e
scoreboard players add #n le.e 8
execute store result storage last_ember:pt n int 1 run scoreboard players get #n le.e
function last_ember:potion/oil_mod with storage last_ember:pt
title @s actionbar {"text":"Масло нанесено","color":"gold"}
playsound minecraft:item.bottle.empty player @a[distance=..8] ~ ~ ~ 1 1
