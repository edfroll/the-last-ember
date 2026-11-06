# generated: macro gen: the players with a key item: the holder of the valid key anchor_drowned (returns 1 when found)
$execute as @a[tag=le.khas] if items entity @s container.* *[minecraft:custom_data~{le_key:"anchor_drowned",gen:$(gen)}] run return run function last_ember:altar/gen/kh_anchor_drowned
$execute as @a[tag=le.khas] if items entity @s weapon.offhand *[minecraft:custom_data~{le_key:"anchor_drowned",gen:$(gen)}] run return run function last_ember:altar/gen/kh_anchor_drowned
$execute as @a[tag=le.khas] if items entity @s player.cursor *[minecraft:custom_data~{le_key:"anchor_drowned",gen:$(gen)}] run return run function last_ember:altar/gen/kh_anchor_drowned
$execute as @a[tag=le.khas] if items entity @s armor.* *[minecraft:custom_data~{le_key:"anchor_drowned",gen:$(gen)}] run return run function last_ember:altar/gen/kh_anchor_drowned
$execute as @a[tag=le.khas] if items entity @s enderchest.* *[minecraft:custom_data~{le_key:"anchor_drowned",gen:$(gen)}] run return run function last_ember:altar/gen/kh_anchor_drowned
return 0
