# generated: as the holder of the valid key shard_ice_crown: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_shard_ice_crown] run function last_ember:altar/gen/khn_shard_ice_crown
data modify storage last_ember:keys k.shard_ice_crown.it set value 0b
data modify storage last_ember:keys k.shard_ice_crown.got set value 1b
data modify storage last_ember:keys k.shard_ice_crown.pend set value 0b
