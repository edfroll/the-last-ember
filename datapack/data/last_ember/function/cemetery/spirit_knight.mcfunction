# T-027: a knight spirit here: a skeleton invisible (no particles of the effect), pale blue leather, a stone sword, nothing dropped
summon minecraft:skeleton ~ ~ ~ {PersistenceRequired:1b,DeathLootTable:"minecraft:empty",Tags:["le.cspirit","le.cknight","le.noelite","le.cnew"],equipment:{head:{id:"minecraft:leather_helmet",count:1,components:{"minecraft:dyed_color":11393254}},chest:{id:"minecraft:leather_chestplate",count:1,components:{"minecraft:dyed_color":11393254}},legs:{id:"minecraft:leather_leggings",count:1,components:{"minecraft:dyed_color":11393254}},feet:{id:"minecraft:leather_boots",count:1,components:{"minecraft:dyed_color":11393254}},mainhand:{id:"minecraft:stone_sword",count:1}},drop_chances:{head:0.0f,chest:0.0f,legs:0.0f,feet:0.0f,mainhand:0.0f},active_effects:[{id:"minecraft:invisibility",amplifier:0b,duration:-1,show_particles:0b,show_icon:0b}]}
scoreboard players set @e[tag=le.cnew] le.cst 0
particle minecraft:soul ~ ~0.8 ~ 0.4 0.8 0.4 0.03 25 force
particle minecraft:soul_fire_flame ~ ~0.2 ~ 0.3 0.1 0.3 0.02 10 force
tag @e[tag=le.cnew] remove le.cnew
