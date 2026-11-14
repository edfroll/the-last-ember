# T-023: one tick of the event of Altar I (called by altar/gen/ev_weepers at the centre of the circle; #ev le.alt = the tick, 1..260):
#   1..200 the Weepers weep (drops and calcite dust from the niches at the eyes), a hum, crying; 200 the candles go out at once;
#   236..240 the sky gathers over the crown; 240 the strike into the top of the tree (particles and sound, no vanilla lightning: no fire),
#   seen and heard within 64; at once the Weepers lower their hands, the core burns from inside, the candles are lit again (templates).
scoreboard players operation #wm le.alt = #ev le.alt
scoreboard players operation #wm le.alt %= #2 le.alt
execute if score #ev le.alt matches 1..200 if score #wm le.alt matches 0 run function last_ember:weepers/gen/tears
execute if score #ev le.alt matches 1 run playsound minecraft:block.beacon.ambient ambient @a[distance=..48] ~ ~ ~ 1.5 0.5
execute if score #ev le.alt matches 1 run playsound minecraft:ambient.soul_sand_valley.mood ambient @a[distance=..48] ~ ~ ~ 2 0.6
execute if score #ev le.alt matches 10 run playsound last_ember:sfx.mind.cry ambient @a[distance=..40] ~ ~2 ~ 0.9 0.9
execute if score #ev le.alt matches 70 run playsound last_ember:sfx.mind.cry ambient @a[distance=..40] ~ ~2 ~ 1.0 0.8
execute if score #ev le.alt matches 130 run playsound last_ember:sfx.mind.cry ambient @a[distance=..40] ~ ~2 ~ 1.1 0.7
execute if score #ev le.alt matches 60 run playsound minecraft:block.beacon.ambient ambient @a[distance=..48] ~ ~ ~ 1.8 0.45
execute if score #ev le.alt matches 120 run playsound minecraft:block.beacon.ambient ambient @a[distance=..48] ~ ~ ~ 2 0.4
execute if score #ev le.alt matches 200 run function last_ember:weepers/candles_out
execute if score #ev le.alt matches 236..239 positioned ~ ~28 ~ run particle minecraft:large_smoke ~ ~6 ~ 3 1 3 0.01 30 force @a[distance=..96]
execute if score #ev le.alt matches 240 run function last_ember:weepers/strike
