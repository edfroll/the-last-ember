# generated: the shortcut r1 is open from inside the region: both sides, forever
execute if score #sc_r1 le.gate matches 1 run return 0
scoreboard players set #sc_r1 le.gate 1
data modify storage last_ember:gates s.r1 set value {open:1b}
