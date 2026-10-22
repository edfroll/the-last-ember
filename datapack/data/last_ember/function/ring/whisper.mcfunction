# sounds and shadows only for the wearer
playsound minecraft:ambient.cave ambient @s ~ ~ ~ 0.6 0.5
execute positioned ^ ^ ^-2 run playsound minecraft:block.gravel.step ambient @s ~ ~ ~ 0.9 0.7
execute if predicate last_ember:chance_30 positioned ^1.6 ^1 ^0.8 run particle minecraft:squid_ink ~ ~ ~ 0.1 0.4 0.1 0.01 4 normal @s
