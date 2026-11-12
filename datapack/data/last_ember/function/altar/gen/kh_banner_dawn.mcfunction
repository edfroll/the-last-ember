# generated: as the holder of the valid key banner_dawn: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_banner_dawn] run function last_ember:altar/gen/khn_banner_dawn
data modify storage last_ember:keys k.banner_dawn.it set value 0b
data modify storage last_ember:keys k.banner_dawn.got set value 1b
data modify storage last_ember:keys k.banner_dawn.pend set value 0b
