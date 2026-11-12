# generated: macro gen: the players with a key item: the holder of the valid key thread_labyrinth (returns 1 when found)
$execute as @a[tag=le.khas] if items entity @s container.* *[minecraft:custom_data~{le_key:"thread_labyrinth",gen:$(gen)}] run return run function last_ember:altar/gen/kh_thread_labyrinth
$execute as @a[tag=le.khas] if items entity @s weapon.offhand *[minecraft:custom_data~{le_key:"thread_labyrinth",gen:$(gen)}] run return run function last_ember:altar/gen/kh_thread_labyrinth
$execute as @a[tag=le.khas] if items entity @s player.cursor *[minecraft:custom_data~{le_key:"thread_labyrinth",gen:$(gen)}] run return run function last_ember:altar/gen/kh_thread_labyrinth
$execute as @a[tag=le.khas] if items entity @s armor.* *[minecraft:custom_data~{le_key:"thread_labyrinth",gen:$(gen)}] run return run function last_ember:altar/gen/kh_thread_labyrinth
$execute as @a[tag=le.khas] if items entity @s enderchest.* *[minecraft:custom_data~{le_key:"thread_labyrinth",gen:$(gen)}] run return run function last_ember:altar/gen/kh_thread_labyrinth
return 0
