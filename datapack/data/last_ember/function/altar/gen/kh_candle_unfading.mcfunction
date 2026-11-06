# generated: as the holder of the valid key candle_unfading: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_candle_unfading] run function last_ember:altar/gen/khn_candle_unfading
data modify storage last_ember:keys k.candle_unfading.it set value 0b
data modify storage last_ember:keys k.candle_unfading.got set value 1b
data modify storage last_ember:keys k.candle_unfading.pend set value 0b
