# T-033: as a new vanilla zombie / husk / skeleton in the workings (after its elite roll, not an elite): with an empty head - the miner's
# helmet and a pickaxe (zombies and husks in the hand if it is empty; skeletons in the off hand: they keep the bow), drop 0
tag @s add le.mnhat
execute if items entity @s armor.head * run return 0
item replace entity @s armor.head with minecraft:leather_helmet[dyed_color=3877402]
data modify entity @s drop_chances.head set value 0.0f
execute if entity @s[type=!minecraft:skeleton] unless items entity @s weapon.mainhand * run data modify entity @s drop_chances.mainhand set value 0.0f
execute if entity @s[type=!minecraft:skeleton] unless items entity @s weapon.mainhand * run item replace entity @s weapon.mainhand with minecraft:stone_pickaxe
execute if entity @s[type=minecraft:skeleton] unless items entity @s weapon.offhand * run data modify entity @s drop_chances.offhand set value 0.0f
execute if entity @s[type=minecraft:skeleton] unless items entity @s weapon.offhand * run item replace entity @s weapon.offhand with minecraft:stone_pickaxe
