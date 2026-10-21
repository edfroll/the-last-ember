# generated: lit state of a bonfire with circle radius 4 (at the hearth)
execute if block ~ ~-1 ~ minecraft:hay_block run setblock ~ ~ ~ minecraft:campfire[lit=true,signal_fire=true]
execute unless block ~ ~-1 ~ minecraft:hay_block run setblock ~ ~ ~ minecraft:campfire[lit=true,signal_fire=false]
setblock ~ ~1 ~-4 minecraft:shroomlight
setblock ~-4 ~ ~-4 minecraft:candle[candles=3,lit=true]
setblock ~4 ~ ~-4 minecraft:candle[candles=3,lit=true]
setblock ~-4 ~ ~4 minecraft:candle[candles=3,lit=true]
setblock ~4 ~ ~4 minecraft:candle[candles=3,lit=true]
