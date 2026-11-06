# generated: macro gen: the players with a key item: the holder of the valid key drop_source (returns 1 when found)
$execute as @a[tag=le.khas] if items entity @s container.* *[minecraft:custom_data~{le_key:"drop_source",gen:$(gen)}] run return run function last_ember:altar/gen/kh_drop_source
$execute as @a[tag=le.khas] if items entity @s weapon.offhand *[minecraft:custom_data~{le_key:"drop_source",gen:$(gen)}] run return run function last_ember:altar/gen/kh_drop_source
$execute as @a[tag=le.khas] if items entity @s player.cursor *[minecraft:custom_data~{le_key:"drop_source",gen:$(gen)}] run return run function last_ember:altar/gen/kh_drop_source
$execute as @a[tag=le.khas] if items entity @s armor.* *[minecraft:custom_data~{le_key:"drop_source",gen:$(gen)}] run return run function last_ember:altar/gen/kh_drop_source
$execute as @a[tag=le.khas] if items entity @s enderchest.* *[minecraft:custom_data~{le_key:"drop_source",gen:$(gen)}] run return run function last_ember:altar/gen/kh_drop_source
return 0
