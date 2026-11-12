# generated: open the gate sealed_well (chapter 4 -> r5); a repeat does nothing
execute if score #gate_sealed_well le.gate matches 1 run return 0
scoreboard players set #gate_sealed_well le.gate 1
scoreboard players set #open_r5 le.gate 1
data modify storage last_ember:gates g.sealed_well set value {open:1b}
execute as @a at @s run playsound minecraft:entity.lightning_bolt.thunder weather @s ~ ~ ~ 0.8 0.6
title @a actionbar {"text": "Земля под Приютом дрогнула.", "color": "gold"}
execute in minecraft:overworld positioned 40 101 -44 as @a[distance=..64] run playsound minecraft:block.iron_door.open block @s ~ ~ ~ 2 0.5
execute in minecraft:overworld positioned 40 101 -44 run particle minecraft:large_smoke ~ ~2 ~ 3 2 3 0.02 80 force
execute in minecraft:overworld positioned 40 101 -44 run particle minecraft:flash{color:[1.0,0.9,0.7,1.0]} ~ ~2 ~ 0 0 0 0 1 force
function last_ember:gate/hook/sealed_well
