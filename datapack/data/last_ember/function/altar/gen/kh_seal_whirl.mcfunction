# generated: as the holder of the valid key seal_whirl: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_seal_whirl] run function last_ember:altar/gen/khn_seal_whirl
data modify storage last_ember:keys k.seal_whirl.it set value 0b
data modify storage last_ember:keys k.seal_whirl.got set value 1b
data modify storage last_ember:keys k.seal_whirl.pend set value 0b
