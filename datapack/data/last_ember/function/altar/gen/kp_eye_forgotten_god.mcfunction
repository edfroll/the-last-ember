# generated: macro gen: the players with a key item: the holder of the valid key eye_forgotten_god (returns 1 when found)
$execute as @a[tag=le.khas] if items entity @s container.* *[minecraft:custom_data~{le_key:"eye_forgotten_god",gen:$(gen)}] run return run function last_ember:altar/gen/kh_eye_forgotten_god
$execute as @a[tag=le.khas] if items entity @s weapon.offhand *[minecraft:custom_data~{le_key:"eye_forgotten_god",gen:$(gen)}] run return run function last_ember:altar/gen/kh_eye_forgotten_god
$execute as @a[tag=le.khas] if items entity @s player.cursor *[minecraft:custom_data~{le_key:"eye_forgotten_god",gen:$(gen)}] run return run function last_ember:altar/gen/kh_eye_forgotten_god
$execute as @a[tag=le.khas] if items entity @s armor.* *[minecraft:custom_data~{le_key:"eye_forgotten_god",gen:$(gen)}] run return run function last_ember:altar/gen/kh_eye_forgotten_god
$execute as @a[tag=le.khas] if items entity @s enderchest.* *[minecraft:custom_data~{le_key:"eye_forgotten_god",gen:$(gen)}] run return run function last_ember:altar/gen/kh_eye_forgotten_god
return 0
