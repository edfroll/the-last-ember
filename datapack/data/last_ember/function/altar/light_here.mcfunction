# at the carrier: a light block of level 12 at the head, it follows him (under water too)
execute positioned ~ ~1.6 ~ align xyz positioned ~0.5 ~0.5 ~0.5 if entity @e[type=minecraft:marker,tag=le.emlight,distance=..0.1] if block ~ ~ ~ minecraft:light run return 0
function last_ember:altar/light_off
execute positioned ~ ~1.6 ~ align xyz positioned ~0.5 ~0.5 ~0.5 if block ~ ~ ~ minecraft:air run setblock ~ ~ ~ minecraft:light[level=12,waterlogged=false]
execute positioned ~ ~1.6 ~ align xyz positioned ~0.5 ~0.5 ~0.5 if block ~ ~ ~ minecraft:water run setblock ~ ~ ~ minecraft:light[level=12,waterlogged=true]
execute positioned ~ ~1.6 ~ align xyz positioned ~0.5 ~0.5 ~0.5 if block ~ ~ ~ minecraft:light run summon minecraft:marker ~ ~ ~ {Tags:["le.emlight"]}
