# at the hearth interaction: lit by the carrier
function last_ember:bonfire/set_lit with storage last_ember:bt
playsound minecraft:item.firecharge.use block @a[distance=..32] ~ ~ ~ 1 0.7
playsound minecraft:block.fire.ambient block @a[distance=..32] ~ ~ ~ 1 1
particle minecraft:flame ~ ~0.6 ~ 0.3 0.3 0.3 0.04 80
particle minecraft:lava ~ ~0.6 ~ 0.2 0.2 0.2 0 12
particle minecraft:campfire_signal_smoke ~ ~1.5 ~ 0.15 1.5 0.15 0.01 30 force
execute as @a[distance=..16] run function last_ember:bonfire/bind
tellraw @a[distance=..16] {"text":"Костёр зажжён. Теперь вы возродитесь здесь.","color":"gold"}
