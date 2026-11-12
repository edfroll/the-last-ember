# generated: as the holder of the valid key crown_mountain_king: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_crown_mountain_king] run function last_ember:altar/gen/khn_crown_mountain_king
data modify storage last_ember:keys k.crown_mountain_king.it set value 0b
data modify storage last_ember:keys k.crown_mountain_king.got set value 1b
data modify storage last_ember:keys k.crown_mountain_king.pend set value 0b
