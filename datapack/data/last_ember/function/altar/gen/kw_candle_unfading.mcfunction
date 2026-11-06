# generated: macro gen (storage last_ember:keys k.candle_unfading): stale copies leave players and the floor; the holder is remembered; a loss is repaired
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"candle_unfading"},!minecraft:custom_data~{gen:$(gen)}] run kill @s
$execute unless data storage last_ember:keys k.candle_unfading{gen:1} run clear @a[tag=le.khas] *[minecraft:custom_data~{le_key:"candle_unfading"},!minecraft:custom_data~{gen:$(gen)}]
execute if data storage last_ember:keys k.candle_unfading{st:2} run return 0
execute if data storage last_ember:keys k.candle_unfading{st:1} run return 0
$execute as @e[type=minecraft:item,tag=le.kitem,tag=!le.kthr] if items entity @s contents *[minecraft:custom_data~{le_key:"candle_unfading",gen:$(gen)}] run function last_ember:altar/gen/kf_candle_unfading
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"candle_unfading",gen:$(gen)}] run return run data modify storage last_ember:keys k.candle_unfading.it set value 1b
execute if data storage last_ember:keys k.candle_unfading{it:0b} if data storage last_ember:keys k.candle_unfading{got:1b} run return 0
execute if data storage last_ember:keys k.candle_unfading{it:0b} unless score #kphase le.alt matches 0 run return 0
function last_ember:altar/gen/kp_candle_unfading with storage last_ember:keys k.candle_unfading
execute if data storage last_ember:keys k.candle_unfading{it:1b} run function last_ember:altar/key_lost {id:"candle_unfading"}
