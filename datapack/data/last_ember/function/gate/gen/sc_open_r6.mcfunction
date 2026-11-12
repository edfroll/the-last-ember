# generated: the shortcut r6 is open from inside the region: both sides, forever
execute if score #sc_r6 le.gate matches 1 run return 0
scoreboard players set #sc_r6 le.gate 1
data modify storage last_ember:gates s.r6 set value {open:1b}
