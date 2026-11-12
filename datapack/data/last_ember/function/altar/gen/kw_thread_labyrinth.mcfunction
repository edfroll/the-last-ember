# generated: macro gen (storage last_ember:keys k.thread_labyrinth): stale copies leave players and the floor; the holder is remembered; a loss is repaired
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"thread_labyrinth"},!minecraft:custom_data~{gen:$(gen)}] run kill @s
$execute unless data storage last_ember:keys k.thread_labyrinth{gen:1} run clear @a[tag=le.khas] *[minecraft:custom_data~{le_key:"thread_labyrinth"},!minecraft:custom_data~{gen:$(gen)}]
execute if data storage last_ember:keys k.thread_labyrinth{st:2} run return 0
execute if data storage last_ember:keys k.thread_labyrinth{st:1} run return 0
$execute as @e[type=minecraft:item,tag=le.kitem,tag=!le.kthr] if items entity @s contents *[minecraft:custom_data~{le_key:"thread_labyrinth",gen:$(gen)}] run function last_ember:altar/gen/kf_thread_labyrinth
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"thread_labyrinth",gen:$(gen)}] run return run data modify storage last_ember:keys k.thread_labyrinth.it set value 1b
execute if data storage last_ember:keys k.thread_labyrinth{it:0b} if data storage last_ember:keys k.thread_labyrinth{got:1b} run return 0
execute if data storage last_ember:keys k.thread_labyrinth{it:0b} unless score #kphase le.alt matches 3 run return 0
function last_ember:altar/gen/kp_thread_labyrinth with storage last_ember:keys k.thread_labyrinth
execute if data storage last_ember:keys k.thread_labyrinth{it:1b} run function last_ember:altar/key_lost {id:"thread_labyrinth"}
