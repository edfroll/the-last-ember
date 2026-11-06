# generated: TEST ONLY: close the gate sealed_well again
scoreboard players set #gate_sealed_well le.gate 0
data modify storage last_ember:gates g.sealed_well set value {open:0b}
scoreboard players set #open_r5 le.gate 0
