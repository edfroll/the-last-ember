# macro slot: the item of storage last_ember:pt it replaces the item in container slot $(slot) of the player (through a marker armor stand)
data remove storage last_ember:pt it.Slot
summon minecraft:armor_stand ~ ~ ~ {Marker:1b,Invisible:1b,NoGravity:1b,Tags:["le.ptmp"]}
data modify entity @e[type=minecraft:armor_stand,tag=le.ptmp,limit=1,distance=..1] equipment.mainhand set from storage last_ember:pt it
$item replace entity @s container.$(slot) from entity @e[type=minecraft:armor_stand,tag=le.ptmp,limit=1,distance=..1] weapon.mainhand
kill @e[type=minecraft:armor_stand,tag=le.ptmp,distance=..1]
