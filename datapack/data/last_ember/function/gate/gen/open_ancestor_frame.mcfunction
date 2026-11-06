# generated: open the gate ancestor_frame (chapter 5 -> r6); a repeat does nothing
execute if score #gate_ancestor_frame le.gate matches 1 run return 0
scoreboard players set #gate_ancestor_frame le.gate 1
scoreboard players set #open_r6 le.gate 1
data modify storage last_ember:gates g.ancestor_frame set value {open:1b}
execute as @a at @s run playsound minecraft:entity.lightning_bolt.thunder weather @s ~ ~ ~ 0.8 0.6
title @a actionbar {"text": "Рамка Предков ожила.", "color": "gold"}
function last_ember:gate/hook/ancestor_frame
