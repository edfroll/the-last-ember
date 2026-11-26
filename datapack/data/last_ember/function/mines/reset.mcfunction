# T-033: admin: the mines as in a new world: the cave-ins standing (templates `before`, the sensors), the dead miners on their points, Bran
# resting in his pocket, the carts at their places, the props, the barrels and the chest with their loot
function last_ember:mines/gen/restore_all
kill @e[type=minecraft:item,tag=le.mnbi]
scoreboard players set #bran le.mn 0
data modify storage last_ember:mines bran set value 0
function last_ember:mines/gen/bran_spawn
function last_ember:mines/gen/dawn_all
kill @e[type=minecraft:minecart,tag=le.mn_cart]
scoreboard players set #i1 le.mn 0
scoreboard players set #i2 le.mn 0
scoreboard players set #i3 le.mn 0
scoreboard players set #i4 le.mn 0
function last_ember:mines/gen/props_put
function last_ember:mines/gen/barrels
tellraw @s {"text":"mines: reset","color":"gray"}
