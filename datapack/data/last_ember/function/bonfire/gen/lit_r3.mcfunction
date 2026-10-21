# generated: lit state of a bonfire with circle radius 3 (at the hearth)
execute if block ~ ~-1 ~ minecraft:hay_block run setblock ~ ~ ~ minecraft:campfire[lit=true,signal_fire=true]
execute unless block ~ ~-1 ~ minecraft:hay_block run setblock ~ ~ ~ minecraft:campfire[lit=true,signal_fire=false]
setblock ~ ~1 ~-3 minecraft:shroomlight
setblock ~-3 ~ ~-3 minecraft:candle[candles=3,lit=true]
setblock ~3 ~ ~-3 minecraft:candle[candles=3,lit=true]
setblock ~-3 ~ ~3 minecraft:candle[candles=3,lit=true]
setblock ~3 ~ ~3 minecraft:candle[candles=3,lit=true]
