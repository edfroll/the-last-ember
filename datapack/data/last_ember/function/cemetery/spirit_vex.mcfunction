# T-027: an evil spirit here: a vex «Злой дух», 30 s of life (cemetery/spirit_sec), nothing dropped
summon minecraft:vex ~ ~1 ~ {PersistenceRequired:1b,DeathLootTable:"minecraft:empty",CustomName:{text:"Злой дух",color:"dark_aqua"},Tags:["le.cspirit","le.cvex","le.noelite","le.cnew"],drop_chances:{mainhand:0.0f,offhand:0.0f}}
scoreboard players set @e[tag=le.cnew] le.cst 0
particle minecraft:soul ~ ~1 ~ 0.4 0.6 0.4 0.04 25 force
tag @e[tag=le.cnew] remove le.cnew
