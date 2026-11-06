# generated: macro gen: the players with a key item: the holder of the valid key banner_dawn (returns 1 when found)
$execute as @a[tag=le.khas] if items entity @s container.* *[minecraft:custom_data~{le_key:"banner_dawn",gen:$(gen)}] run return run function last_ember:altar/gen/kh_banner_dawn
$execute as @a[tag=le.khas] if items entity @s weapon.offhand *[minecraft:custom_data~{le_key:"banner_dawn",gen:$(gen)}] run return run function last_ember:altar/gen/kh_banner_dawn
$execute as @a[tag=le.khas] if items entity @s player.cursor *[minecraft:custom_data~{le_key:"banner_dawn",gen:$(gen)}] run return run function last_ember:altar/gen/kh_banner_dawn
$execute as @a[tag=le.khas] if items entity @s armor.* *[minecraft:custom_data~{le_key:"banner_dawn",gen:$(gen)}] run return run function last_ember:altar/gen/kh_banner_dawn
$execute as @a[tag=le.khas] if items entity @s enderchest.* *[minecraft:custom_data~{le_key:"banner_dawn",gen:$(gen)}] run return run function last_ember:altar/gen/kh_banner_dawn
return 0
