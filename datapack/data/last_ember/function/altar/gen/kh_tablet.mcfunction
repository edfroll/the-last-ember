# generated: as the holder of the valid key tablet: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_tablet] run function last_ember:altar/gen/khn_tablet
data modify storage last_ember:keys k.tablet.it set value 0b
data modify storage last_ember:keys k.tablet.got set value 1b
data modify storage last_ember:keys k.tablet.pend set value 0b
