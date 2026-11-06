# generated: macro gen (storage last_ember:keys k.stone_black_water): stale copies leave players and the floor; the holder is remembered; a loss is repaired
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"stone_black_water"},!minecraft:custom_data~{gen:$(gen)}] run kill @s
$execute unless data storage last_ember:keys k.stone_black_water{gen:1} run clear @a[tag=le.khas] *[minecraft:custom_data~{le_key:"stone_black_water"},!minecraft:custom_data~{gen:$(gen)}]
execute if data storage last_ember:keys k.stone_black_water{st:2} run return 0
execute if data storage last_ember:keys k.stone_black_water{st:1} run return 0
$execute as @e[type=minecraft:item,tag=le.kitem,tag=!le.kthr] if items entity @s contents *[minecraft:custom_data~{le_key:"stone_black_water",gen:$(gen)}] run function last_ember:altar/gen/kf_stone_black_water
$execute as @e[type=minecraft:item,tag=le.kitem] if items entity @s contents *[minecraft:custom_data~{le_key:"stone_black_water",gen:$(gen)}] run return run data modify storage last_ember:keys k.stone_black_water.it set value 1b
execute if data storage last_ember:keys k.stone_black_water{it:0b} if data storage last_ember:keys k.stone_black_water{got:1b} run return 0
execute if data storage last_ember:keys k.stone_black_water{it:0b} unless score #kphase le.alt matches 2 run return 0
function last_ember:altar/gen/kp_stone_black_water with storage last_ember:keys k.stone_black_water
execute if data storage last_ember:keys k.stone_black_water{it:1b} run function last_ember:altar/key_lost {id:"stone_black_water"}
