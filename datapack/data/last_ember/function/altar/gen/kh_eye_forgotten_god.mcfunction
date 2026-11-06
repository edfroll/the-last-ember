# generated: as the holder of the valid key eye_forgotten_god: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_eye_forgotten_god] run function last_ember:altar/gen/khn_eye_forgotten_god
data modify storage last_ember:keys k.eye_forgotten_god.it set value 0b
data modify storage last_ember:keys k.eye_forgotten_god.got set value 1b
data modify storage last_ember:keys k.eye_forgotten_god.pend set value 0b
