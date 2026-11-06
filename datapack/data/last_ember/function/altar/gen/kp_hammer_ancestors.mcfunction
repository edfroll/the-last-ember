# generated: macro gen: the players with a key item: the holder of the valid key hammer_ancestors (returns 1 when found)
$execute as @a[tag=le.khas] if items entity @s container.* *[minecraft:custom_data~{le_key:"hammer_ancestors",gen:$(gen)}] run return run function last_ember:altar/gen/kh_hammer_ancestors
$execute as @a[tag=le.khas] if items entity @s weapon.offhand *[minecraft:custom_data~{le_key:"hammer_ancestors",gen:$(gen)}] run return run function last_ember:altar/gen/kh_hammer_ancestors
$execute as @a[tag=le.khas] if items entity @s player.cursor *[minecraft:custom_data~{le_key:"hammer_ancestors",gen:$(gen)}] run return run function last_ember:altar/gen/kh_hammer_ancestors
$execute as @a[tag=le.khas] if items entity @s armor.* *[minecraft:custom_data~{le_key:"hammer_ancestors",gen:$(gen)}] run return run function last_ember:altar/gen/kh_hammer_ancestors
$execute as @a[tag=le.khas] if items entity @s enderchest.* *[minecraft:custom_data~{le_key:"hammer_ancestors",gen:$(gen)}] run return run function last_ember:altar/gen/kh_hammer_ancestors
return 0
