# generated: macro gen: the players with a key item: the holder of the valid key seal_magister (returns 1 when found)
$execute as @a[tag=le.khas] if items entity @s container.* *[minecraft:custom_data~{le_key:"seal_magister",gen:$(gen)}] run return run function last_ember:altar/gen/kh_seal_magister
$execute as @a[tag=le.khas] if items entity @s weapon.offhand *[minecraft:custom_data~{le_key:"seal_magister",gen:$(gen)}] run return run function last_ember:altar/gen/kh_seal_magister
$execute as @a[tag=le.khas] if items entity @s player.cursor *[minecraft:custom_data~{le_key:"seal_magister",gen:$(gen)}] run return run function last_ember:altar/gen/kh_seal_magister
$execute as @a[tag=le.khas] if items entity @s armor.* *[minecraft:custom_data~{le_key:"seal_magister",gen:$(gen)}] run return run function last_ember:altar/gen/kh_seal_magister
$execute as @a[tag=le.khas] if items entity @s enderchest.* *[minecraft:custom_data~{le_key:"seal_magister",gen:$(gen)}] run return run function last_ember:altar/gen/kh_seal_magister
return 0
