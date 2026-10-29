# MODULE (as a player): Venom — a bite of the claws: poison I for 8 s; a bite while the venom still holds: poison II for 8 s (it grows no further);
# milk, the antidote of the healer (and the water of the Healing Lake: it only has to clear poison) take it off — le.wven drops to 0 when the poison is gone
tag @s add le.wound
execute unless predicate last_ember:lab/poisoned run scoreboard players set @s le.wven 0
execute if score @s le.wven matches 1.. run effect give @s minecraft:poison 8 1
execute unless score @s le.wven matches 1.. run effect give @s minecraft:poison 8 0
scoreboard players set @s le.wven 160
title @s actionbar {"text":"Яд — нужно противоядие или молоко","color":"dark_green"}
