# macro mob, mob2 (T-026: every second mob is mob2; the same as mob when not given), at the chest: one mob of the ring round it; #cnt le.tr counts down
scoreboard players operation #m le.tr = #cnt le.tr
scoreboard players operation #m le.tr %= #8 le.tr
scoreboard players operation #odd le.tr = #cnt le.tr
scoreboard players operation #odd le.tr %= #2 le.tr
$execute if score #odd le.tr matches 0 if score #m le.tr matches 0 positioned ~2 ~ ~0 run summon $(mob) ~ ~ ~ {Tags:["le.noelite"]}
$execute if score #odd le.tr matches 1 if score #m le.tr matches 0 positioned ~2 ~ ~0 run summon $(mob2) ~ ~ ~ {Tags:["le.noelite"]}
$execute if score #odd le.tr matches 0 if score #m le.tr matches 1 positioned ~1 ~ ~2 run summon $(mob) ~ ~ ~ {Tags:["le.noelite"]}
$execute if score #odd le.tr matches 1 if score #m le.tr matches 1 positioned ~1 ~ ~2 run summon $(mob2) ~ ~ ~ {Tags:["le.noelite"]}
$execute if score #odd le.tr matches 0 if score #m le.tr matches 2 positioned ~0 ~ ~2 run summon $(mob) ~ ~ ~ {Tags:["le.noelite"]}
$execute if score #odd le.tr matches 1 if score #m le.tr matches 2 positioned ~0 ~ ~2 run summon $(mob2) ~ ~ ~ {Tags:["le.noelite"]}
$execute if score #odd le.tr matches 0 if score #m le.tr matches 3 positioned ~-1 ~ ~2 run summon $(mob) ~ ~ ~ {Tags:["le.noelite"]}
$execute if score #odd le.tr matches 1 if score #m le.tr matches 3 positioned ~-1 ~ ~2 run summon $(mob2) ~ ~ ~ {Tags:["le.noelite"]}
$execute if score #odd le.tr matches 0 if score #m le.tr matches 4 positioned ~-2 ~ ~0 run summon $(mob) ~ ~ ~ {Tags:["le.noelite"]}
$execute if score #odd le.tr matches 1 if score #m le.tr matches 4 positioned ~-2 ~ ~0 run summon $(mob2) ~ ~ ~ {Tags:["le.noelite"]}
$execute if score #odd le.tr matches 0 if score #m le.tr matches 5 positioned ~-1 ~ ~-2 run summon $(mob) ~ ~ ~ {Tags:["le.noelite"]}
$execute if score #odd le.tr matches 1 if score #m le.tr matches 5 positioned ~-1 ~ ~-2 run summon $(mob2) ~ ~ ~ {Tags:["le.noelite"]}
$execute if score #odd le.tr matches 0 if score #m le.tr matches 6 positioned ~0 ~ ~-2 run summon $(mob) ~ ~ ~ {Tags:["le.noelite"]}
$execute if score #odd le.tr matches 1 if score #m le.tr matches 6 positioned ~0 ~ ~-2 run summon $(mob2) ~ ~ ~ {Tags:["le.noelite"]}
$execute if score #odd le.tr matches 0 if score #m le.tr matches 7 positioned ~1 ~ ~-2 run summon $(mob) ~ ~ ~ {Tags:["le.noelite"]}
$execute if score #odd le.tr matches 1 if score #m le.tr matches 7 positioned ~1 ~ ~-2 run summon $(mob2) ~ ~ ~ {Tags:["le.noelite"]}
scoreboard players remove #cnt le.tr 1
$execute if score #cnt le.tr matches 1.. run function last_ember:trap/spawn_ring {mob:"$(mob)",mob2:"$(mob2)"}
