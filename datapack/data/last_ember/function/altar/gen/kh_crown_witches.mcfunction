# generated: as the holder of the valid key crown_witches: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_crown_witches] run function last_ember:altar/gen/khn_crown_witches
data modify storage last_ember:keys k.crown_witches.it set value 0b
data modify storage last_ember:keys k.crown_witches.got set value 1b
data modify storage last_ember:keys k.crown_witches.pend set value 0b
