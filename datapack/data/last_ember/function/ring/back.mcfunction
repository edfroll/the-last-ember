# macro slot: one piece back (see restore_armor)
$execute unless data storage last_ember:ring cur.$(slot) run return 0
$data modify storage last_ember:ring it set from storage last_ember:ring cur.$(slot)
execute unless data storage last_ember:ring it.components run data modify storage last_ember:ring it.components set value {}
scoreboard players set #dup le.e 0
execute if score #dd le.e matches 1 run function last_ember:ring/dup_check with storage last_ember:ring it
execute if score #dup le.e matches 1 run return 0
$execute if data entity @s equipment.$(slot) run function last_ember:ring/eject {slot:"$(slot)"}
data modify entity @e[type=minecraft:armor_stand,tag=le.ringstand,limit=1] equipment.mainhand set from storage last_ember:ring it
$item replace entity @s armor.$(slot) from entity @e[type=minecraft:armor_stand,tag=le.ringstand,limit=1] weapon.mainhand
