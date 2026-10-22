# macro id gen st it: stale copies leave players and the floor; a loss is repaired
$clear @a *[minecraft:custom_data~{le_key:"$(id)"},!minecraft:custom_data~{gen:$(gen)}]
$execute as @e[type=minecraft:item] if items entity @s contents *[minecraft:custom_data~{le_key:"$(id)"},!minecraft:custom_data~{gen:$(gen)}] run kill @s
$execute if data storage last_ember:keys k.$(id){st:2} run return 0
$execute if data storage last_ember:keys k.$(id){st:1} run return 0
scoreboard players set #kh le.alt 0
$execute as @a run function last_ember:altar/holds_key {id:"$(id)",gen:$(gen)}
execute if score #kh le.alt matches 1 run return 0
$execute if entity @e[type=minecraft:item,nbt={Item:{components:{"minecraft:custom_data":{le_key:"$(id)",gen:$(gen)}}}}] run return run data modify storage last_ember:keys k.$(id).it set value 1b
$execute if data storage last_ember:keys k.$(id){it:1b} run function last_ember:altar/key_lost {id:"$(id)"}
