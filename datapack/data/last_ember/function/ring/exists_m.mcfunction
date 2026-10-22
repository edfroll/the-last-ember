# macro a b c d: #rx = 1 when a ring of this owner is anywhere: in a player's inventory, hands, head, ender chest, or on the floor
$execute if items entity @a container.* *[minecraft:custom_data~{le_ring:1b,owner:[I;$(a),$(b),$(c),$(d)]}] run scoreboard players set #rx le.e 1
$execute if items entity @a armor.head *[minecraft:custom_data~{le_ring:1b,owner:[I;$(a),$(b),$(c),$(d)]}] run scoreboard players set #rx le.e 1
$execute if items entity @a weapon.* *[minecraft:custom_data~{le_ring:1b,owner:[I;$(a),$(b),$(c),$(d)]}] run scoreboard players set #rx le.e 1
$execute if items entity @a enderchest.* *[minecraft:custom_data~{le_ring:1b,owner:[I;$(a),$(b),$(c),$(d)]}] run scoreboard players set #rx le.e 1
$execute if entity @e[type=minecraft:item,nbt={Item:{components:{"minecraft:custom_data":{le_ring:1b,owner:[I;$(a),$(b),$(c),$(d)]}}}}] run scoreboard players set #rx le.e 1
