# generated: the shortcut r2 is open from inside the region: both sides, forever
execute if score #sc_r2 le.gate matches 1 run return 0
scoreboard players set #sc_r2 le.gate 1
data modify storage last_ember:gates s.r2 set value {open:1b}
