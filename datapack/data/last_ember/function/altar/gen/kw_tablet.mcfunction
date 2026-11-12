# generated: macro gen (storage last_ember:keys k.tablet): stale copies leave players and the floor; the holder is remembered; a loss is repaired
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"tablet"},!minecraft:custom_data~{gen:$(gen)}] run kill @s
$execute unless data storage last_ember:keys k.tablet{gen:1} run clear @a[tag=le.khas] *[minecraft:custom_data~{le_key:"tablet"},!minecraft:custom_data~{gen:$(gen)}]
execute if data storage last_ember:keys k.tablet{st:2} run return 0
execute if data storage last_ember:keys k.tablet{st:1} run return 0
$execute as @e[type=minecraft:item,tag=le.kitem,tag=!le.kthr] if items entity @s contents *[minecraft:custom_data~{le_key:"tablet",gen:$(gen)}] run function last_ember:altar/gen/kf_tablet
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"tablet",gen:$(gen)}] run return run data modify storage last_ember:keys k.tablet.it set value 1b
execute if data storage last_ember:keys k.tablet{it:0b} if data storage last_ember:keys k.tablet{got:1b} run return 0
execute if data storage last_ember:keys k.tablet{it:0b} unless score #kphase le.alt matches 3 run return 0
function last_ember:altar/gen/kp_tablet with storage last_ember:keys k.tablet
execute if data storage last_ember:keys k.tablet{it:1b} run function last_ember:altar/key_lost {id:"tablet"}
