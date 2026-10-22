# macro id, components: #dup = 1 when the player already has this piece (id + components) anywhere
$execute if data entity @s Inventory[{id:"$(id)",components:$(components)}] run scoreboard players set #dup le.e 1
$execute if data entity @s equipment.chest{id:"$(id)",components:$(components)} run scoreboard players set #dup le.e 1
$execute if data entity @s equipment.legs{id:"$(id)",components:$(components)} run scoreboard players set #dup le.e 1
$execute if data entity @s equipment.feet{id:"$(id)",components:$(components)} run scoreboard players set #dup le.e 1
$execute if data entity @s equipment.head{id:"$(id)",components:$(components)} run scoreboard players set #dup le.e 1
$execute if data entity @s equipment.offhand{id:"$(id)",components:$(components)} run scoreboard players set #dup le.e 1
