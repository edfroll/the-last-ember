# generated: as the holder of the valid key tear_titan: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_tear_titan] run function last_ember:altar/gen/khn_tear_titan
data modify storage last_ember:keys k.tear_titan.it set value 0b
data modify storage last_ember:keys k.tear_titan.got set value 1b
data modify storage last_ember:keys k.tear_titan.pend set value 0b
