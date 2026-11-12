# generated: macro gen (storage last_ember:keys k.shard_ice_crown): stale copies leave players and the floor; the holder is remembered; a loss is repaired
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"shard_ice_crown"},!minecraft:custom_data~{gen:$(gen)}] run kill @s
$execute unless data storage last_ember:keys k.shard_ice_crown{gen:1} run clear @a[tag=le.khas] *[minecraft:custom_data~{le_key:"shard_ice_crown"},!minecraft:custom_data~{gen:$(gen)}]
execute if data storage last_ember:keys k.shard_ice_crown{st:2} run return 0
execute if data storage last_ember:keys k.shard_ice_crown{st:1} run return 0
$execute as @e[type=minecraft:item,tag=le.kitem,tag=!le.kthr] if items entity @s contents *[minecraft:custom_data~{le_key:"shard_ice_crown",gen:$(gen)}] run function last_ember:altar/gen/kf_shard_ice_crown
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"shard_ice_crown",gen:$(gen)}] run return run data modify storage last_ember:keys k.shard_ice_crown.it set value 1b
execute if data storage last_ember:keys k.shard_ice_crown{it:0b} if data storage last_ember:keys k.shard_ice_crown{got:1b} run return 0
execute if data storage last_ember:keys k.shard_ice_crown{it:0b} unless score #kphase le.alt matches 2 run return 0
function last_ember:altar/gen/kp_shard_ice_crown with storage last_ember:keys k.shard_ice_crown
execute if data storage last_ember:keys k.shard_ice_crown{it:1b} run function last_ember:altar/key_lost {id:"shard_ice_crown"}
