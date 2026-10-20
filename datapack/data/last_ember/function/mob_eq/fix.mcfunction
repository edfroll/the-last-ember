# Runs as one mob, once. Our own elite mobs (tag le.elite) are equipped by the datapack itself and are skipped.
tag @s add le.eq_done
execute if entity @s[tag=le.elite] run return 0
execute if items entity @s weapon.mainhand #last_ember:metal_gear run data merge entity @s {drop_chances:{mainhand:0.0f}}
execute if items entity @s weapon.offhand #last_ember:metal_gear run data merge entity @s {drop_chances:{offhand:0.0f}}
execute if items entity @s armor.head #last_ember:metal_gear run data merge entity @s {drop_chances:{head:0.0f}}
execute if items entity @s armor.chest #last_ember:metal_gear run data merge entity @s {drop_chances:{chest:0.0f}}
execute if items entity @s armor.legs #last_ember:metal_gear run data merge entity @s {drop_chances:{legs:0.0f}}
execute if items entity @s armor.feet #last_ember:metal_gear run data merge entity @s {drop_chances:{feet:0.0f}}
execute if items entity @s armor.body #last_ember:metal_gear run data merge entity @s {drop_chances:{body:0.0f}}
