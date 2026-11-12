# generated: as the holder of the valid key stone_black_water: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_stone_black_water] run function last_ember:altar/gen/khn_stone_black_water
data modify storage last_ember:keys k.stone_black_water.it set value 0b
data modify storage last_ember:keys k.stone_black_water.got set value 1b
data modify storage last_ember:keys k.stone_black_water.pend set value 0b
