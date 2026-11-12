# generated: as the holder of the valid key hammer_ancestors: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_hammer_ancestors] run function last_ember:altar/gen/khn_hammer_ancestors
data modify storage last_ember:keys k.hammer_ancestors.it set value 0b
data modify storage last_ember:keys k.hammer_ancestors.got set value 1b
data modify storage last_ember:keys k.hammer_ancestors.pend set value 0b
