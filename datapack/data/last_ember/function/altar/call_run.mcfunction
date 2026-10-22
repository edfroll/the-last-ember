# as the carrier: sparks go 12 blocks towards the nearest key point of the current chapter that nobody has found yet (else towards its altar)
scoreboard players operation #cur le.alt = #chapters le.alt
scoreboard players add #cur le.alt 1
function last_ember:altar/gen/call_target
execute if score #found le.alt matches 0 run return run title @s actionbar {"text":"Уголь молчит","color":"gray"}
execute store result storage last_ember:altar call.x int 1 run scoreboard players get #tx le.alt
execute store result storage last_ember:altar call.z int 1 run scoreboard players get #tz le.alt
function last_ember:altar/call_m with storage last_ember:altar call
playsound minecraft:block.fire.ambient player @s ~ ~ ~ 1 1.5
