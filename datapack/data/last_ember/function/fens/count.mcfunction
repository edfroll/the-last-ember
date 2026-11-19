# T-026: macro key: #c = copies of the quest item `key` held by the players in the game (inventory, hands, the cursor) + lying on the ground
$execute store result score #c le.fn run clear @a *[minecraft:custom_data~{le_citem:"$(key)"}] 0
$execute as @e[type=minecraft:item] if items entity @s contents *[minecraft:custom_data~{le_citem:"$(key)"}] run scoreboard players add #c le.fn 1
