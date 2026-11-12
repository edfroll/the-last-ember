# generated: open the gate ash_summit (chapter 6 -> final); a repeat does nothing
execute if score #gate_ash_summit le.gate matches 1 run return 0
scoreboard players set #gate_ash_summit le.gate 1
scoreboard players set #open_final le.gate 1
data modify storage last_ember:gates g.ash_summit set value {open:1b}
execute as @a at @s run playsound minecraft:entity.lightning_bolt.thunder weather @s ~ ~ ~ 0.8 0.6
title @a actionbar {"text": "Вершина Пепельной горы ждёт.", "color": "gold"}
function last_ember:gate/hook/ash_summit
