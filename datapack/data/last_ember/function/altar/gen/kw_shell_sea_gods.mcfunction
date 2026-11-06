# generated: macro gen (storage last_ember:keys k.shell_sea_gods): stale copies leave players and the floor; the holder is remembered; a loss is repaired
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"shell_sea_gods"},!minecraft:custom_data~{gen:$(gen)}] run kill @s
$execute unless data storage last_ember:keys k.shell_sea_gods{gen:1} run clear @a[tag=le.khas] *[minecraft:custom_data~{le_key:"shell_sea_gods"},!minecraft:custom_data~{gen:$(gen)}]
execute if data storage last_ember:keys k.shell_sea_gods{st:2} run return 0
execute if data storage last_ember:keys k.shell_sea_gods{st:1} run return 0
$execute as @e[type=minecraft:item,tag=le.kitem,tag=!le.kthr] if items entity @s contents *[minecraft:custom_data~{le_key:"shell_sea_gods",gen:$(gen)}] run function last_ember:altar/gen/kf_shell_sea_gods
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"shell_sea_gods",gen:$(gen)}] run return run data modify storage last_ember:keys k.shell_sea_gods.it set value 1b
execute if data storage last_ember:keys k.shell_sea_gods{it:0b} if data storage last_ember:keys k.shell_sea_gods{got:1b} run return 0
execute if data storage last_ember:keys k.shell_sea_gods{it:0b} unless score #kphase le.alt matches 1 run return 0
function last_ember:altar/gen/kp_shell_sea_gods with storage last_ember:keys k.shell_sea_gods
execute if data storage last_ember:keys k.shell_sea_gods{it:1b} run function last_ember:altar/key_lost {id:"shell_sea_gods"}
