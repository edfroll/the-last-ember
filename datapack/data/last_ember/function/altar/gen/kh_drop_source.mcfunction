# generated: as the holder of the valid key drop_source: remembered as the last one who held it
scoreboard players set #kh le.alt 1
data modify storage last_ember:keys k.drop_source.h set from entity @s UUID
data modify storage last_ember:keys k.drop_source.it set value 0b
data modify storage last_ember:keys k.drop_source.got set value 1b
data modify storage last_ember:keys k.drop_source.pend set value 0b
