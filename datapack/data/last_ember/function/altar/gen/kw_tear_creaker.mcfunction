# generated: macro gen (storage last_ember:keys k.tear_creaker): stale copies leave players and the floor; the holder is remembered; a loss is repaired
$clear @a *[minecraft:custom_data~{le_key:"tear_creaker"},!minecraft:custom_data~{gen:$(gen)}]
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"tear_creaker"},!minecraft:custom_data~{gen:$(gen)}] run kill @s
execute if data storage last_ember:keys k.tear_creaker{st:2} run return 0
execute if data storage last_ember:keys k.tear_creaker{st:1} run return 0
scoreboard players set #kh le.alt 0
$execute as @a[limit=1] if score #kh le.alt matches 0 as @a if items entity @s container.* *[minecraft:custom_data~{le_key:"tear_creaker",gen:$(gen)}] run function last_ember:altar/gen/kh_tear_creaker
$execute as @a[limit=1] if score #kh le.alt matches 0 as @a if items entity @s weapon.offhand *[minecraft:custom_data~{le_key:"tear_creaker",gen:$(gen)}] run function last_ember:altar/gen/kh_tear_creaker
$execute as @a[limit=1] if score #kh le.alt matches 0 as @a if items entity @s player.cursor *[minecraft:custom_data~{le_key:"tear_creaker",gen:$(gen)}] run function last_ember:altar/gen/kh_tear_creaker
$execute as @a[limit=1] if score #kh le.alt matches 0 as @a if items entity @s armor.* *[minecraft:custom_data~{le_key:"tear_creaker",gen:$(gen)}] run function last_ember:altar/gen/kh_tear_creaker
$execute as @a[limit=1] if score #kh le.alt matches 0 as @a if items entity @s enderchest.* *[minecraft:custom_data~{le_key:"tear_creaker",gen:$(gen)}] run function last_ember:altar/gen/kh_tear_creaker
execute if score #kh le.alt matches 1 run return 0
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"tear_creaker",gen:$(gen)}] run return run data modify storage last_ember:keys k.tear_creaker.it set value 1b
execute if data storage last_ember:keys k.tear_creaker{it:1b} run function last_ember:altar/key_lost {id:"tear_creaker"}
