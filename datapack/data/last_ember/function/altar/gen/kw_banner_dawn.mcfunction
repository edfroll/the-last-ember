# generated: macro gen (storage last_ember:keys k.banner_dawn): stale copies leave players and the floor; the holder is remembered; a loss is repaired
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"banner_dawn"},!minecraft:custom_data~{gen:$(gen)}] run kill @s
$execute unless data storage last_ember:keys k.banner_dawn{gen:1} run clear @a[tag=le.khas] *[minecraft:custom_data~{le_key:"banner_dawn"},!minecraft:custom_data~{gen:$(gen)}]
execute if data storage last_ember:keys k.banner_dawn{st:2} run return 0
execute if data storage last_ember:keys k.banner_dawn{st:1} run return 0
$execute as @e[type=minecraft:item,tag=le.kitem,tag=!le.kthr] if items entity @s contents *[minecraft:custom_data~{le_key:"banner_dawn",gen:$(gen)}] run function last_ember:altar/gen/kf_banner_dawn
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"banner_dawn",gen:$(gen)}] run return run data modify storage last_ember:keys k.banner_dawn.it set value 1b
execute if data storage last_ember:keys k.banner_dawn{it:0b} if data storage last_ember:keys k.banner_dawn{got:1b} run return 0
execute if data storage last_ember:keys k.banner_dawn{it:0b} unless score #kphase le.alt matches 2 run return 0
function last_ember:altar/gen/kp_banner_dawn with storage last_ember:keys k.banner_dawn
execute if data storage last_ember:keys k.banner_dawn{it:1b} run function last_ember:altar/key_lost {id:"banner_dawn"}
