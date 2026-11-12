# generated: macro gen: the players with a key item: the holder of the valid key crown_witches (returns 1 when found)
$execute as @a[tag=le.khas] if items entity @s container.* *[minecraft:custom_data~{le_key:"crown_witches",gen:$(gen)}] run return run function last_ember:altar/gen/kh_crown_witches
$execute as @a[tag=le.khas] if items entity @s weapon.offhand *[minecraft:custom_data~{le_key:"crown_witches",gen:$(gen)}] run return run function last_ember:altar/gen/kh_crown_witches
$execute as @a[tag=le.khas] if items entity @s player.cursor *[minecraft:custom_data~{le_key:"crown_witches",gen:$(gen)}] run return run function last_ember:altar/gen/kh_crown_witches
$execute as @a[tag=le.khas] if items entity @s armor.* *[minecraft:custom_data~{le_key:"crown_witches",gen:$(gen)}] run return run function last_ember:altar/gen/kh_crown_witches
$execute as @a[tag=le.khas] if items entity @s enderchest.* *[minecraft:custom_data~{le_key:"crown_witches",gen:$(gen)}] run return run function last_ember:altar/gen/kh_crown_witches
return 0
