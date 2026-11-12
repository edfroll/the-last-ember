# generated: as the holder of the valid key shell_sea_gods: remembered as the last one who held it
scoreboard players set #kh le.alt 1
execute unless entity @s[tag=le.kh_shell_sea_gods] run function last_ember:altar/gen/khn_shell_sea_gods
data modify storage last_ember:keys k.shell_sea_gods.it set value 0b
data modify storage last_ember:keys k.shell_sea_gods.got set value 1b
data modify storage last_ember:keys k.shell_sea_gods.pend set value 0b
