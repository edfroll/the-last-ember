# generated: macro gen (storage last_ember:keys k.seal_magister): stale copies leave players and the floor; the holder is remembered; a loss is repaired
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"seal_magister"},!minecraft:custom_data~{gen:$(gen)}] run kill @s
$execute unless data storage last_ember:keys k.seal_magister{gen:1} run clear @a[tag=le.khas] *[minecraft:custom_data~{le_key:"seal_magister"},!minecraft:custom_data~{gen:$(gen)}]
execute if data storage last_ember:keys k.seal_magister{st:2} run return 0
execute if data storage last_ember:keys k.seal_magister{st:1} run return 0
$execute as @e[type=minecraft:item,tag=le.kitem,tag=!le.kthr] if items entity @s contents *[minecraft:custom_data~{le_key:"seal_magister",gen:$(gen)}] run function last_ember:altar/gen/kf_seal_magister
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"seal_magister",gen:$(gen)}] run return run data modify storage last_ember:keys k.seal_magister.it set value 1b
execute if data storage last_ember:keys k.seal_magister{it:0b} if data storage last_ember:keys k.seal_magister{got:1b} run return 0
execute if data storage last_ember:keys k.seal_magister{it:0b} unless score #kphase le.alt matches 0 run return 0
function last_ember:altar/gen/kp_seal_magister with storage last_ember:keys k.seal_magister
execute if data storage last_ember:keys k.seal_magister{it:1b} run function last_ember:altar/key_lost {id:"seal_magister"}
