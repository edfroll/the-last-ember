# generated: macro gen (storage last_ember:keys k.seal_whirl): stale copies leave players and the floor; the holder is remembered; a loss is repaired
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"seal_whirl"},!minecraft:custom_data~{gen:$(gen)}] run kill @s
$execute unless data storage last_ember:keys k.seal_whirl{gen:1} run clear @a[tag=le.khas] *[minecraft:custom_data~{le_key:"seal_whirl"},!minecraft:custom_data~{gen:$(gen)}]
execute if data storage last_ember:keys k.seal_whirl{st:2} run return 0
execute if data storage last_ember:keys k.seal_whirl{st:1} run return 0
$execute as @e[type=minecraft:item,tag=le.kitem,tag=!le.kthr] if items entity @s contents *[minecraft:custom_data~{le_key:"seal_whirl",gen:$(gen)}] run function last_ember:altar/gen/kf_seal_whirl
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"seal_whirl",gen:$(gen)}] run return run data modify storage last_ember:keys k.seal_whirl.it set value 1b
execute if data storage last_ember:keys k.seal_whirl{it:0b} if data storage last_ember:keys k.seal_whirl{got:1b} run return 0
execute if data storage last_ember:keys k.seal_whirl{it:0b} unless score #kphase le.alt matches 0 run return 0
function last_ember:altar/gen/kp_seal_whirl with storage last_ember:keys k.seal_whirl
execute if data storage last_ember:keys k.seal_whirl{it:1b} run function last_ember:altar/key_lost {id:"seal_whirl"}
