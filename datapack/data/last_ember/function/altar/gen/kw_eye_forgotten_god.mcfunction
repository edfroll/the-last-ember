# generated: macro gen (storage last_ember:keys k.eye_forgotten_god): stale copies leave players and the floor; the holder is remembered; a loss is repaired
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"eye_forgotten_god"},!minecraft:custom_data~{gen:$(gen)}] run kill @s
$execute unless data storage last_ember:keys k.eye_forgotten_god{gen:1} run clear @a[tag=le.khas] *[minecraft:custom_data~{le_key:"eye_forgotten_god"},!minecraft:custom_data~{gen:$(gen)}]
execute if data storage last_ember:keys k.eye_forgotten_god{st:2} run return 0
execute if data storage last_ember:keys k.eye_forgotten_god{st:1} run return 0
$execute as @e[type=minecraft:item,tag=le.kitem,tag=!le.kthr] if items entity @s contents *[minecraft:custom_data~{le_key:"eye_forgotten_god",gen:$(gen)}] run function last_ember:altar/gen/kf_eye_forgotten_god
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"eye_forgotten_god",gen:$(gen)}] run return run data modify storage last_ember:keys k.eye_forgotten_god.it set value 1b
execute if data storage last_ember:keys k.eye_forgotten_god{it:0b} if data storage last_ember:keys k.eye_forgotten_god{got:1b} run return 0
execute if data storage last_ember:keys k.eye_forgotten_god{it:0b} unless score #kphase le.alt matches 1 run return 0
function last_ember:altar/gen/kp_eye_forgotten_god with storage last_ember:keys k.eye_forgotten_god
execute if data storage last_ember:keys k.eye_forgotten_god{it:1b} run function last_ember:altar/key_lost {id:"eye_forgotten_god"}
