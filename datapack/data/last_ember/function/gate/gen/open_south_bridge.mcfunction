# generated: open the gate south_bridge (chapter 3 -> r4); a repeat does nothing
execute if score #gate_south_bridge le.gate matches 1 run return 0
scoreboard players set #gate_south_bridge le.gate 1
scoreboard players set #open_r4 le.gate 1
data modify storage last_ember:gates g.south_bridge set value {open:1b}
execute as @a at @s run playsound minecraft:entity.lightning_bolt.thunder weather @s ~ ~ ~ 0.8 0.6
title @a actionbar {"text": "На юге опустился мост.", "color": "gold"}
execute in minecraft:overworld positioned -3 126 633 as @a[distance=..64] run playsound minecraft:block.iron_door.open block @s ~ ~ ~ 2 0.5
execute in minecraft:overworld positioned -3 126 633 run particle minecraft:large_smoke ~ ~2 ~ 3 2 3 0.02 80 force
execute in minecraft:overworld positioned -3 126 633 run particle minecraft:flash{color:[1.0,0.9,0.7,1.0]} ~ ~2 ~ 0 0 0 0 1 force
function last_ember:gate/hook/south_bridge
