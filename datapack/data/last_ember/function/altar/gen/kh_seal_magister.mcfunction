# generated: as the holder of the valid key seal_magister: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_seal_magister] run function last_ember:altar/gen/khn_seal_magister
data modify storage last_ember:keys k.seal_magister.it set value 0b
data modify storage last_ember:keys k.seal_magister.got set value 1b
data modify storage last_ember:keys k.seal_magister.pend set value 0b
