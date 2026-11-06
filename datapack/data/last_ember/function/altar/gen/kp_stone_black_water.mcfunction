# generated: macro gen: the players with a key item: the holder of the valid key stone_black_water (returns 1 when found)
$execute as @a[tag=le.khas] if items entity @s container.* *[minecraft:custom_data~{le_key:"stone_black_water",gen:$(gen)}] run return run function last_ember:altar/gen/kh_stone_black_water
$execute as @a[tag=le.khas] if items entity @s weapon.offhand *[minecraft:custom_data~{le_key:"stone_black_water",gen:$(gen)}] run return run function last_ember:altar/gen/kh_stone_black_water
$execute as @a[tag=le.khas] if items entity @s player.cursor *[minecraft:custom_data~{le_key:"stone_black_water",gen:$(gen)}] run return run function last_ember:altar/gen/kh_stone_black_water
$execute as @a[tag=le.khas] if items entity @s armor.* *[minecraft:custom_data~{le_key:"stone_black_water",gen:$(gen)}] run return run function last_ember:altar/gen/kh_stone_black_water
$execute as @a[tag=le.khas] if items entity @s enderchest.* *[minecraft:custom_data~{le_key:"stone_black_water",gen:$(gen)}] run return run function last_ember:altar/gen/kh_stone_black_water
return 0
