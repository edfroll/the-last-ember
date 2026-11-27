# put the main item #k le.vt into a treasury of r1
execute if function last_ember:vault/gen/ch_1 run return 1
execute if function last_ember:vault/gen/ch_2 run return 1
tellraw @a[tag=le.vdbg] {"text":"VAULT WARNING: no place for a main item","color":"red"}
return 0
