# generated: as the holder of the valid key heart_silence: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_heart_silence] run function last_ember:altar/gen/khn_heart_silence
data modify storage last_ember:keys k.heart_silence.it set value 0b
data modify storage last_ember:keys k.heart_silence.got set value 1b
data modify storage last_ember:keys k.heart_silence.pend set value 0b
