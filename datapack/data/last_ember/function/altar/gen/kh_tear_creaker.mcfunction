# generated: as the holder of the valid key tear_creaker: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_tear_creaker] run function last_ember:altar/gen/khn_tear_creaker
data modify storage last_ember:keys k.tear_creaker.it set value 0b
data modify storage last_ember:keys k.tear_creaker.got set value 1b
data modify storage last_ember:keys k.tear_creaker.pend set value 0b
