# generated: macro gen (storage last_ember:keys k.heart_silence): stale copies leave players and the floor; the holder is remembered; a loss is repaired
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"heart_silence"},!minecraft:custom_data~{gen:$(gen)}] run kill @s
$execute unless data storage last_ember:keys k.heart_silence{gen:1} run clear @a[tag=le.khas] *[minecraft:custom_data~{le_key:"heart_silence"},!minecraft:custom_data~{gen:$(gen)}]
execute if data storage last_ember:keys k.heart_silence{st:2} run return 0
execute if data storage last_ember:keys k.heart_silence{st:1} run return 0
$execute as @e[type=minecraft:item,tag=le.kitem,tag=!le.kthr] if items entity @s contents *[minecraft:custom_data~{le_key:"heart_silence",gen:$(gen)}] run function last_ember:altar/gen/kf_heart_silence
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"heart_silence",gen:$(gen)}] run return run data modify storage last_ember:keys k.heart_silence.it set value 1b
execute if data storage last_ember:keys k.heart_silence{it:0b} if data storage last_ember:keys k.heart_silence{got:1b} run return 0
execute if data storage last_ember:keys k.heart_silence{it:0b} unless score #kphase le.alt matches 1 run return 0
function last_ember:altar/gen/kp_heart_silence with storage last_ember:keys k.heart_silence
execute if data storage last_ember:keys k.heart_silence{it:1b} run function last_ember:altar/key_lost {id:"heart_silence"}
