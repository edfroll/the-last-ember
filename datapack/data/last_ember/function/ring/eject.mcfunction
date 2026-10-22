# macro slot: what the wearer put into an armor slot goes back to him (the inventory, else the floor)
$execute unless data entity @s equipment.$(slot) run return 0
summon minecraft:item ~ ~ ~ {Item:{id:"minecraft:stone",count:1},PickupDelay:0,Tags:["le.ringeject"]}
$data modify entity @e[type=minecraft:item,tag=le.ringeject,limit=1,sort=nearest] Item set from entity @s equipment.$(slot)
tag @e[type=minecraft:item,tag=le.ringeject] remove le.ringeject
$item replace entity @s armor.$(slot) with minecraft:air
