# generated: as the holder of the valid key anchor_drowned: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_anchor_drowned] run function last_ember:altar/gen/khn_anchor_drowned
data modify storage last_ember:keys k.anchor_drowned.it set value 0b
data modify storage last_ember:keys k.anchor_drowned.got set value 1b
data modify storage last_ember:keys k.anchor_drowned.pend set value 0b
