# generated: open the gate watch_gates (chapter 2 -> r3); a repeat does nothing
execute if score #gate_watch_gates le.gate matches 1 run return 0
scoreboard players set #gate_watch_gates le.gate 1
scoreboard players set #open_r3 le.gate 1
data modify storage last_ember:gates g.watch_gates set value {open:1b}
execute as @a at @s run playsound minecraft:entity.lightning_bolt.thunder weather @s ~ ~ ~ 0.8 0.6
title @a actionbar {"text": "Далеко на севере открылись ворота.", "color": "gold"}
execute in minecraft:overworld positioned -880 0 -640 positioned over world_surface as @a[distance=..64] run playsound minecraft:block.iron_door.open block @s ~ ~ ~ 2 0.5
execute in minecraft:overworld positioned -880 0 -640 positioned over world_surface run particle minecraft:large_smoke ~ ~2 ~ 3 2 3 0.02 80 force
function last_ember:gate/hook/watch_gates
