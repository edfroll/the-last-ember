# at the centre of the circle: every candle of the circle goes out at once (the Weepers' candles stand on the plinths at y 112)
fill ~-18 ~ ~-18 ~18 ~1 ~18 minecraft:candle[candles=1,lit=false] replace minecraft:candle[candles=1,lit=true]
fill ~-18 ~ ~-18 ~18 ~1 ~18 minecraft:candle[candles=2,lit=false] replace minecraft:candle[candles=2,lit=true]
fill ~-18 ~ ~-18 ~18 ~1 ~18 minecraft:candle[candles=3,lit=false] replace minecraft:candle[candles=3,lit=true]
fill ~-18 ~ ~-18 ~18 ~1 ~18 minecraft:candle[candles=4,lit=false] replace minecraft:candle[candles=4,lit=true]
particle minecraft:smoke ~ ~0.5 ~ 12 0.2 12 0.01 120
playsound minecraft:block.candle.extinguish block @a[distance=..32] ~ ~ ~ 1.5 0.7
playsound minecraft:block.candle.extinguish block @a[distance=..32] ~ ~ ~ 1.5 0.5
