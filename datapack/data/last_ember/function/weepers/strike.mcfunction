# at the centre of the circle: the strike into the top of the tree (no vanilla lightning), the swap of the templates (the end of the grief)
execute positioned ~ ~28 ~ run particle minecraft:electric_spark ~ ~16 ~ 0.15 16 0.15 0.4 400 force @a[distance=..64]
execute positioned ~ ~28 ~ run particle minecraft:flash{color:[0.85,0.9,1.0,1.0]} ~ ~1 ~ 0 0 0 0 1 force @a[distance=..64]
execute positioned ~ ~28 ~ run particle minecraft:explosion ~ ~ ~ 1 1 1 0 6 force @a[distance=..64]
execute positioned ~ ~28 ~ run particle minecraft:large_smoke ~ ~ ~ 0.8 0.8 0.8 0.05 40 force @a[distance=..64]
execute positioned ~ ~28 ~ run particle minecraft:lava ~ ~ ~ 0.5 0.5 0.5 0 20 force @a[distance=..64]
playsound minecraft:entity.lightning_bolt.thunder weather @a[distance=..64] ~ ~28 ~ 5 0.9
playsound minecraft:entity.lightning_bolt.impact weather @a[distance=..64] ~ ~28 ~ 3 0.8
function last_ember:weepers/gen/statues_down
function last_ember:weepers/gen/core_after
particle minecraft:end_rod ~ ~6 ~ 1.5 4 1.5 0.05 120 force @a[distance=..64]
particle minecraft:flame ~ ~6 ~ 1.2 3 1.2 0.02 60 force @a[distance=..64]
playsound minecraft:block.beacon.power_select block @a[distance=..48] ~ ~ ~ 2 0.6
